"""Test cases

Test cases for the store models. Mainly tests abstratctions on
text-encoded fields.
"""

__all__ = ["StringEncodingTestCase"]
__author__ = "Advaith Menon"

from django.test import TestCase
from django.urls import reverse

from .models import Pokemon


class StringEncodingTestCase(TestCase):
    """Test if string encodings work properly.

    Lists are encoded in a CSV-like format: ``Ramblin' Wreck, Fightin'
    Pollen,Buzz`` would become ``["Ramblin' Wreck", "Fightin' Pollen",
    "Buzz"]``.

    Hashmaps are encoded in environment variable style:
    ``best_university=Georgia Tech;worst_university=university [sic] of
    Georgia;mid_university=Quahog University`` would become
    ```{"best_university": "Georgia Tech", "worst_university":
    "university [sic] of Georgia", "mid_university": "Quahog
    University"}```

    It is **not** possible to encode non-character values into
    this format directly. However, one could encode the non-character
    object to a string and encode it.

    Consecutive commas are empty strings - this is by design. Similarly,
    the pair ``=;`` is a map from an empty string to an empty string. It
    is possible to repeat keys - they will be overwritten with the most
    recent instance (the rightmost).

    **Escape characters are not supported**. Usage of special characters
    (``,``, ``=``, ``;``) can yield in unexpected output.
    """
    def test_getters_no_edge(self):
        """Test getters, with no edge cases"""
        edison = Pokemon(name="Edison Hong", supertype="CS 2340",
                         subtype_l="el1,el2,el3",
                         hp=420,
                         resistance_h="sleep=1000x;leisure=100x");
        # Per Junit convention, expected is followed by actual
        self.assertEqual(["el1", "el2", "el3"],
                         edison.subtypes);

        self.assertEqual({"sleep": "1000x", "leisure": "100x"},
                         edison.resistances);

    def test_getters_edge(self):
        """Test edge cases with all getters"""
        advaith = Pokemon(name="Advaith", supertype="CS 2340",
                          subtype_l=",el@1,,el2,",
                          hp=1024,
                          resistance_h="=;=hello;world=;j=k;=");
        self.assertEqual(["", "el@1", "", "el2", ""],
                         advaith.subtypes);

        self.assertEqual({"": "", "world": "", "j": "k"},
                         advaith.resistances);

    def test_setters_edge(self):
        mario = Pokemon(name="Mario");
        mario.subtypes = ["", "el@1", "", "el2", ""]
        mario.resistances = {"": "", "worl": "", "m": "k"}
        self.assertEqual(",el@1,,el2,",
                         mario.subtype_l);
        self.assertEqual("=;worl=;m=k",
                         mario.resistance_h);


