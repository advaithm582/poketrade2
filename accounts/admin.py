"""Admin Registration for Accounts

Registration of all account-related models is done here.
"""

__all__ = []
__author__ = "Advaith Menon"

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


admin.site.register(User, UserAdmin);

