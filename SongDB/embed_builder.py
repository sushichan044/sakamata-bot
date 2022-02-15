from curses.ascii import EM
from datetime import datetime, timedelta, timezone
from typing import Optional
from unicodedata import name

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

    def _query(self, *, input: dict) -> list[str]:
        converter_dict = {
            "song_name": "曲名: ",
            "artist_name": "アーティスト名: ",
            "stream_id": "配信ID: ",
        }
        s_method = [converter_dict[k] + v for k, v in input.items() if v]
        return s_method

    def _empty(self, *, input: dict) -> Embed:
        embed = Embed(
            title="検索結果",
            description="検索結果は0件でした。",
            color=2105893,
        )
        embed.add_field(
            name="検索条件",
            value="\n".join(self._query(input=input)),
        )
        return embed

    def _rawsong(self, *, input: dict, songs: list[Song]) -> list[Embed]:
        embeds = []
        embed = Embed(
            title="検索結果",
            description=f"検索結果は{len(songs)}件でした。",
            color=2105893,
        )
        embed.add_field(
            name="検索条件",
            value="\n".join(self._query(input=input)),
        )
        embeds.append(embed)
        if songs != []:
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
                if song.latest.url:
                    embed.add_field(
                        name="視聴",
                        value=f"[クリックして視聴]({song.latest.url})",
                        inline=False,
                    )
                    embed.set_thumbnail(
                        url=f"https://img.youtube.com/vi/{song.latest.raw_id}/maxresdefault.jpg"
                    )
                else:
                    embed.add_field(
                        name="視聴不可",
                        value="No archive",
                        inline=False,
                    )
                if song.latest.note:
                    embed.add_field(
                        name="備考",
                        value=song.latest.note,
                        inline=False,
                    )
                if not song.latest.url:
                    availables = [history for history in song.history if history.url]
                    if availables != []:
                        embed.add_field(
                            name="視聴(二番目に新しいもの)",
                            value=f"[クリックして視聴]({availables[0].url})",
                            inline=False,
                        )
                        embed.set_thumbnail(
                            url=f"https://img.youtube.com/vi/{availables[0].raw_id}/maxresdefault.jpg"
                        )
                        if availables[0].note:
                            embed.add_field(
                                name="備考",
                                value=availables[0].note,
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
