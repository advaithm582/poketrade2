"""URL Configuration for Trading
"""

__all__ = ["app_name", "urlpatterns"]
__author__ = "Advaith Menon"

from django.urls import include, path

from . import views as v

# Creates the 'accounts' namespace.
app_name = "trading"


# Describes the URLs in this namespace.
urlpatterns = [
        path("pokemon/all", v.PokemonListView.as_view(), name="list"),
        path("pokemon/<int:pk>/", v.PokemonDetailView.as_view(),
             name="single_detail"),
        ]

