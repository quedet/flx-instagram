from django.urls import path
from .views import *

app_name = 'messenger'

urlpatterns = [
    path('inbox/new-message/', NewMessageView.as_view(), name='new-message'),
    path("t/<user_name>/", MessengerChatRoomView.as_view(), name='room'),
    path('search/accounts/', SearchAccountView.as_view(), name='search-accounts')
]
