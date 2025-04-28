"""Forms for user creation"""

__author__ = "Advaith Menon"
__all__ = ["UserRegistrationRequestForm"]

from django import forms
from django.contrib.auth.forms import UserCreationForm \
        as OUserCreationForm

from .models import User


class UserRegistrationRequestForm(forms.Form):
    email = forms.EmailField(label="Email Address");
    first_name = forms.CharField(label="First Name", max_length=64);
    last_name = forms.CharField(label="Last Name", max_length=64);


class UserCreationForm(OUserCreationForm):
    class Meta(OUserCreationForm.Meta):
        model = User
