"""URL Configuration for Accounts
"""

__all__ = ["app_name", "urlpatterns"]
__author__ = "Advaith Menon"

from django.urls import include, path

from . import views as v

# Creates the 'accounts' namespace.
app_name = "accounts"


# Describes the URLs in this namespace.
urlpatterns = [
        path("", include("django.contrib.auth.urls")),
        path("profile/<int:pk>/", v.ProfileView.as_view(), name="profile"),
        path("profile/<int:pk>/edit", v.ProfileUpdateView.as_view(),
             name="edit_profile"),
        path("profile/", v.my_profile, name="my_profile"),
        path("profile/pokemon", v.MyPokemonsListView.as_view(),
             name="my_pokemon"),
        ]

