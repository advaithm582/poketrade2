"""Test cases

Test cases for the store models. Mainly tests abstratctions on
text-encoded fields.
"""

__all__ = ["QueryParserTest",
           "TradingPolicyGetterTest", "StringEncodingTestCase"]
__author__ = "Advaith Menon"

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .models import Pokemon
from .helpers import QueryParser


class _Q(object):
    """A dummy Q object"""
    def __init__(self, *a, **kw):
        self.str = str(kw) if kw else a[0]

    def __and__(self, other):
        return _Q(self.str + "A" + other.str)

    def __or__(self, other):
        return _Q(self.str + "O" + other.str)

    def __invert__(self):
        return _Q("N" + self.str)


class QueryParserTest(TestCase):
    """Test the working of the Query Parser.
    """
    def test_untangle(self):
        """Test escaping acc to RFC 3986"""
        self.assertEqual("pushing,limits;",
                         QueryParser.untangle("pushing%2Climits%3B"));
        # lower case
        self.assertEqual("pushing,limits;",
                         QueryParser.untangle("pushing%2climits%3b"));

    def test_parse_small_raw(self):
        """Test parsing raw fields"""
        qp = QueryParser(valid_fields={"name": str, "year": int})
        self.assertEqual(("name__exact", "Khrushchev, Nikita"),
                         qp.parse_small_raw(
                             "name,IDENT,Khrushchev%2C Nikita"))
        self.assertEqual(("year__lte", 1991),
                         qp.parse_small_raw("year,LTE,1991"))

        with self.assertRaises(ValueError) as e:
            # sorry math fans!
            qp.parse_small_raw("year,CONTAINS,(1991%2c2004)")
        self.assertEqual("Unsupported operation for field",
                         str(e.exception))

        with self.assertRaises(ValueError) as e:
            qp.parse_small_raw("american_counterpart,EXACT,Ronald Reagan")
        self.assertEqual("No such field: american_counterpart",
                         str(e.exception))

        with self.assertRaises(ValueError) as e:
            qp.parse_small_raw("name,is_KGB_AGENT,true");
        self.assertEqual("No such operator: IS_KGB_AGENT",
                         str(e.exception))

    def test_parse(self):
        qp = QueryParser(valid_fields={"name": str, "year": int, "potus": str})
        rv = qp.parse(
                "name,CONTAINS,ail;year,LTE,1991;@OR;potus,IDENT,"
                "Ronald Reagan;@NOT",
                qcb=_Q);
        self.assertEqual(
                "N{'potus__exact': 'Ronald Reagan'}A{'year__lte': "
                "1991}O{'name__contains': 'ail'}",
                rv.str)


class TradingPolicyGetterTest(TestCase):
    """Test if the Trading Policy Getters work properly, and
    if their constant values (1, 2, 3) are fixed.
    """

    TP_FOR_SALE = 1
    TP_CLAIMED = 2
    TP_RESERVED = 3

    def setUp(self):
        """Set up the tests with dummy Pokemon.

        Here, Pokemon unique by trading policy are created.
        """
        self.usr = User(username="gpburdell",
                        first_name="George",
                        last_name="Burdell",
                        email="gpburdell@gatech.edu")
        # for sale
        self.p1 = Pokemon(name="crocodile",
                          sell_price=25565,
                          owner=self.usr);
        # claimed
        self.p2 = Pokemon(name="cat",
                          sell_price=0,
                          owner=self.usr);
        # reserved
        self.p3 = Pokemon(name="dog",
                          sell_price=0);

    def test_hardcoded(self):
        """Test if the trading policies are hard set correctly"""
        self.assertEqual(self.TP_FOR_SALE, self.p1.trading_policy);
        self.assertEqual(self.TP_CLAIMED, self.p2.trading_policy);
        self.assertEqual(self.TP_RESERVED, self.p3.trading_policy);


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


