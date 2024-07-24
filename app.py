import discord
import logging
from discord import option
from dotenv import load_dotenv
import os
from dateutil import parser
import validators
from utils.suggest_utils import get_suggest_embed
from utils.type_texts import type_dict
from utils.exceptions import SuggestException


load_dotenv()

KEY = os.getenv("KEY")
GUILDS = os.getenv("GUILDS").split(" ")
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)
bot = discord.Bot(debug_guilds=GUILDS)


@bot.slash_command(description="very important command")
@option("name", description="who pomifsia?", default="<@284617027593961475>")
async def pomifsia(ctx: discord.ApplicationContext, name: str):
    await ctx.respond(f"{name} pomifsia ({name} помыфся)")
    logger.info(f"{name} помывся/pomifsia")


@bot.slash_command(description="Suggest new thing")
@option(
    "type",
    description='What type of "thing" it is?',
    choices=list(type_dict.keys()),
)
@option(
    "description",
    description="Provide short/long(better not very long) description",
    max_length=1000,
)
@option(
    "date",
    description="Provide date. Discord pls add date option",
    max_length=11,
)
@option(
    "source_link",
    description="Link to any source like twitter, reddit ect.",
    max_length=256,
)
@option(
    "map_link",
    description="[OPTIONAL] Link to the map if that's a score",
    max_length=256,
    required=False,
)
@option(
    "player",
    description="[OPTIONAL] Player nickname or link",
    max_length=256,
    required=False,
)
@option("pp", description="[OPTIONAL] ikr", required=False, max_length=5)
async def suggest(
    ctx: discord.ApplicationContext,
    type: str,
    description: str,
    date: str,
    source_link: str,
    map_link: str,
    player: str,
    pp: str,
):
    try:
        if source_link and not validators.url(source_link):
            raise SuggestException("Provide valid source link!")
        if map_link and not validators.url(map_link):
            raise SuggestException("Provide valid map link!")
        await ctx.respond(
            f"🤙 New Suggestion made by: {ctx.author.name}",
            embed=get_suggest_embed(
                suggest_type=type,
                description=description,
                date=parser.parse(date),
                source_link=source_link,
                map_link=map_link,
                player=player,
                pp=pp,
            ),
        )
        logger.info(f"{ctx.author.name}(id: {ctx.author.id}) made his suggestion")
    except SuggestException as sex:
        await ctx.respond(str(sex))
    except Exception as ex:
        await ctx.respond("Something else went wrong!")
        logger.exception(ex)


logger.info("Yo!")
bot.run(KEY)
