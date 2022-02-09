from discord import Embed
from discord.utils import utcnow
from datetime import timezone, timedelta

jst = timezone(timedelta(hours=9), "Asia/Tokyo")


def _survey_embed(text: str, user: str = None) -> Embed:
    now = utcnow().astimezone(jst).strftime("%Y/%m/%d %H:%M:%S")
    embed = Embed(
        title="フィードバック",
        description=text,
        color=15767485,
    )
    embed.set_footer(text=now)
    if user:
        embed.add_field(name="アカウント", value=user)
    return embed
