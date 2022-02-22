from datetime import datetime, timezone
import os

import discord
from discord import Message
from discord.ext import commands

admin_role = int(os.environ["ADMIN_ROLE"])


class AntiSpam(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def _anti_rapid_post(self, message: Message):
        if message.channel.type == discord.DMChannel:
            return
        if message.author.id == self.bot.user.id:
            return
        if admin_role in [r.id for r in message.author.roles]:
            return

        def check_rapid_post(m: Message):
            return (
                m.author == message.author
                and (
                    datetime.utcnow().astimezone(timezone.utc)
                    - m.created_at.astimezone(timezone.utc)
                ).seconds
                < 15
            )

        if (
            len(list(filter(lambda m: check_rapid_post(m), self.bot.cached_messages)))
            >= 5
        ):
            print("連投を検知")
            return  # alert 連投


def setup(bot):
    return bot.add_cog(AntiSpam(bot))
