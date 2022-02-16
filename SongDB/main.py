import os

import discord
from Core.error import InteractionError
from discord import ApplicationContext
from discord.commands import slash_command
from discord.ext import commands
from SongDBCore import SongDBClient

from SongDB.embed_builder import EmbedBuilder as EB
from SongDB.match import match_url
from SongDB.many_page import PagePage


req_url = "https://script.google.com/macros/s/AKfycbyYXAOWYDQRe1___cQyPTZkKGC-BZfbpF4ksEpXIvJpAHPH8CO-I0yu0fNqpNCvT7M/exec"

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
        embed = EB()._start()
        view = ProdDropdownView()
        await ctx.interaction.followup.send(embed=embed, view=view, ephemeral=True)
        return


class ProdDropdown(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(
                label="データベース検索",
                value="multi",
                description="曲名、アーティスト名、配信URLなどの条件で検索",
                default=False,
            ),
            discord.SelectOption(
                label="最近歌われていない曲(利用不可)",
                value="no_recent",
                description="最近歌われていない曲の一覧を検索できます。",
                default=False,
            ),
        ]
        super().__init__(
            placeholder="検索方式を指定してください。", min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        if self.values[0] == "multi":
            await interaction.response.send_modal(modal=ProdSearch())
            return
        elif self.values[0] == "no_recent":
            await interaction.response.send_message(content="準備中です。", ephemeral=True)
            return
        else:
            raise InteractionError(interaction=interaction, cls=self)


class ProdSearch(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="歌枠データベース")
        self.add_item(
            discord.ui.InputText(
                label="検索したい曲名を入力してください。",
                style=discord.InputTextStyle.short,
                required=False,
                row=0,
                placeholder="曲名",
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="検索したいアーティスト名や作曲者名を入力してください。",
                style=discord.InputTextStyle.short,
                required=False,
                row=1,
                placeholder="アーティスト名/作曲者名",
            ),
        )
        self.add_item(
            discord.ui.InputText(
                label="検索したい歌枠のURLを入力してください。",
                style=discord.InputTextStyle.short,
                required=False,
                row=2,
                placeholder="youtube.comとyoutu.beに対応しています",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        # await interaction.response.defer(ephemeral=True)
        if self.children[2].value:
            id = match_url(self.children[2].value)
            if not id:
                print("Invalid url inputted.")
                await interaction.response.send_message(
                    content="対応していないURLが入力されました。", ephemeral=True
                )
                return
        client = SongDBClient(url=req_url)
        d = {
            "song_name": self.children[0].value,
            "artist_name": self.children[1].value,
            "stream_id": self.children[2].value,
        }
        if not any(d.values()):
            await interaction.response.send_message(
                content="一つ以上の検索条件を指定してください。", ephemeral=True
            )
            return
        songs = await client.multi_search(**d)
        if songs.songs == []:  # no result found
            embed = EB()._empty(input=d)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        embeds = EB()._rawsong(input=d, songs=songs.songs)
        await PagePage(embeds=embeds)._send(interaction)
        return


class ProdDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ProdDropdown())


def setup(bot):
    return bot.add_cog(SongDB(bot))
