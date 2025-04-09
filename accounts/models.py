"""User Models for Authentication.

Subclasses Django's default User Model to allow for more efficient
database queries. With a one-to-one relation, two queries would be
required for every profile attribute query:

#. ``SELECT user_id FROM users WHERE username=?``
#. ``SELECT * FROM profile WHERE user_id=?``

It is possible to do this with an inner join (``SELECT * from users,
profile WHERE users.user_id=? AND users.user_id = profile.user_id``),
but that has an equivalent database hit - two database tables have
to be queried.

One-to-one relations are generally a bad idea, since fields can be put
in the same table (unless of course you exceed the max column limit,
but you should seriously reconsider your design if you are near there.)
By putting fields along with the User object, querying becomes faster
and the database is free to do more work.
"""

__all__ = ["User"]
__author__ = "Advaith Menon"

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Defines a PokeTrade2 User.

    A PokeTrade2 user consists of normal user attributes, as defined by
    Django, and some custom attributes, which are documented below.
    """

    # The coins owned by a user
    coins = models.IntegerField(default=0)

    # The user's streak
    streak = models.IntegerField(default=0)

