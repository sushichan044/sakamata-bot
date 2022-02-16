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

    def calc_delta(self, latest: str) -> timedelta:
        latest_dt = datetime.strptime(latest, "%Y/%m/%d").replace(tzinfo=jst)
        delta = datetime.now().astimezone(jst) - latest_dt
        return delta

    def _query(self, *, input: dict) -> list[str]:
        converter_dict = {
            "song_name": "曲名: ",
            "artist_name": "アーティスト名: ",
            "stream_id": "配信ID: ",
        }
        s_method = [converter_dict[k] + v for k, v in input.items() if v]
        return s_method

    def _many(self, *, input: dict, songs: list[Song]) -> str:
        s_texts = []
        nl = "\n"
        dnl = "\n\n"
        for num in range(len(songs)):
            song = songs[num]
            delta = self.calc_delta(song.latest.date)
            if not song.latest.url:
                availables = [history for history in song.history if history.url]
                if availables != []:
                    _watch = (
                        f"最新のデータの配信にはアーカイブが存在しません。{nl}二番目に新しいものを視聴({availables[0].url})"
                    )
                _watch = "アーカイブが存在しません。"
            _watch = f"視聴({song.latest.url})"
            _text = f"""
            [{str(num+1)}]{nl}
            曲名: {song.title}{nl}
            アーティスト名: {song.artist}{nl}
            最終歌唱日: {song.latest.date}({str(delta.days)}日経過){nl}
            {_watch}{nl}
            """
            s_texts.append(_text)
        text = f"""
        【歌枠データベース照会結果】{nl}
        検索結果が10件を超えたため簡易表示に切り替えます。{nl}{nl}
        検索条件:{nl}
        {nl.join(self._query(input=input))}{nl}{nl}
        {dnl.join(s_texts)}"""
        print(len(text))
        return text
