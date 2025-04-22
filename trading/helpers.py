"""Trading Helpers

Contains helpers to parse advanced queries
"""

__all__ = ["QueryParser", "assign_pokemon_to_user", "QueryableMixin"]
__author__ = "Advaith Menon"

import re

from django.db.models import Q
from django.views.generic import ListView

from .models import Pokemon


# Defines an escape sequence according to RFC 3986
ESCAPE = re.compile("%([0-9A-Fa-f]{2})")


# Maps operator strings to (roughly) types and Django names
OPERATORS = {
    "IDENT": ({str, int, float}, "exact"),
    "NOCASE_IDENT": ({str}, "iexact"),
    "CONTAINS": ({str}, "contains"),
    "NOCASE_CONTAINS": ({str}, "icontains"),
    "GT": ({int, float}, "gt"),
    "LT": ({int, float}, "lt"),
    "GTE": ({int, float}, "gte"),
    "LTE": ({int, float}, "lte"),
    "BEGINS": ({str}, "startswith"),
    "ENDS": ({str}, "endswith"),
}


class QueryParser(object):
    """Implements a Query parser for any class.

    :param cls: The class to implement the query for
    :type cls:
    :param valid_fields: Fields that should be added to the query
    :type valid_fields: tuple
    :param valid_ops: Operations that should be allowed
    :type ops: tuple
    """
    def __init__(self, *, cls=None, valid_fields=None, valid_ops=None):
        self.fieldcls = cls
        if valid_fields is None:
            self.fields = {"pk": int}
        else:
            self.fields = valid_fields
        self.ops = valid_ops or ("eq")

    # def populate_fields(self):
    #     """Auto populate fields from the model as valid ones
    #     """
    #     self.fields = {map(lambda x: (x.name, str),
    #                             self.fieldcls._meta.get_fields()))

    @classmethod
    def _untangler(cls, val): return chr(int(val.group(1), base=16))

    @classmethod
    def untangle(cls, val):
        """Escape characters according to RFC 3986.

        :note:
            The untangling should be done only after all parsing!

        :param val: The value to untangle
        :type val: str
        :return: The untangled value
        :rtype: str
        """
        return ESCAPE.sub(cls._untangler, val);

    def parse_small_raw(self, val):
        """Parse small Query to a dictionary with parameters.
        
        A small query does not involve any logical operators other than
        the implicit AND (i.e. the comma).

        Examples of small queries are:
        #. ``hello,EQ,world``
        #. ``age,LTE,3``
        #. ``name,CONTAINS,Ruby Smith``
        #. ``name,IEQ,Hello&H44 World!``
        :param val: The small Query to parse
        :type val: str
        :return: A key-value pair to turn into a Q
        :rtype: tuple
        """
        x = val.split(",")
        if len(x) != 3:
            raise ValueError("There should only be 3 values on split")
        field, op, val = x
        field = self.untangle(field)
        if field not in self.fields:
            raise ValueError("No such field: %s" % field)

        if op.upper() not in OPERATORS:
            raise ValueError("No such operator: %s" % op.upper())
        op = OPERATORS[op.upper()]
        if self.fields[field] not in op[0]:
            raise ValueError("Unsupported operation for field")

        val = self.untangle(val)
        if self.fields[field] != str:
            try:
                val = (self.fields[field])(val)
            except:
                raise ValueError("Cannot convert value")

        # finally
        return "%s__%s" % (field.lower(), op[1]), val

    def parse(self, val, qcb=None):
        """Parse an expression.

        Documentation is provided separately.
        :param qcb: A Q query object. Leave at default
        :type qcb: type
        """
        if qcb is None:
            qcb = Q

        stack = list()
        for term in val.split(";"):
            if term.startswith("@"):
                # it is an operator
                if term == "@AND":
                    # pop 2 vals from stack and and them
                    stack.append(stack.pop() & stack.pop())
                elif term == "@OR":
                    # pop 2 vals from stack and and them
                    stack.append(stack.pop() | stack.pop())
                elif term == "@NOT":
                    # pop 2 vals from stack and and them
                    stack.append(~stack.pop())
            else:
                stack.append(qcb(**dict([self.parse_small_raw(term)])))

        # there should be only one Q-expr left, if not, and them all
        while len(stack) != 1:
            stack.append(stack.pop() & stack.pop())

        # return that 1 element
        return stack.pop()


class QueryableMixin(object):
    """A mixin that supports user queries.
    """
    def _get_userquery(self):
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

    def _get_pu(self):
        """Get Parsed User Query"""
        return self.generic_qparse.parse(self._get_userquery())

    def get_context_data(self, **kwargs):
        # to modify message on search
        ctx = ListView.get_context_data(self, **kwargs)
        ctx["query_str"] = self._get_userquery() or "";
        return ctx

    def get_queryset(self):
        if self._get_userquery() is not None:
            # we have a search term
            return self.model.objects.filter(self._get_pu())
        return self.model.objects.all()


def assign_pokemon_to_user(user):
    """Randomly assign Pokemon to user. Update their account balance.

    :param user: The user to assign Pokemon to.
    :type user: class`accounts.User`
    """
    # TODO
    for o in Pokemon.objects.filter(owner__isnull=True, sell_price__lte=0)\
            .order_by("?")[:10]:
        o.owner = user
        user.coins += o.sell_price \
                or o.suggested_price or o.average_sell_price \
                or o.low_price or o.trend_price
        o.save()
        user.save()

