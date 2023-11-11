from django.urls import path
from apps.accounts.management.views import *

app_name = 'manage'

urlpatterns = [
    path('', EditProfileView.as_view(), name='profile'),
    path('picture/', EditProfilePictureView.as_view(), name='profile-picture')
]
