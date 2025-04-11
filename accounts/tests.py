"""Tests for Accounts

Test certain flows and model methods.
"""

__all__ = ["GravatarTestCase"]
__author__ = "Advaith Menon"

import hashlib
from urllib.parse import parse_qs
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from .models import User


class GravatarTestCase(TestCase):
    """Test if Gravatar Conversion works properly.
    """
    def setUp(self):
        """Create dummy test objects.
        """
        self.u1 = User(username="webmaster",
                       first_name="Web",
                       last_name="Master");
        self.u2 = User(email="gpburdell@gatech.edu");

    def test_simple(self):
        """Test basic behavior of vanilla Gravatar method.

        This ensures that default params remain consistent.
        """
        url, _, param = self.u2.gravatar().partition("?");
        param = parse_qs(param)
        self.assertEqual(
                "https://www.gravatar.com/avatar/"
                + hashlib.sha256("gpburdell@gatech.edu".encode()).hexdigest(),
                url);
        self.assertEqual({
            "d": ["wavatar"], "s": ["40"], "name": [" "]},
            param);

    def test_fallback(self):
        """Test basic behavior of fallback Gravatar method.

        This ensures that default params remain consistent.
        """
        url, _, param = self.u1.gravatar().partition("?");
        param = parse_qs(param)
        self.assertEqual(
                "https://www.gravatar.com/avatar/"
                + hashlib.sha256("webmaster@example.org".encode()).hexdigest(),
                url);
        self.assertEqual({
            "d": ["wavatar"], "s": ["40"], "name": ["Web Master"]},
            param);


class UpdateInterestTest(TestCase):
    """Tests if the Update Interest command works as intended.
    """
    def setUp(self):
        self.p47 = User.objects.create(username="realDonaldTrump",
                            coins=120000)
        self.p46 = User.objects.create(username="JoeRogan",
                            coins=0)

    def refresh_props(self):
        """Refresh objects from database
        """
        self.p47.refresh_from_db()
        self.p46.refresh_from_db()

    def test_interest_zero(self):
        """Tests if an interest of zero percent retains the account
        balance.
        """
        call_command("update_interest", 0)
        self.refresh_props()
        self.assertEqual(120000, self.p47.coins)
        self.assertEqual(0, self.p46.coins)

    def test_interest_half(self):
        """Tests if an interest of 50 percent increases the account
        balance.
        """
        call_command("update_interest", 0.5)
        self.refresh_props()
        self.assertEqual(120000 * 1.5, self.p47.coins)
        self.assertEqual(0, self.p46.coins)

