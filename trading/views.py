"""Views for Trading

With the exception of the "My Pokemon" page, all other pages
be under the Trading app.
"""

__all__ = ["PokemonListView"]
__author__ = "Advaith Menon"

from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .models import Pokemon
from .helpers import QueryParser


class PokemonListView(ListView):
    """Lists a users' owned Pokemon.
    """
    # template name is trading/pokemon_list.html
    # the default ^^ is okay
    model = Pokemon
    context_object_name = "pokemons"
    paginate_by = 50

    # defines the custom query
    __qparse = QueryParser(valid_fields={"name": str, "hp": int,
                            "rarity": str, "sell_price": float})

    def __get_userquery(self):
        """Get the user's query (simple or advanced)
        """
        if "q" in self.request.GET:
            return self.request.GET["q"]
        elif "s" in self.request.GET:
            return "name,CONTAINS,%s" % (
                    self.request.GET["s"].replace(",", "%2C") \
                            .replace(";", "%3B") \
                            .replace(":", "%3A") \
                            .replace("@", "%40"))
        else:
            return None

    def __get_pu(self):
        """Get Parsed User Query"""
        return self.__qparse.parse(self.__get_userquery())

    def get_context_data(self, **kwargs):
        # to modify message on search
        ctx = super().get_context_data(**kwargs)
        ctx["query_str"] = self.__get_userquery() or "";
        return ctx


    def get_queryset(self):
        if self.__get_userquery() is not None:
            # we have a search term
            return Pokemon.objects.filter(self.__get_pu())
        return Pokemon.objects.all()


class PokemonDetailView(DetailView):
    # template: trading/pokemon_detail.html
    model = Pokemon
    context_object_name = "the_pokemon"

