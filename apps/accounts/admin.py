from django.contrib import admin
from guardian.admin import GuardedModelAdminMixin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, Profile, Photo,SearchHistory


# Register your models here.
@admin.register(User)
class UserAdmin(GuardedModelAdminMixin, DefaultUserAdmin):
    list_display = ['username', 'uid', 'email', 'first_name', 'last_name', 'is_staff']

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            "Personal info",
            {"fields": ("uid", "first_name", "last_name", "rooms")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined")},
        ),
    )

    readonly_fields = ['uid']

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("first_name", "last_name", "username", "email", "password1", "password2"),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name")


@admin.register(Profile)
class ProfileAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'gender']


@admin.register(Photo)
class PictureAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(SearchHistory)
class SearchHistoryAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    pass
