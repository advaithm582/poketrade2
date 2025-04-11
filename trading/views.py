"""Views for Trading

With the exception of the "My Pokemon" page, all other pages
be under the Trading app.
"""

__all__ = ["PokemonListView"]
__author__ = "Advaith Menon"

from django.views.generic import ListView

from .models import Pokemon


class PokemonListView(ListView):
    """Lists a users' owned Pokemon.
    """
    # template name is trading/pokemon_list.html
    # the default ^^ is okay
    model = Pokemon
    context_object_name = "pokemons"
    paginate_by = 50

    def get_context_data(self, **kwargs):
        # to modify message on search
        ctx = super().get_context_data(**kwargs)
        ctx["query_str"] = self.request.GET.get("s", "")
        return ctx


    def get_queryset(self):
        if "s" in self.request.GET:
            # we have a search term
            term = self.request.GET["s"]
            return Pokemon.objects.filter(name__contains=term)
        return Pokemon.objects.all()
