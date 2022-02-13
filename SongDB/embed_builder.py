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

    def _artist(self, artist: str, songs: list[Song]) -> Embed:
        embed = Embed(
            title=f"検索結果({artist})",
            color=2105893,
        )
        for num in range(len(songs)):
            sung = datetime.strptime(songs[num].latest.date, "%Y/%m/%d").replace(
                tzinfo=jst
            )
            delta = datetime.now().astimezone(jst) - sung
            title = songs[num].title
            value = f"アーティスト: {songs[num].artist}\n最終歌唱:{songs[num].latest.date}({delta.days}日経過)"
            if songs[num].latest.note:
                value = value + "\n備考: " + songs[num].latest.note
            value = value + f"\n[クリックして視聴]({songs[num].latest.url}"
            embed.add_field(name=title, value=value, inline=False)
        return embed
