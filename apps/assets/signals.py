from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed, post_delete
from guardian.shortcuts import assign_perm
from moviepy.editor import VideoFileClip, ImageClip
from PIL import Image as PILImage
from io import BytesIO
from django.core.files.base import ContentFile
from .models import Media, Image, Video, Story
import time, os, cv2, glob, re
from django.conf import settings


@receiver(post_save, sender=Image)
def image_post_save(sender, instance, created, **kwargs):
    if created and instance.owner is not None:
        permissions = [
            'assets.view_image',
            'assets.change_image',
            'assets.delete_image',
            'assets.add_image'
        ]

        for perm in permissions:
            assign_perm(perm, instance.owner, instance)


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.owner is not None:
        permissions = [
            'assets.view_video',
            'assets.change_video',
            'assets.delete_video',
            'assets.add_video'
        ]

        for perm in permissions:
            assign_perm(perm, instance.owner, instance)


@receiver(post_save, sender=Media)
def media_post_save(sender, instance, created, **kwargs):
    if created and instance.owner is not None:
        permissions = [
            'assets.view_media',
            'assets.change_media',
            'assets.delete_media',
            'assets.add_media'
        ]

        for perm in permissions:
            assign_perm(perm, instance.owner, instance)


@receiver(m2m_changed, sender=Media.users_like.through)
def media_users_like_changed(sender, instance, **kwargs):
    instance.total_likes = instance.users_like.count()
    instance.save()


@receiver(m2m_changed, sender=Media.comments.through)
def media_comments_changed(sender, instance, **kwargs):
    instance.total_comments = instance.comments.count()
    instance.save()


@receiver(post_save, sender=Story)
def user_story_post_save(sender, instance, created, **kwargs):
    if created and instance.user is not None:
        permissions = [
            'assets.view_story',
            'assets.change_story',
            'assets.delete_story',
            'assets.add_story',
        ]

        if instance.video and not instance.thumbnail:
            video = VideoFileClip(instance.video.path)
            frame = video.get_frame(1)
            img = PILImage.fromarray(frame, 'RGB')

            thumb_temp = BytesIO()
            img.save(thumb_temp, "JPEG")

            thumb_temp.seek(0)
            instance.thumbnail.save(f"{instance.video.name}.jpeg", ContentFile(thumb_temp.read()), save=True)
            thumb_temp.close()


@receiver(post_delete, sender=Story)
def user_story_post_delete(sender, instance, **kwargs):
    if instance.video:
        # os.remove(instance.video.path)  and os.path.isfile(instance.video.path)
        instance.video.delete()

    if instance.thumbnail:
        instance.thumbnail.delete()
