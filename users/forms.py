from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# ==========================================================
# REGISTER FORM
# ==========================================================

class RegisterForm(UserCreationForm):

    class Meta:
        model = User

        fields = (
            'username',
            'email',
            'password1',
            'password2',
        )


# ==========================================================
# LOGIN FORM
# ==========================================================

class LoginForm(forms.Form):

    ROLE_CHOICES = (
        ('User', 'User'),
        ('Manager', 'Manager'),
        ('Admin', 'Admin'),
    )

    username = forms.CharField(
        max_length=150,
        label='Username'
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Password'
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='Permission'
    )
