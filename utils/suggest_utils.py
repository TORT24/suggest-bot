import discord
from utils.type_texts import type_dict
from typing import List
from datetime import datetime
import os
import requests
from utils.exceptions import SuggestException


def request_osu_data(user_input: str = None, map_input: str = None) -> dict:
    url = os.getenv("BACKEND_URL") + "/api/OsuApi/handleosuinfo"
    params = dict(map=map_input, user=user_input)
    resp = requests.get(url=url, params=params)
    if resp.status_code == 200:
        return resp.json()
    raise SuggestException(f"{resp.status_code}: Something wrong with your inputs")


def get_additional_info_string(
    source_link: str, map_link: str = None, player_id: str = None, pp: str = None
) -> str:
    result: List[str] = []
    if pp:
        result.append(f"PP: {pp}")
    if source_link:
        result.append(f"[source]({source_link})")
    if player_id:
        result.append(f"[profile](https://osu.ppy.sh/u/{player_id})")
    if map_link:
        result.append(f"[beatmap]({map_link})")
    return " | ".join(result)


def get_suggest_embed(
    suggest_type: str,
    description: str,
    date: datetime,
    source_link: str,
    map_link: str = None,
    player: str = None,
    pp: str = None,
) -> discord.Embed:
    embed = discord.Embed(color=discord.Colour.blurple())
    player_id = None
    player_username = None
    embed.add_field(name="**Description:**", value=description, inline=False)
    embed.add_field(name="**Date:**", value=date.strftime("%d/%m/%Y"), inline=False)
    embed.add_field(name="**Type:**", value=type_dict[suggest_type], inline=False)
    if player or map_link:
        data = request_osu_data(user_input=player, map_input=map_link)
        if data["beatMapSetId"]:
            card_link = f"https://assets.ppy.sh/beatmaps/{data["beatMapSetId"]}/covers/card.jpg"
            embed.set_image(url=card_link)
        if data["userInfo"]:
            user_info = data["userInfo"]
            player_id = user_info["id"]
            player_username = user_info["username"]
            embed.set_author(name=player_username, icon_url=f"https://a.ppy.sh/{player_id}", url=f"https://osu.ppy.sh/u/{player_id}")
    embed.add_field(
        name="**Additional information:**",
        value=get_additional_info_string(
            source_link=source_link, map_link=map_link, player_id=player_id, pp=pp
        ),
        inline=False,
    )
    embed.set_footer(text="Thank you! :)")
    return embed
