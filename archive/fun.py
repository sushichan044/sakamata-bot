import os

import discord
import requests
from bs4 import BeautifulSoup as BS
from discord.commands import slash_command, permissions
from discord.ext import commands
import random

guild_id = int(os.environ["GUILD_ID"])
server_member_role = int(os.environ["SERVER_MEMBER_ROLE"])


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[guild_id], name="dub")
    @permissions.has_role(server_member_role)
    async def _shindan(self, ctx):
        name = ctx.author.display_name
        nickname = self._get_shindan(name)
        await ctx.respond(f"今日の二つ名は...\n||{nickname}||", ephemeral=True)
        return

    def _get_shindan(self, name) -> str:
        url = "https://shindanmaker.com/512272"
        session = requests.session()
        s = session.get(url)
        if s.status_code != 200:
            raise FileNotFoundError(s.status_code)
        source = BS(s.text)
        params = {i["name"]: i["value"] for i in source.find_all("input")[1:4]}
        params["shindanName"] = str(random.random()) if name is None else name
        login = session.post(url, data=params)
        return BS(login.text).find("span", id="shindanResult").text


def setup(bot):
    return bot.add_cog(Fun(bot))
