from django.views.generic import TemplateView, FormView
from apps.accounts.forms import SignupForm, LoginForm
from django.contrib.auth import login
from django.shortcuts import redirect

from apps.accounts.models import User

import http


# Create your views here.
class SignupView(FormView):
    template_name = 'pages/registration/signup.html'
    form_class = SignupForm

    def get_success_url(self):
        return self.request.GET.get('next', '/')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        new_user = User.objects.create_user(**form.cleaned_data)
        login(self.request, user=new_user, backend='apps.accounts.backends.AuthenticationBackend')
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = http.HTTPStatus.UNPROCESSABLE_ENTITY
        return response


class LoginView(FormView):
    template_name = 'pages/registration/login.html'
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.GET.get('next', '/')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, user=form.get_user(), backend='apps.accounts.backends.AuthenticationBackend')
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = http.HTTPStatus.UNPROCESSABLE_ENTITY
        return response
