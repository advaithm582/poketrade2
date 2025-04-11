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

import hashlib
from urllib.parse import urlencode

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

    def gravatar(self, size=40, *, fallback="wavatar",
                 default="{username}@example.org"):
        """Get the User's Gravatar.

        To have a pseudo-Pokemon theme, the attribute ``wavatar`` is
        used if the avatar does not exist.

        If the email does not exist, the generated hash is of the
        form ``username@example.net``.

        :param size: The size of the image. Defult: 40.
        :type size: int
        :param fallback: The fallback avatar to use. Default: wavatar
        :type size: str
        :param default: The default email to use. Format specifiers
        ``username``, ``first``, ``last`` are replaced in .format()
        style.
        :type default: str
        :return: A string with the correct Gravatar URL.
        :rtype: str
        """
        # Get the user's email
        email = (self.email
                 or default.format(username=self.username,
                                   first=self.first_name,
                                   last=self.last_name))

        param = dict();

        # Get the hash
        hash = hashlib.sha256(email.encode()).hexdigest()
        param["d"] = fallback
        param["s"] = str(size)
        param["name"] = ' '.join((self.first_name or "", self.last_name or ""))
        param = urlencode(param);
        return "https://www.gravatar.com/avatar/{}?{}".format(hash, param)

