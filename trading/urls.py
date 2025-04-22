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
        path("", v.PokemonListView.as_view(), name="list"),
        path("pokemon/<int:pk>/", v.PokemonDetailView.as_view(),
             name="single_detail"),
        path("pokemon/<int:pk>/buy", v.BuyPokemonView.as_view(),
             name="buy_single"),
        path("pokemon/<int:pk>/sell", v.UpdateSellPriceView.as_view(),
             name="sell_single"),
        path("accounts/profile/<int:pk>/collection",
             v.UserPokemonListView.as_view(), name="user_collection"),
        ]

