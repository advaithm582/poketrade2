"""Add a pokemon

Add pokemon from the TCG rest api
"""

__all__ = ["Command"]
__author__ = "Advaith Menon"

import urllib.request
import os
import time
import tempfile

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from pokemontcgsdk import Card
from PIL import Image
from google import genai

from trading.models import Pokemon, Ability


# Offset values for cropping - don't change
X = 0.11
Y = 0.12
A = 0.78
B = 0.52


# Prompt to AI for flavorText
GEN_AI_PROMPT = ("""You are given the following card:
Name: {name}
Supertype: {supertype}
Subtypes: {subtypes}
HP: {hp}
Types: {types}
Evolves From: {evolves_from}
Rules: {rules}
Weakness: {weakness}
Resistance: {resistance}
Retreats: {retreats}

"""
"Generate a \"Flavor Text\" for this pokemon. Feel free to use any "
"resource. Do not output any additional text other than the flavor "
"text itself, output will be added directly to a database.")


def _get_crop_vals(x, y):
    """Get the crop values for an image.
    """
    return (round(x * X, 0),
            round(y * Y, 0),
            round(x * A, 0),
            round(x * B, 0))


def _ab2cc(tup):
    """Convert image offsets to Cartesian Coordinates
    """
    return (tup[0], tup[1], tup[0] + tup[2], tup[1] + tup[3])


class Command(BaseCommand):
    help = "Add pokemon(s) from the TCG API."

    def _handle_image(self, url, poke):
        pre_crop = tempfile.TemporaryFile()
        post_crop = tempfile.TemporaryFile()

        # download image
        with urllib.request.urlopen(urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64; rv:128."
                        "0) Gecko/20100101 Firefox/128.0")
                        }
                )) as im:
            pre_crop.write(im.read())

        # move pointer to beginning of file
        pre_crop.flush()
        pre_crop.seek(0)

        # save image before cropping
        poke.card.save(os.path.split(url)[1], File(pre_crop), save=False)
        pre_crop.seek(0)

        # read image with pillow
        pre_im = Image.open(pre_crop)

        post_im = pre_im.crop(_ab2cc(_get_crop_vals(*pre_im.size)))

        post_im.save(post_crop, format="png")

        pre_im.close()
        post_im.close()
        pre_crop.close()

        post_crop.seek(0)

        # save done later
        poke.image.save(os.path.split(url)[1], File(post_crop), save=False)
        post_crop.close()

    def _ability_check(self, abil):
        """Check if an Ability is already present in the database.

        :param abil: The ability to check for
        :return: The Ability object (will be created if nonexistent)
        """
        # query the database
        a = Ability.objects.filter(name=abil.name, text=abil.text or "",
                                   type=abil.type or "")
        if not a:
            a = Ability.objects.create(name=abil.name,
                                       text=abil.text or "",
                                       type=abil.type or "")
            return a
        return a[0]

    def _add_pokemon(self, poke):
        pk = Pokemon()
        self._update_pokemon(pk, poke)
        return pk

    def _update_pokemon(self, pk, poke):
        self._update_attrib_poke(pk, poke)
        pk.save()

    def _update_attrib_poke(self, pk, poke):
        """Update pokemon attributes"""
        pk.tcg_id = poke.id
        pk.name = poke.name
        if pk.supertype:
            pk.supertype = poke.supertype
        if pk.subtypes:
            pk.subtypes = poke.subtypes
        if poke.hp:
            try:
                pk.hp = int(poke.hp)
            except ValueError:
                sys.stderr.write("  * Cannot add HP for this Pokemon")
                sys.stderr.write("    {} is not an integer".format(poke.hp))

        if poke.types:
            pk.types = poke.types
        if poke.evolvesFrom:
            pk.evolves_from = poke.evolvesFrom
        if poke.weaknesses:
            pk.weaknesses = {j.type: j.value for j in poke.weaknesses}
        if poke.resistances:
            pk.resistances = {j.type: j.value for j in poke.resistances}
        if poke.retreatCost:
            pk.retreat_cost = poke.retreatCost
        if poke.number:
            pk.number = poke.number or ""
        if poke.artist:
            pk.artist = poke.artist or ""
        if poke.flavorText:
            pk.flavorText = poke.flavorText or ""
        if poke.nationalPokedexNumbers:
            pk.national_pokedex_numbers = poke.nationalPokedexNumbers
        # TODO: add rarity
        if poke.cardmarket and poke.cardmarket.prices:
            pk.average_sell_price = poke.cardmarket.prices.averageSellPrice
            pk.low_price = poke.cardmarket.prices.lowPrice
            pk.trend_price = poke.cardmarket.prices.trendPrice
            pk.suggested_price = poke.cardmarket.prices.suggestedPrice

        pk.save()

        if poke.abilities is not None:
            for ability in poke.abilities:
                # get the object
                pk.ability_set.add(self._ability_check(ability))

        if poke.images:
            try:
                self._handle_image(poke.images.large or poke.images.small,
                                   pk)
            except Exception as e:
                self.stderr.write("  * cannot add image {} {}".format(
                    e.__class__.__name__, str(e)))

    def _gen_ai_prompt(self, pk):
        """Create a GenAI object, given a database Pokemon object.

        :param pk: A database pokemon object
        :return: A string with a prompt.
        """
        prompt = GEN_AI_PROMPT.format(
                name=pk.name,
                supertype=pk.supertype or "None",
                subtypes=", ".join(pk.subtypes),
                hp=pk.hp,
                types=", ".join(pk.types),
                evolves_from=pk.evolves_from or "None",
                rules=pk.rules or "None",
                weakness="\n  * ".join(("%s: %s" % (k, v)
                                        for k, v in pk.weaknesses.items())),
                resistance="\n  * ".join(("%s: %s" % (k, v)
                                        for k, v in pk.resistances.items())),
                retreats=", ".join(pk.retreat_cost))
        response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt)
        return response.text


    def add_arguments(self, parser):
        parser.add_argument("-q", help="Query string",
                            default="")
        parser.add_argument("-u", "--update",
                            help="Update objects with new data",
                            action="store_true")
        parser.add_argument("-f", "--gen-ai-fill",
                            help="Fill empty fields with Generative AI",
                            action="store_true")
        parser.add_argument("--verbose", action="store_true")

    def handle(self, *args, **options):
        self.stdout.write("Query: {}".format(repr(options["q"])))
        self.stdout.write(("" if options["update"] else "NOT ")
                          + "Updating")
        if options["gen_ai_fill"]:
            if os.getenv("GEMINI_API_KEY") is None:
                raise CommandError("API key not set")
            self.client = genai.Client(
                    api_key=os.getenv("GEMINI_API_KEY"))
        for poke in Card.where(q=options["q"]):
            self.stdout.write("Adding {}".format(repr(poke.name)))
            pk = Pokemon.objects.filter(tcg_id__exact=poke.id)
            timeout = 0
            if pk:
                self.stderr.write("  * Already exists in DB")

                if not options["update"]:
                    continue

                pk = pk[0]
                self.stdout.write("  * Updating attributes")
                self._update_pokemon(pk, poke)
            else:
                pk = self._add_pokemon(poke)

            if options["gen_ai_fill"] and not pk.flavorText:
                self.stdout.write("  * Filling AI generated flavor text")
                while True:
                    try:
                        pk.flavorText = "\u2728 " + self._gen_ai_prompt(pk)
                    except genai.errors.ClientError:
                        if timeout == 0:
                            timeout = 10
                        else:
                            timeout = 2 * timeout
                        self.stdout.write("      * Request Timeout")
                        self.stdout.write("      * Wait %d seconds" % timeout)
                        time.sleep(timeout)
                    else:
                        timeout = 0
                        break

                pk.save()

            if options["verbose"]:
                self.stdout.write("  * Pokenon ID is: %s" % pk.pk)

