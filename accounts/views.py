"""Views for the Accounts app.

Contains signup pages and the profile page.
"""

__all__ = ["ProfileView", "ProfileUpdateView", "my_profile"]

__author__ = "Advaith Menon"

from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, reverse
from django.views.generic.edit import UpdateView

from .models import User


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
        return reverse("accounts:profile", kwargs=self.kwargs)


def my_profile(request):
    return redirect(reverse("accounts:profile", args=[request.user.pk]))
