from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import Image, Video, Media, Comment, Story


# Register your models here.
@admin.register(Image)
class ImageAdmin(GuardedModelAdmin):
    pass


@admin.register(Video)
class VideoAdmin(GuardedModelAdmin):
    pass


@admin.register(Media)
class MediaAdmin(GuardedModelAdmin):
    pass


@admin.register(Story)
class StoryAdmin(GuardedModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(GuardedModelAdmin):
    pass
