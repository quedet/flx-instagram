from django.urls import path, include

app_name = 'accounts'

urlpatterns = [
    path('accounts/', include('apps.accounts.registration.urls', namespace='registration')),
    path('accounts/edit/', include('apps.accounts.management.urls', namespace='manage')),
    path('t/<user_name>/', include('apps.accounts.profile.urls', namespace='profile'))
]
