from django.urls import path
from .views import VideoStreamingView

urlpatterns = [
    path('stream/', VideoStreamingView.as_view(), name='video-stream')
]
