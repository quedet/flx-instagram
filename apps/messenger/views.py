from django.views.generic import TemplateView
from django.contrib.postgres.search import TrigramWordSimilarity
from apps.accounts.models import User
from apps.messenger.models import Message, Room
from django.shortcuts import get_object_or_404
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator


class NewMessageView(TemplateView):
    template_name = 'pages/messenger/new_message.html'

    def post(self, request, *args, **kwargs):
        return self.render_to_response({

        })


class MessengerChatRoomView(TemplateView):
    template_name = 'pages/core/messenger.html'
    account = None
    room = None

    def dispatch(self, request, *args, **kwargs):
        self.account = get_object_or_404(User, username=kwargs['user_name'])
        self.room = Room.objects.filter(users_subscribed__in=[self.account]).intersection(Room.objects.filter(users_subscribed__in=[request.user])).first()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        messages = Message.objects.filter(room=self.room)

        return self.render_to_response({
            'account': self.account,
            'rooms': Room.objects.filter(users_subscribed__in=[request.user]).exclude(messages=None),
            'messages': messages
        })


class SearchAccountView(TemplateView):
    template_name = 'pages/messenger/search_account.html'

    def post(self, request, *args, **kwargs):
        query = request.POST.get('query', None)
        accounts = []

        if query and str(query).strip() != '':
            accounts = User.objects.exclude(username__in=[request.user.username, 'AnonymousUser']).annotate(
                similarity=TrigramWordSimilarity(query, 'username') + TrigramWordSimilarity(query, 'first_name') +
                           TrigramWordSimilarity(query, 'last_name')).filter(similarity__gt=0.3).order_by('-similarity')

        return self.render_to_response({
            'accounts': accounts
        })
