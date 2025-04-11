"""Updates the monthly interest on users.

The command must be executed monthly by cron.
"""

__all__ = ["Command"]
__author__ = "Advaith Menon"

from django.core.management.base import BaseCommand
from django.db.models import F
from accounts.models import User


class Command(BaseCommand):
    help = "Updates interest for users"

    def add_arguments(self, parser):
        # this is just a Python standard argparse object
        parser.add_argument("interest_value", action="store",
                            type=float,
                            help="Interest value as multiplier")

    def handle(self, *args, **options):
        """Handle the command.

        Refer to Django Docs to learn more about this class.
        """
        User.objects.all().update(coins=(options["interest_value"] + 1) \
                * F("coins"))

