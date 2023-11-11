from django.urls import path
from .views import *

app_name = 'core'

urlpatterns = [
    path("", HomeView.as_view(), name='home'),
    path("p/<post_id>/", PostDetailsView.as_view(), name='details'),
    path("search/", SearchView.as_view(), name='search'),
    path("search/results/", SearchResultsView.as_view(), name='search-results'),
    path("explore/", ExploreView.as_view(), name='explore'),
    path("reels/", ReelsRedirectionView.as_view(), name='reels'),
    path("reels/<reel_id>/", ReelsView.as_view(), name='reels-details'),
    path("direct/inbox/", MessagesView.as_view(), name='messages'),
    path("notifications/", NotificationsView.as_view(), name='notifications'),
    path("create/", CreateView.as_view(), name='create'),
    path("profile/", ProfileView.as_view(), name='profile'),
    path("create-story/", CreatStoryView.as_view(), name='create-story'),
    path("stories/<user_name>/<story_id>/", UserStoryView.as_view(), name='stories')
]
