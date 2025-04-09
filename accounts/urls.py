"""URL Configuration for Accounts
"""

__all__ = ["app_name", "urlpatterns"]
__author__ = "Advaith Menon"

from django.urls import include, path

# Creates the 'accounts' namespace.
app_name = "accounts"


# Describes the URLs in this namespace.
urlpatterns = [
        path("", include("django.contrib.auth.urls")),
        ]

