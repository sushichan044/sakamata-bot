from curses.ascii import EM
from datetime import datetime, timedelta, timezone
from typing import Optional

from discord import Embed
from SongDBCore.model import Artist, History, No_Recent, Song, Stream

utc = timezone.utc
jst = timezone(timedelta(hours=9), "Asia/Tokyo")


class EmbedBuilder:
    def __init__(
        self,
        *,
        artist: Optional[Artist] = None,
        history: Optional[History] = None,
        no_recent: Optional[No_Recent] = None,
        song: Optional[Song] = None,
        songs: Optional[list[Song]] = None,
        stream: Optional[Stream] = None,
    ) -> None:
        pass

    def _start(self) -> Embed:
        embed = Embed(
            title="歌枠データベース",
            color=2105893,
        )
        return embed

    def _artist(self, songs: list[Song]) -> Embed:
        embed = Embed(
            title="検索結果(アーティスト検索)",
            color=2105893,
        )
        for num in range(len(songs)):
            delta = self.calc_delta(songs[num].latest.date)
            title = songs[num].title
            value = f"アーティスト: {songs[num].artist}\n最終歌唱:{songs[num].latest.date}({delta.days}日経過)"
            if songs[num].latest.note:
                value = value + "\n備考: " + songs[num].latest.note
            if songs[num].latest.url:
                value = value + f"\n[クリックして視聴]({songs[num].latest.url})"
            embed.add_field(name=title, value=value, inline=False)
        return embed

    def _stream(self, songs: list[Song]) -> Embed:
        embed = Embed(
            title="検索結果(URL検索)",
            color=2105893,
        )
        for num in range(len(songs)):
            delta = self.calc_delta(songs[num].latest.date)
            title = songs[num].title
            value = f"アーティスト: {songs[num].artist}\n最終歌唱日:{songs[num].latest.date}({str(delta.days)}日経過)"
            if songs[num].latest.note:
                value = value + "\n備考: " + songs[num].latest.note
            if songs[num].latest.url:
                value = value + f"\n[クリックして視聴]({songs[num].latest.url})"
            embed.add_field(name=title, value=value, inline=False)
        return embed

    def _rawsong(self, *, input: dict, songs: list[Song]) -> list[Embed]:
        s_method = [value for value in list(input.values()) if value]
        embeds = []
        embed = Embed(
            title="検索結果(複数条件検索)",
            color=2105893,
        )
        embed.add_field(
            name="検索条件",
            value="\n".join(s_method),
        )
        embeds.append(embed)
        for song in songs:
            delta = self.calc_delta(song.latest.date)
            embed = Embed(
                title=song.title,
                color=2105893,
            )
            embed.add_field(
                name="アーティスト",
                value=song.artist,
                inline=False,
            )
            embed.add_field(
                name="最終歌唱日",
                value=f"{song.latest.date}({str(delta.days)}日経過)",
                inline=False,
            )
            embed.add_field(
                name="視聴",
                value=f"[クリックして視聴]({song.latest.url})",
                inline=False,
            )
            embed.set_thumbnail(
                url=f"https://img.youtube.com/vi/{song.latest.raw_id}/maxresdefault.jpg"
            )
            if song.latest.note:
                embed.add_field(
                    name="備考",
                    value=song.latest.note,
                    inline=False,
                )
            embeds.append(embed)
        return embeds

    def _song(self, song_input: str, song: Song) -> Embed:
        embed = Embed(
            title=f"検索結果({song_input})",
            color=2105893,
        )
        delta = self.calc_delta(song.latest.date)
        embed.add_field(
            name="曲名",
            value=song.title,
        )
        embed.add_field(
            name="アーティスト",
            value=song.artist,
        )
        embed.add_field(
            name="最終歌唱日",
            value=f"{song.latest.date}({str(delta.days)}日経過)",
        )
        embed.set_image(
            url=f"https://img.youtube.com/vi/{song.latest.raw_id}/maxresdefault.jpg"
        )
        return embed

    def calc_delta(self, latest: str) -> timedelta:
        latest_dt = datetime.strptime(latest, "%Y/%m/%d").replace(tzinfo=jst)
        delta = datetime.now().astimezone(jst) - latest_dt
        return delta
