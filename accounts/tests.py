"""Tests for Accounts

Test certain flows and model methods.
"""

__all__ = ["GravatarTestCase"]
__author__ = "Advaith Menon"

import hashlib
from urllib.parse import parse_qs

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

