from django import forms
from django.contrib.auth import authenticate, login

from .models import User, Profile
from apps.core.utils import is_valid_email


class SignupForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your first name', 'class': 'form--input', 'data-action': 'input->registration#setUsername'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your last name', 'class': 'form--input', 'data-action': 'input->registration#setUsername'}))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your pseudo', 'class': 'form--input', 'data-registration-target': 'username',
        'data-action': 'input->registration#check'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email address', 'class': 'form--input',
        'data-action': 'input->registration#checkEmail'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'placeholder': 'Create new password', 'class': 'form--input'}))
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter the same password as before, for verification.', 'class': 'form--input'}))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        firstname = self.cleaned_data.get('first_name')
        lastname = self.cleaned_data.get('last_name')
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        password1 = self.cleaned_data.pop('password1')
        password2 = self.cleaned_data.pop('password2')

        if not firstname:
            raise forms.ValidationError({'first_name': 'Please provide a first name'})

        if not lastname:
            raise forms.ValidationError({'last_name': 'Please provide a first name'})

        if not username:
            raise forms.ValidationError({'username': 'Please provide a first name'})

        if not email:
            raise forms.ValidationError({'email': 'Please provide a first name'})

        if not password1:
            raise forms.ValidationError({'password1': 'Please provide a first name'})

        if not password2:
            raise forms.ValidationError({'password2': 'Please provide a first name'})

        if password2 != password1:
            raise forms.ValidationError({'password2': "Confirmation password doesn't match."})
        else:
            self.cleaned_data.update({'password': password1})

        if not is_valid_email(email):
            raise forms.ValidationError({'email': 'Please provide a valid email. eg xyz@xyz.com'})

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError({'username': f'User with Username "{username}" already exists'})

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError({'email': f'User with email address "{email}"'})

        return self.cleaned_data

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']


class LoginForm(forms.Form):
    identifier = forms.CharField(label='Identifier', widget=forms.TextInput(attrs={'placeholder': 'Enter your username or your email address', 'class': 'form--input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form--input'}))

    def __init__(self, request=None, *args, **kwargs):
        self.user = None
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        identifier = self.cleaned_data.get('identifier', None)
        password = self.cleaned_data.get('password', None)

        if not identifier:
            raise forms.ValidationError({'identifier': 'Please supply a username or a valid email address'})

        if not password:
            raise forms.ValidationError({'password': 'Please supply a password'})

        if is_valid_email(identifier):
            try:
                User.objects.get(email=identifier)
            except User.DoesNotExist:
                raise forms.ValidationError({'identifier': 'There is no user with that email'})
        else:
            try:
                User.objects.get(username=identifier)
            except User.DoesNotExist:
                raise forms.ValidationError({'identifier': 'There is no user with that username'})

        user = authenticate(request=self.request, username=identifier, password=password)

        if user is None:
            raise forms.ValidationError({'password': 'Supply a correct password'})
        self.user = user

        return self.cleaned_data

    def get_user(self):
        return self.user


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']
        labels = {
            'enable_suggestions': 'Show account suggestions on profiles'
        }
        widgets = {
            'enable_suggestions': forms.CheckboxInput(attrs={'class': 'field--checkbox', 'required': False}),
            'bio': forms.Textarea(
                attrs={'class': 'field--input', 'data-controller': "textarea-autogrow",
                       'data-textarea-autogrow-resize-debounce-delay-value': "500", 'rows': 3,
                       'data-character-counter-target': 'input', 'maxlength': 150})
        }