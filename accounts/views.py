"""Views for the Accounts app.

Contains signup pages and the profile page.
"""

__all__ = ["ProfileView", "ProfileUpdateView", "MyPokemonsListView",
           "my_profile"]

__author__ = "Advaith Menon"

from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, reverse
from django.views.generic.edit import UpdateView

from .models import User
from trading.models import Pokemon


class MyPokemonsListView(LoginRequiredMixin, ListView):
    """Lists a users' owned Pokemon.
    """
    template_name = "accounts/my_pokemons.html"
    model = Pokemon
    context_object_name = "pokemons"

    def get_context_data(self, **kwargs):
        # to modify message on search
        ctx = super().get_context_data(**kwargs)
        ctx["query_str"] = self.request.GET.get("s", "")
        return ctx


    def get_queryset(self):
        if "s" in self.request.GET:
            # we have a search term
            term = self.request.GET["s"]
            return self.request.user.pokemons.filter(name__contains=term)
        return self.request.user.pokemons.all()


class ProfileView(LoginRequiredMixin, DetailView):
    """Enables viewing of profiles.
    """
    template_name = "accounts/user_detail.html"
    context_object_name = "the_user"
    model = User


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ["username", "first_name", "last_name", "email"]
    # accounts/user_update.html.bak
    template_name_suffix = "_update"

    def get_object(self, *args, **kw):
        """Get the object requested by the user.

        This is overriden to prevent users from editing each others'
        profiles.
        """
        obj = super().get_object(*args, **kw)
        if obj != self.request.user:
            # malicious user
            raise PermissionDenied
        return obj

    def get_success_url(self):
        """URL to redirect on success

        :return: A URL to redirect to on success
            This is the profile just edited.
        :rtype: str
        """
        return reverse("accounts:profile", kwargs=self.kwargs)


def my_profile(request):
    return redirect(reverse("accounts:profile", args=[request.user.pk]))
