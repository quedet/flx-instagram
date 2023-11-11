from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from apps.assets.models import Media, Video
from apps.accounts.models import User


# Create your views here.
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/account/profile/posts.html'

    def get(self, request, *args, **kwargs):
        account = User.objects.get(username=kwargs['user_name'])
        return self.render_to_response({
            'account': account,
            'section': 'posts'
        })


class ProfileReelsView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/account/profile/reels.html'

    def get(self, request, *args, **kwargs):
        account = User.objects.get(username=kwargs['user_name'])
        reels = Media.objects.filter(content_type=ContentType.objects.get_for_model(Video), owner=account)
        return self.render_to_response({
            'account': account,
            'reels': reels,
            'section': 'reels'
        })


class ProfileBookmarkView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/account/profile/bookmark.html'

    def get(self, request, *args, **kwargs):
        account = User.objects.get(username=kwargs['user_name'])
        return self.render_to_response({
            'account': account,
            'section': 'bookmark'
        })


class ProfileTaggedView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/account/profile/tagged.html'

    def get(self, request, *args, **kwargs):
        account = User.objects.get(username=kwargs['user_name'])
        return self.render_to_response({
            'account': account,
            'section': 'tagged'
        })


class ProfileFollowingView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/account/profile/following.html'

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=kwargs['user_name'])
        return self.render_to_response({
            'account': user
        })


class ProfileFollowersView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/account/profile/followers.html'

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=kwargs['user_name'])
        return self.render_to_response({
            'followers': user.followers.all()
        })
