"""Views for Trading

With the exception of the "My Pokemon" page, all other pages
be under the Trading app.
"""

__all__ = ["PokemonListView", "PokemonDetailView",
           "UserPokemonListView", "BuyPokemonView",
           "UpdateSellPriceView", "UserPokemonWishListView",
           "WishPokemonView", "UnWishPokemonView"]
__author__ = "Advaith Menon"

from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import get_object_or_404, reverse, redirect
from django.contrib import messages
from django.db.models import Q

from accounts.models import User
from .models import Pokemon, TradingPolicy
from .helpers import QueryParser, QueryableMixin


class PokemonListView(QueryableMixin, ListView):
    """Lists all Pokemon.
    """
    # template name is trading/pokemon_list.html
    # the default ^^ is okay
    model = Pokemon
    context_object_name = "pokemons"
    paginate_by = 100

    # defines the custom query
    generic_qparse = QueryParser(valid_fields={"name": str, "hp": int,
                            "rarity": str, "sell_price": float,
                            "owner__username": str})


class UserPokemonListView(QueryableMixin, LoginRequiredMixin, ListView):
    """Lists a single users' Pokemon.
    """
    model = Pokemon
    context_object_name = "pokemons"
    paginate_by = 100

    def get_queryset(self):
        # print("kwe:", type(self.kwargs.get("pk")))
        return super().get_queryset() \
                .filter(owner__pk__exact=self.kwargs.get("pk"))


class UserPokemonWishListView(QueryableMixin, LoginRequiredMixin, ListView):
    """Lists a single users' Pokemon wishlist
    """
    model = User
    context_object_name = "pokemons"
    paginate_by = 100

    # defines the custom query
    generic_qparse = QueryParser(valid_fields={"name": str, "hp": int,
                            "rarity": str, "sell_price": float,
                            "owner__username": str})

    def get_queryset(self):
        if self._get_userquery() is not None:
            return get_object_or_404(self.model, pk=self.kwargs["pk"]) \
                    .wishlist.filter(self._get_pu())
        return get_object_or_404(self.model, pk=self.kwargs["pk"]) \
                .wishlist.all()


class BuyPokemonView(LoginRequiredMixin, TemplateView):
    """Buys a pokemon if the request is POST.
    """
    http_method_names = ["post", "options"]
    template_name = "trading/bought_pokemon.html"

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # copied from the source code of the LogoutView
        # TL;DR provides CSRF protection
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pok_id = self.kwargs["pk"]
        pok_obj = get_object_or_404(Pokemon, Q(pk=pok_id)
                                    & ~Q(owner=self.request.user))
        if pok_obj.trading_policy != TradingPolicy.FOR_SALE:
            messages.error(request, "You cannot buy PokeMon not for sale!!!")
            return redirect(reverse("trading:single_detail"), args=[pok_id])


        # subtract its sell price to your account
        if self.request.user.coins < pok_obj.sell_price:
            messages.error(request,
                           "You don't have enough coins to buy PokeMon")
            return redirect(reverse("trading:single_detail"), args=[pok_id])
        self.request.user.coins -= pok_obj.sell_price

        # add sell price to owner (if exists)
        if pok_obj.owner:
            pok_obj.owner.coins += pok_obj.sell_price
            pok_obj.owner.save()

        # make POK's cost price the sell price
        pok_obj.cost_price = pok_obj.sell_price

        # make sell price 0
        pok_obj.sell_price = 0

        # update owner
        pok_obj.owner = self.request.user

        # save both
        self.request.user.save()
        pok_obj.save()
        messages.success(request, "The pokemon is now yours")
        return redirect(reverse("trading:single_detail"), args=[pok_id])
        #return super().get(request, *args, **kwargs)


class UnWishPokemonView(LoginRequiredMixin, TemplateView):
    """Wish a pokemon if the request is POST.
    """
    http_method_names = ["post", "delete", "options"]
    template_name = "trading/bought_pokemon.html"

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # copied from the source code of the LogoutView
        # TL;DR provides CSRF protection
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pok_id = self.kwargs["pk"]
        pok_obj = get_object_or_404(Pokemon, pk=pok_id)
        pok_obj.wishers.remove(request.user)
        pok_obj.save()
        return redirect(reverse("trading:user_wl", args=[request.user.pk]))


class WishPokemonView(LoginRequiredMixin, TemplateView):
    """Wish a pokemon if the request is POST.
    """
    http_method_names = ["post", "delete", "options"]
    template_name = "trading/pokemon_list.html"

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # copied from the source code of the LogoutView
        # TL;DR provides CSRF protection
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pok_id = self.kwargs["pk"]
        pok_obj = get_object_or_404(Pokemon, pk=pok_id)
        pok_obj.wishers.add(request.user)
        pok_obj.save()
        return redirect(reverse("trading:user_wl", args=[request.user.pk]))

    def delete(self, request, *args, **kwargs):
        pok_id = self.kwargs["pk"]
        pok_obj = get_object_or_404(Pokemon, pk=pok_id)
        pok_obj.wishers.delete(request.user)
        pok_obj.save()
        messages.success(request, "Pokemon removed from wishlist")
        return super().get(request, *args, **kwargs)


class UpdateSellPriceView(LoginRequiredMixin, UpdateView):
    model = Pokemon
    fields = ["sell_price"]
    # trading/pokemon_update.html
    template_name_suffix = "_update"

    def get_object(self, *args, **kw):
        """Get the object requested by the user.

        This is overriden to prevent users from selling each others'
        pokemon
        """
        obj = super().get_object(*args, **kw)
        if obj.owner != self.request.user:
            # malicious user
            raise PermissionDenied
        return obj

    def get_success_url(self):
        """URL to redirect on success

        :return: A URL to redirect to on success
            This is the profile just edited.
        :rtype: str
        """
        return reverse("trading:list")


class PokemonDetailView(DetailView):
    # template: trading/pokemon_detail.html
    model = Pokemon
    context_object_name = "the_pokemon"

    def get_context_data(self, **kwargs):
        # to modify message on search
        ctx = super().get_context_data(**kwargs)
        ctx["in_wishlist"] = \
            self.get_object().wishers.filter(pk=self.request.user.pk).exists()
        return ctx
