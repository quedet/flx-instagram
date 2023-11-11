from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from .models import Profile, Photo, User, SearchHistory

from guardian.shortcuts import assign_perm


# @receiver(m2m_changed, sender=User.followings.through)
# def user_followings_changed(sender, instance, **kwargs):
#     print(instance.rel_from_set)


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created and instance.email is not None:
        permissions = [
            'accounts.add_user',
            'accounts.change_user',
            'accounts.delete_user',
            'accounts.view_user'
        ]

        for perm in permissions:
            assign_perm(perm, instance, instance)

        Profile.objects.create(user=instance)
        Photo.objects.create(user=instance)
        SearchHistory.objects.create(account=instance)


@receiver(post_save, sender=Profile)
def user_profile_post_save(sender, instance, created, **kwargs):
    if created and instance.user is not None:
        permissions = [
            'accounts.add_profile',
            'accounts.change_profile',
            'accounts.delete_profile',
            'accounts.view_profile'
        ]

        for perm in permissions:
            assign_perm(perm, instance.user, instance)
