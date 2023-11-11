from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import *

app_name = 'registration'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout')
]
