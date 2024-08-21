import discord
from utils.type_texts import type_dict
from utils.suggest_dataclass import SuggestInfo
from utils.exceptions import SuggestException
from typing import List
from datetime import datetime, timedelta
import os
import requests

class BotUtils:
    def __init__(self):
        self.BACKEND_URL = os.getenv("BACKEND_URL")
        self.AUTH_CREDENTIALS = dict(
            UserName=os.getenv("API_LOGIN"), Password=os.getenv("API_PASS")
        )
        self.key_valid_untill: datetime = None
        self.access_key: str = None

    def refresh_token_if_needed(self):
        if self.key_valid_untill is None or datetime.now() > self.key_valid_untill:
            url = self.BACKEND_URL + "/api/Auth/login"
            resp = requests.post(url=url, params=self.AUTH_CREDENTIALS)
            if resp.status_code == 200:
                self.access_key = resp.json()["token"]
                self.key_valid_untill = datetime.now() + timedelta(days=1)
                return
            raise Exception(f"{resp.status_code}: {resp.reason}")

    def request_osu_data(self, user_input: str = None, map_input: str = None) -> dict:
        self.refresh_token_if_needed()
        url = self.BACKEND_URL + "/api/OsuApi/handleosuinfo"
        params = dict(map=map_input, user=user_input)
        headers = {"Authorization": f"Bearer {self.access_key}"}
        resp = requests.get(url=url, params=params, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        raise SuggestException(f"{resp.status_code}: Something wrong with your inputs")

    def get_additional_info_string(
        self, info: SuggestInfo, player_id: str = None
    ) -> str:
        result: list[str] = []
        if info.pp:
            result.append(f"PP: {info.pp}")
        if info.source_link:
            result.append(f"[source]({info.source_link})")
        if player_id:
            result.append(f"[profile](https://osu.ppy.sh/u/{player_id})")
        if info.map_link:
            result.append(f"[beatmap]({info.map_link})")
        return " | ".join(result)

    def upsert_data_to_coda(
        self,
        suggest_info: SuggestInfo,
        made_by: str,
        player_id: str = None,
        player_username: str = None,
    ):
        self.refresh_token_if_needed()
        url = self.BACKEND_URL + "/api/Coda/postSuggestionToCoda"
        params = dict(
            Description=suggest_info.description,
            Type=suggest_info.suggest_type,
            SourceLink=suggest_info.source_link,
            Date=suggest_info.date.strftime("%m/%d/%Y, %H:%M:%S"),
            MapLink=suggest_info.map_link,
            Player=player_username,
            PlayerLink=player_id,
            Pp=suggest_info.pp,
            MadeBy=made_by,
        )
        headers = {"Authorization": f"Bearer {self.access_key}"}
        resp = requests.post(url=url, params=params, headers=headers)
        if resp.status_code == 200:
            return
        raise SuggestException(f"{resp.status_code}: Something wrong with your inputs")

    # i was too lazy to rewrite this shit to make 2 proper methods. sorry, maybe later tho
    def get_suggest_embed_and_upsert_coda(
        self, info: SuggestInfo, author: str
    ) -> discord.Embed:
        embed = discord.Embed(color=discord.Colour.blurple())
        player_id = None
        player_username = None

        embed.add_field(name="**Description:**", value=info.description, inline=False)
        embed.add_field(
            name="**Date:**", value=info.date.strftime("%d/%m/%Y"), inline=False
        )
        embed.add_field(
            name="**Type:**", value=type_dict[info.suggest_type], inline=False
        )

        if info.player or info.map_link:
            data = self.request_osu_data(
                user_input=info.player, map_input=info.map_link
            )
            if data.get("beatMapSetId"):
                card_link = f"https://assets.ppy.sh/beatmaps/{data['beatMapSetId']}/covers/card.jpg"
                embed.set_image(url=card_link)
            if data.get("userInfo"):
                user_info = data["userInfo"]
                player_id = user_info["id"]
                player_username = user_info["username"]
                embed.set_author(
                    name=player_username,
                    icon_url=f"https://a.ppy.sh/{player_id}",
                    url=f"https://osu.ppy.sh/u/{player_id}",
                )

        embed.add_field(
            name="**Additional information:**",
            value=self.get_additional_info_string(info=info, player_id=player_id),
            inline=False,
        )
        embed.set_footer(text="Thank you! :)")
        self.upsert_data_to_coda(
            suggest_info=info,
            made_by=author,
            player_id=player_id,
            player_username=player_username,
        )
        return embed
