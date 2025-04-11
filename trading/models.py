"""PokeTrade2 Models

Since PokeTrade2 is already used as the application management folder,
we have to use a separate folder. "Trading" sounded the best.
"""

__all__ = ["Pokemon", "Ability", "Attack"]
__author__ = "Advaith Menon"

from django.db import models


class Pokemon(models.Model):
    """Represents a singular Pokemon."""
    # ID is automatically taken care of by Django

    # If there is no code below, run the code generator!!
    # Rarity Enum
    # ~machine~begin~{e77bdfa3-a871-445c-b412-d7914751c6b7}
    # ~machine~end~{e77bdfa3-a871-445c-b412-d7914751c6b7}

    name = models.CharField(max_length=256)
    supertype = models.CharField(max_length=256, null=True)
    # NOTE: use the property ".subtypes", it is a list which will
    # do the serialization for you.
    subtype_l = models.TextField(default="");
    hp = models.IntegerField(default=-1);
    # NOTE: use the property ".types", it is a list which will
    # do the serialization for you.
    type_l = models.TextField(default="");
    description = models.TextField(default="")
    # Some pokemon don't evolve from anything. Just like how some random
    # bacteria pop out of nowhere.
    # evolvesFrom = models.CharField(max_length=127, null=True,
    # blank=True)
    evolvesFrom = models.ForeignKey("self", on_delete=models.CASCADE,
                                    null=True, blank=True);
    # Sometimes, Pokemon just evolve to nothing. Just as how after
    # robots take over the world, there will be nothing left. Just
    # better robots.
    # evolvesTo = models.CharField(max_length=127, null=True, blank=True)
    # NOTE: we don't need evolvesTo, we can just query for all
    # "children" of a pokemon since evolvesFrom is a PK.

    # separated by newlines
    rules = models.TextField(default="");

    # To get abilities, refer to the docs:
    # https://docs.djangoproject.com/en/5.1/topics/db/queries/#following-relationships-backward

    # NOTE: use the property ".weaknesses", it is a hashmap which will
    # do the serialization for you.
    weakness_h = models.TextField(default="");

    # NOTE: use the property ".resistances", it is a hashmap which will
    # do the serialization for you.
    resistance_h = models.TextField(default="");

    # NOTE: use the property ".retreat_cost", it is a list which will
    # do the serialization for you.
    retreat_l = models.TextField(default="");

    # NOTE: use the virtual property ".converted_retreat_cost"
    # (non-editable)

    # NOTE: set has been skipped with prior discussion with Hardik

    # NOTE: field name is misleading
    number = models.CharField(max_length=64, default="");

    artist = models.CharField(max_length=256, default="");



    flavorText = models.TextField(default="");

    # NOTE: use the property ".national_pokedex_numbers" instead, it is
    # a list which will do the serialization for you.
    national_l = models.TextField(default="");

    # If there is no code below, run the code generator!!
    # Rarity Field
    # ~machine~begin~{028c3792-35e5-4337-8947-67c7f0a8f139}
    # ~machine~end~{028c3792-35e5-4337-8947-67c7f0a8f139}

    flavorText = models.TextField(default="");

    image = models.ImageField(upload_to='pokemon_images/')

    # NOTE: 0 is a null value for this
    average_sell_price = models.FloatField(default=0);
    low_price = models.FloatField(default=0);
    trend_price = models.FloatField(default=0);
    suggested_price = models.FloatField(default=0);

    # real sell price
    sell_price = models.FloatField(default=0);

    @property
    def weaknesses(self):
        """A Pythonic Getter for weaknesses.

        :return: The weaknesses of a Pokemon
        :rtype: dict
        """
        return {
                x.partition("=")[0] : x.partition("=")[2]
                for x in self.weakness_h.split(";")
               }

    @weaknesses.setter
    def weaknesses(self, weaknesses):
        """A Pythonic way to set weaknesses.

        :param weaknesses: The weaknesses to set to.
        :type weaknesses: dict
        """
        if weaknesses is None:
            weaknesses = dict(); # an empty dict works
        retstr = "";
        for k, v in weaknesses.items():
            retstr += "%s=%s;" % (k, v);
        retstr = retstr.strip(";");
        self.weakness_h = retstr;

    @property
    def resistances(self):
        """A Pythonic Getter for resistances.

        :return: The resistances of a Pokemon
        :rtype: dict
        """
        return {
                x.partition("=")[0] : x.partition("=")[2]
                for x in self.resistance_h.split(";")
               }

    @resistances.setter
    def resistances(self, resistances):
        """A Pythonic way to set resistances.

        :param resistances: The resistances to set to.
        :type resistances: dict
        """
        if resistances is None:
            resistances = dict(); # an empty dict works
        retstr = "";
        for k, v in resistances.items():
            retstr += "%s=%s;" % (k, v);
        retstr = retstr.strip(";");
        self.resistance_h = retstr;

    @property
    def retreat_cost(self):
        """A Pythonic way to deal with retreats.

        :return: A retreat cost, in the form of a list
        :rtype: list
        """
        return self.retreat_l.split(",");

    @retreat_cost.setter
    def retreat_cost(self, retreat_cost):
        """A Pythonic way to set retreats.

        :param retreat_cost: The retreat cost, in the form of a list
        :type retreat_cost: list
        """
        self.retreat_l = ",".join(retreat_cost);

    @property
    def converted_retreat_cost(self):
        """Return the number of retreat costs.

        :return: The number of retreat costs, or 0 if not applicable
        :rtype: int
        """
        return self.retreat_l.count(",") + 1 \
                if self.retreat_l is not None else 0;

    @property
    def subtypes(self):
        """A Pythonic way to deal with subtypes.

        :return: A subtype, in the form of a list
        :rtype: list
        """
        return self.subtype_l.split(",");

    @subtypes.setter
    def subtypes(self, subtypes):
        """A Pythonic way to set subtypes.

        :param subtypes: The subtype, in the form of a list
        :type subtypes: list
        """
        self.subtype_l = ",".join(subtypes);

    @property
    def types(self):
        """A Pythonic way to deal with types.

        :return: A type, in the form of a list
        :rtype: list
        """
        return self.type_l.split(",");

    @types.setter
    def types(self, types):
        """A Pythonic way to set types.

        :param types: The type, in the form of a list
        :type types: list
        """
        self.type_l = ",".join(types);

    @classmethod
    def get_random_pokemon(self):
        """Get a random pokemon from the TCG API that is not already
        present.

        :returns: A Pokemon object randomly selected from the TCG API
        :rtype: class`store.Pokemon`
        """
        # TODO: implement
        ...

    def __repr__(self):
        return "<Pokemon id=%s, name=%s>" % (id, name);


class Ability(models.Model):
    """Represents the abilities of a Pokemon.
    """
    name = models.CharField(max_length=128);
    # description of the ability
    text = models.TextField();
    type = models.CharField(max_length=256);
    pokemons = models.ManyToManyField(Pokemon);
    class Meta:
        constraints = [
                models.UniqueConstraint(fields=["name"],
                                        name="uniq_ability_name"),
                ];
        indexes = [
                models.Index(fields=["name"], name="ix_ability_name"),
                ];


class Attack(models.Model):
    """Represents the attacks of a Pokemon.
    """
    name = models.CharField(max_length=128);
    # For now, costs are a text field with ',' as delimiter
    cost_s = models.TextField();
    text = models.TextField();
    damage = models.CharField(max_length=64);
    # this is a many-to-one since the value of damage could vary.
    pokemons = models.ForeignKey(Pokemon, on_delete=models.CASCADE);

    @property
    def costs(self):
        """Get the value of costs in a Pythonic way.

        :return: The costs of the attack
        :rtype: list
        """
        return self.cost_s.split(",");

    @costs.setter
    def costs(self, costs):
        """Set the value of costs in a Pythonic way.

        :param costs: The costs list to set to.
        :type costs: list
        """
        self.cost_s = ",".join(costs);

    class Meta:
        constraints = [
                models.UniqueConstraint(fields=["name"],
                                        name="uniq_attack_name"),
                ];
        indexes = [
                models.Index(fields=["name"], name="ix_attack_name"),
                ];
