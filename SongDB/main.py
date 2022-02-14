import os

import discord
from Core.error import InteractionError
from discord import ApplicationContext
from discord.commands import slash_command
from discord.ext import commands
from SongDBCore import SongDBClient
from SongDBCore.model import Artist, Song, History, No_Recent, Stream

from SongDB.embed_builder import EmbedBuilder as EB
from SongDB.match import match_url


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
        embed = EB()._start()
        view = SearchDropdownView()
        await ctx.interaction.followup.send(embed=embed, view=view, ephemeral=True)
        return


class SearchDropdown(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(
                label="曲名で検索",
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
        self.disabled = True
        if self.values[0] == "song":
            await interaction.response.send_modal(modal=SearchBySong())
            return
        elif self.values[0] == "artist":
            await interaction.response.send_modal(modal=SearchByArtist())
            return
        elif self.values[0] == "url":
            await interaction.response.send_modal(modal=SearchByStream())
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
        await interaction.response.defer(ephemeral=True)
        client = SongDBClient()
        song = await client.search_song(song_name=self.children[0].value)
        if not song:  # no result found
            await interaction.response.send_message(
                content="検索結果は0件でした。", ephemeral=True
            )
            return
        else:
            print(song)
            embeds = EB()._rawsong(song_input=self.children[0].value, songs=song.songs)
            await interaction.response.send_message(embeds=embeds, ephemeral=False)
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
        await interaction.response.defer(ephemeral=True)
        artist_name = self.children[0].value
        client = SongDBClient()
        artist: Artist = await client.search_artist(artist_name=artist_name)
        if not artist:  # no result found
            await interaction.response.send_message(
                content="検索結果は0件でした。", ephemeral=True
            )
            return
        else:
            embed = EB()._artist(songs=artist.songs)
            await interaction.response.send_message(embed=embed, ephemeral=False)
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
        await interaction.response.defer(ephemeral=True)
        # match pattern and output v_id
        id = match_url(self.children[0].value)
        if not id:
            print("Invalid url inputted.")
            await interaction.response.send_message(
                content="対応していないURLが入力されました。", ephemeral=True
            )
            return
        else:
            print(id)
            client = SongDBClient()
            stream = await client.search_stream(stream_id=id)
        if not stream:  # no result found
            await interaction.response.send_message(
                content="検索結果は0件でした。", ephemeral=True
            )
            return
        else:
            embed = EB()._stream(songs=stream.songs)
            await interaction.response.send_message(embed=embed, ephemeral=False)
            return


class SearchDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SearchDropdown())


def setup(bot):
    return bot.add_cog(SongDB(bot))
