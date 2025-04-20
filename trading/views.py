"""Views for Trading

With the exception of the "My Pokemon" page, all other pages
be under the Trading app.
"""

__all__ = ["PokemonListView", "PokemonDetailView",
           "UserPokemonListView"]
__author__ = "Advaith Menon"

from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .models import Pokemon
from .helpers import QueryParser, QueryableMixin


class PokemonListView(QueryableMixin, ListView):
    """Lists all Pokemon.
    """
    # template name is trading/pokemon_list.html
    # the default ^^ is okay
    model = Pokemon
    context_object_name = "pokemons"
    paginate_by = 50

    # defines the custom query
    generic_qparse = QueryParser(valid_fields={"name": str, "hp": int,
                            "rarity": str, "sell_price": float,
                            "owner__username": str})


class UserPokemonListView(QueryableMixin, ListView):
    """Lists a single users' Pokemon.
    """
    model = Pokemon


class PokemonDetailView(DetailView):
    # template: trading/pokemon_detail.html
    model = Pokemon
    context_object_name = "the_pokemon"

