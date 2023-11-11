import time
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.accounts.models import User


# Create your models here.
def get_assets_pathname(self, filename):
    return f'{self.owner.uid}/assets/{filename}'


def get_assets_thumbnail_pathname(self, filename):
    extension = str(filename).split('.')[-1]
    current_time = time.time()
    file = "".join(str(current_time).split('.'))
    return f'{self.owner.uid}/thumbnails/{file}.{extension}'


class Image(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    source = models.ImageField(upload_to=get_assets_pathname)
    type = models.CharField(max_length=10, default='*/*')
    width = models.PositiveIntegerField(default=1)
    height = models.PositiveIntegerField(default=1)


class Video(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    source = models.FileField(upload_to=get_assets_pathname)
    thumbnail = models.ImageField(upload_to=get_assets_thumbnail_pathname, blank=True)
    type = models.CharField(max_length=10, default='*/*')
    width = models.PositiveIntegerField(default=1)
    height = models.PositiveIntegerField(default=1)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]


class Media(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medias')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={
        'model__in': ('image', 'video')
    })
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    description = models.TextField(null=True, blank=True)
    mime_type = models.CharField(max_length=10, default='image')

    users_like = models.ManyToManyField(User, related_name='likes', blank=True)
    total_likes = models.PositiveIntegerField(default=0)

    comments = models.ManyToManyField(Comment, blank=True)
    total_comments = models.PositiveIntegerField(default=0)

    viewed_by = models.ManyToManyField(User, related_name='histories', through='History')
    total_views = models.PositiveIntegerField(default=0)

    users_bookmarks = models.ManyToManyField(User, related_name='bookmarks', blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['-total_likes']),
            models.Index(fields=['-total_comments'])
        ]

    def get_ratio(self):
        return self.item.width / self.item.height


def get_story_thumbnails_pathname(self, filename):
    extension = str(filename).split('.')[-1]
    current_time = time.time()
    file = "".join(str(current_time).split('.'))
    return f'{self.user.uid}/stories/thumbnails/{file}.{extension}'


def get_story_videos_pathname(self, filename):
    extension = str(filename).split('.')[-1]
    current_time = time.time()
    file = "".join(str(current_time).split('.'))
    return f'{self.user.uid}/stories/{file}.{extension}'


class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    thumbnail = models.ImageField(upload_to=get_story_thumbnails_pathname, null=True, blank=True)
    video = models.FileField(upload_to=get_story_videos_pathname, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    is_expired = models.BooleanField(default=False)

    viewed_by = models.ManyToManyField(User, symmetrical=False)

    class Meta:
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Media, on_delete=models.CASCADE)
    last_date_viewed = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_date_viewed']
        indexes = [
            models.Index(fields=['-last_date_viewed'])
        ]
