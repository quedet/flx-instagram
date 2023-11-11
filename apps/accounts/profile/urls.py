from django.urls import path
from .views import *

app_name = 'profile'

urlpatterns = [
    path('', ProfileView.as_view(), name='posts'),
    path('reels/', ProfileReelsView.as_view(), name='reels'),
    path('tagged/', ProfileTaggedView.as_view(), name='tagged'),
    path('saved/', ProfileBookmarkView.as_view(), name='bookmarked'),
    path('followers/', ProfileFollowersView.as_view(), name='followers'),
    path('following/', ProfileFollowingView.as_view(), name='following'),
]
