from django.db import models
from django.conf import settings
from apps.accounts.models import User


# Create your models here.
class WatchLog(models.Model):
    """Stream Watch Log"""
    video_path = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name='watch_logs', on_delete=models.SET_NULL, null=True, blank=True)
    is_authenticated = models.BooleanField(default=False)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Watch Log ip: {self.ip}, created at {self.created}"

    class Meta:
        verbose_name = 'Watch Log'
        verbose_name_plural = 'Watch Logs'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]
