"""Views for the Accounts app.

Contains signup pages and the profile page.
"""

__all__ = ["ProfileView", "ProfileUpdateView", "MyPokemonsListView",
           "my_profile", "signup_v2_init",
           "signup_v2_verify",]

__author__ = "Advaith Menon"

from time import time
from datetime import datetime

from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, reverse, render
from django.contrib import messages
from django.views.generic.edit import UpdateView
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import jwt

from .models import User
from .forms import UserRegistrationRequestForm, \
        UserCreationForm
from trading.models import Pokemon
from trading.helpers import assign_pokemon_to_user


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
    # accounts/user_update.html
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
        return reverse("profile", kwargs=self.kwargs)


def my_profile(request):
    return redirect(reverse("profile", args=[request.user.pk]))


def signup_v2_init(request):
    form = UserRegistrationRequestForm()
    if request.method == "POST":
        form = UserRegistrationRequestForm(request.POST)
        if form.is_valid():
            if not User.objects.filter(email=form.cleaned_data["email"])\
                    .exists():
                token = jwt.encode({"email": form.cleaned_data["email"],
                            "first": form.cleaned_data["first_name"],
                            "last": form.cleaned_data["last_name"],
                            "exp": time() + 600},
                           settings.SECRET_KEY,
                           algorithm="HS256")
                link = request.get_host() + reverse("sverify",
                                                  kwargs=dict(token=token))
                send_mail(
                        "[GT Movie Store] Account Registration Request",
                        render_to_string("accounts/signup_v2_init.txt",
                             dict(email=form.cleaned_data["email"],
                                  link=link)),
                             settings.SERVER_EMAIL,
                             [form.cleaned_data["email"]],
                             fail_silently=False
                         )
            messages.success(request, "Check your email inbox")
            return redirect(reverse("trading:list"))
    return render(request, "accounts/signup_v2_init.html",
              dict(form=form))


def signup_v2_verify(request, token):
    try:
        token = jwt.decode(token, settings.SECRET_KEY,
                           algorithms=["HS256"])
        if request.method == "GET":
            if User.objects.filter(email=token["email"]).exists():
                raise RuntimeError("User exists")
            form = UserCreationForm()
            return render(request, "accounts/signup_v2_verify.html",
                          dict(form=form,
                               exp=datetime.fromtimestamp(token["exp"])))
        elif request.method == "POST":
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                user.email = token["email"]
                user.first_name = token["first"]
                user.last_name = token["last"]
                assign_pokemon_to_user(user)
                user.save()
                messages.success(request, "user created login now to get $$$")
                return redirect(reverse("trading:list"))
            else:
                form = form
                return render(request, "accounts/signup_v2_verify.html",
                              dict(form=form,
                                   exp=datetime.fromtimestamp(token["exp"])))
    except Exception as e:
        print(e)
        messages.error(request, "Link expired or user exists")
        return redirect(reverse("trading:list"))

