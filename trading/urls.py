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
        # path("pokemon/<int:pk>/", v.PokemonDetailView.as_view(),
        #      name="single_detail"),
        path("pokemon/<int:pk>/buy", v.BuyPokemonView.as_view(),
             name="buy_single"),
        path("pokemon/<int:pk>/", v.UpdateSellPriceView.as_view(),
             name="single_detail"),
        path("accounts/profile/<int:pk>/collection",
             v.UserPokemonListView.as_view(), name="user_collection"),
        path("accounts/profile/<int:pk>/wishlist",
             v.UserPokemonWishListView.as_view(), name="user_wl"),
        path("pokemon/<int:pk>/wish", v.WishPokemonView.as_view(),
             name="wish"),
        path("pokemon/<int:pk>/unwish", v.UnWishPokemonView.as_view(),
             name="unwish"),
        ]

