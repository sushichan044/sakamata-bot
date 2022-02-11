from discord import Embed


class EmbedBuilder:
    def __init__(self) -> None:
        pass

    def _start(self) -> Embed:
        embed = Embed(
            title="歌枠データベース",
            color=2105893,
        )
        return embed
