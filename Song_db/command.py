import os

import discord
import requests
from discord import ApplicationContext
from discord.commands import permissions, slash_command
from discord.ext import commands
from discord.ui import InputText, Modal

from . import embed_builder as EB
from .match import match_url

hook_url = ""

guild_id = int(os.environ["GUILD_ID"])

# search_option:
# 1: 曲で検索
# 2: 歌枠で検索


class SongDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[guild_id], name="song")
    async def _song(self, ctx: ApplicationContext):
        await ctx.interaction.response.defer()
        embed = EB._start()
        view = SearchDropdownView()
        await ctx.interaction.followup.send(embed=embed, view=view)
        return


class SearchDropdown(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(
                label="曲で検索",
                value="song",
                description="曲を指定して歌唱回数などのデータを取得できます。",
                default=False,
            ),
            discord.SelectOption(
                label="歌枠で検索",
                value="url",
                description="歌枠を指定することで曲などのデータを取得できます。",
                default=False,
            ),
        ]
        super().__init__(
            placeholder="検索方式を指定してください。", min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "url":
            await interaction.response.send_modal(SearchByStream())
            return
        else:
            await interaction.response.send_message("Not Available now!")
            return


class SearchByStream(Modal):
    def __init__(self) -> None:
        super().__init__(title="歌枠データベース")
        self.add_item(
            InputText(
                label="検索したい歌枠のURLを入力してください。",
                style=discord.InputTextStyle.short,
                required=True,
                row=0,
                placeholder="youtube.comとyoutu.beに対応しています",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        if not self.children[0].value:
            print("SearchByStream: null is inputted")
            await interaction.response.send_message(
                content="予期せぬエラーが発生しました。\n管理者に問い合わせてください。", ephemeral=True
            )
            return
        else:
            # match pattern and output v_id
            id = match_url(self.children[0].value)
            print(id)
            await interaction.response.send_message(content=id)
            return


class SearchDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SearchDropdown())


def setup(bot):
    return bot.add_cog(SongDB(bot))
