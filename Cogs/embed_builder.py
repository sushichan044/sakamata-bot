from unicodedata import name
from discord import Embed


def _contact_embed() -> Embed:
    embed = Embed(
        title="スレッドが作成されました。",
        description="お問い合わせありがとうございます。\n下のスレッドリンクからスレッドへ移動して、\n内容の投稿をお願いします。",
        color=2105893,
    )
    embed.add_field(name="スレッド", value="Temp")
    return embed
