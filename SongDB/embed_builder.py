from discord import Embed
from SongDBCore.model import Artist, History, No_Recent, Song, Stream
from typing import Optional


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

    def _artist(self, artist):
        pass

    def _songs(self, songs: list[Song]) -> Embed:
        embed = Embed(
            title="検索結果(アーティスト検索)",
            color=2105893,
        )
        for num in range(len(songs)):
            title = songs[num].title
            value = f"アーティスト: {songs[num].artist}\n最終歌唱:[{songs[num].latest.date}]({songs[num].latest.url})"
            if songs[num].latest.note:
                value = value + "\n備考: " + songs[num].latest.note
            embed.add_field(name=title, value=value, inline=False)
        return embed
