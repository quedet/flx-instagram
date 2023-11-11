from django.urls import path

from .views import *

app_name = 'assets'

urlpatterns = [
    path('upload/', UploadMedia.as_view(), name='upload')
]