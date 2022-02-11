import os

import discord
import requests
from Core.error import InteractionError
from discord import ApplicationContext
from discord.commands import permissions, slash_command
from discord.ext import commands

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
        await ctx.interaction.response.defer(ephemeral=True)
        embed = EB._start()
        view = SearchDropdownView()
        await ctx.interaction.followup.send(embed=embed, view=view, ephemeral=True)
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
                label="アーティスト名/作曲者名で検索",
                value="artist",
                description="アーティスト名や作曲者名から曲を検索できます。",
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

    async def callback(self, interaction: discord.Interaction) -> None:
        self.disabled = True
        if self.values[0] == "song":
            modal = SearchBySong()
        elif self.values[0] == "artist":
            modal = SearchByArtist()
        else:
            modal = SearchByStream()
        if modal:
            await interaction.response.send_modal(modal)
            return
        else:
            raise InteractionError(interaction=interaction, err_cls=self)


class SearchBySong(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="歌枠データベース")
        self.add_item(
            discord.ui.InputText(
                label="検索したい曲名を入力してください。",
                style=discord.InputTextStyle.short,
                required=True,
                row=0,
                placeholder="曲名",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        song_name = self.children[0].value
        await interaction.response.defer(ephemeral=True)
        await _sender(interaction=interaction, content="Coming soon", ephemeral=True)
        return


class SearchByArtist(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="歌枠データベース")
        self.add_item(
            discord.ui.InputText(
                label="検索したいアーティスト名や作曲者名を入力してください。",
                style=discord.InputTextStyle.short,
                required=True,
                row=0,
                placeholder="アーティスト名/作曲者名",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        artist_name = self.children[0].value
        await interaction.response.defer(ephemeral=True)
        await _sender(interaction=interaction, content="Coming soon", ephemeral=True)
        return


class SearchByStream(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="歌枠データベース")
        self.add_item(
            discord.ui.InputText(
                label="検索したい歌枠のURLを入力してください。",
                style=discord.InputTextStyle.short,
                required=True,
                row=0,
                placeholder="youtube.comとyoutu.beに対応しています",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        # match pattern and output v_id
        id = match_url(self.children[0].value)
        if id:
            print(id)
            await interaction.response.send_message(content=id)
            return
        else:
            print("Invalid url inputted.")
            await interaction.response.send_message(
                content="対応していないURLが入力されました。", ephemeral=True
            )
            return


class SearchDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SearchDropdown())


async def _sender(interaction: discord.Interaction, **kwarg):
    if interaction.response.is_done():
        await interaction.followup.send(**kwarg)
        return
    else:
        await interaction.response.send_message(**kwarg)
        return


def setup(bot):
    return bot.add_cog(SongDB(bot))
