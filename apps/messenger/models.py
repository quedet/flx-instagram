from django.db import models
from apps.accounts.models import User
import string, secrets


# Create your models here.
class Client(models.Model):
    """
    Clients for users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.CharField(max_length=200, blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Room(models.Model):
    users_subscribed = models.ManyToManyField(User, related_name='users_subscribed')
    clients_active = models.ManyToManyField(Client, related_name='clients_active')
    uid = models.CharField(max_length=20)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.uid:
            population = string.ascii_letters + string.digits
            secret_key = ''.join(secrets.choice(population) for i in range(19))
            self.uid = secret_key
        return super().save(force_insert,force_update, using, update_fields)

    def __str__(self):
        return self.uid


class Message(models.Model):
    """
    Messages for users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['created_at'])]
