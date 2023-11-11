from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import string, random
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.text import slugify

# Create your models here.


class Gender(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    NOT_TO_SAY = "NOT_TO_SAY", "Prefer not to say"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create(self, email, password, **extra_fields):
        if not email:
            raise ValueError('User must have an identifier (e.g username or email address)')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create(email, password, **extra_fields)


class Interest(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True, null=True)

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.slug = slugify(self.name)

        if update_fields is not None and "name" in update_fields:
            update_fields = {"slug"}.union(update_fields)

        return super().save(force_insert, force_update, using, update_fields)


class User(AbstractUser):
    uid = models.CharField(blank=True, unique=True)
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(max_length=150, unique=True, blank=True,
                                help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                                validators=[username_validator],
                                error_messages={
                                    "unique": "A user with that username already exists.",
                                })
    email = models.EmailField('Email address', unique=True, error_messages={
        "unique": "A user with that email already exists"
    })

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    followings = models.ManyToManyField('self', related_name='followers', symmetrical=False, through='Contact')
    interests = models.ManyToManyField(Interest)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.uid:
            population = string.ascii_letters + string.digits
            sample = random.sample(population, 12)
            self.uid = "".join(sample)
        return super().save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, max_length=150)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.NOT_TO_SAY)
    enable_suggestions = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user}'s profile"


def get_original_pathname(self, filename):
    extension = str(filename).split('.')[-1]
    return f'{self.profile.user.uid}/profile/temp/{self.profile.user.uid}.{extension}'


def get_cropped_pathname(self, filename):
    extension = str(filename).split('.')[-1]
    return f'{self.profile.user.uid}/profile/{self.profile.user.uid}.{extension}'


class Photo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='photo')
    original = models.ImageField(upload_to=get_original_pathname, default='portrait.png')
    cropped = models.ImageField(upload_to=get_cropped_pathname, default='portrait.png')
    cropX = models.IntegerField(null=True, blank=True)
    cropY = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    type = models.CharField(default='image/png')


class Contact(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rel_from_set')
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rel_to_set')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created'])
        ]
        ordering = ['-created']

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'


class SearchHistory(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE, related_name='search_history')
    requested_users = models.ManyToManyField(User, symmetrical=False)
