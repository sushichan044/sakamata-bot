import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import discord
from discord import Message
from discord.ext import commands

admin_role = int(os.environ["ADMIN_ROLE"])
security_channel = int(os.environ["SECURITY_CHANNEL"])


class AntiSpam(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def _anti_rapid_post(self, message: Message):
        if message.channel.type == discord.DMChannel:
            return
        if message.author.id == self.bot.user.id or message.author.bot:
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
            target = message.author
            channel = await message.guild.fetch_channel(security_channel)
            print("連投を検知")
            await channel.send(content="連投を検知しました。", view=ExecView(target=target))
            return  # alert 連投


class ExecView(discord.ui.View):
    def __init__(self, *, target: discord.Member):
        super().__init__(timeout=None)
        self.add_item(TimeoutButton(target=target))


class TimeoutButton(discord.ui.Button):
    def __init__(self, *, target: Optional[discord.Member] = None, **kwargs):
        super().__init__(
            style=discord.ButtonStyle.danger,
            label="タイムアウト",
            custom_id="anti_spam_timeout",
            row=0,
            **kwargs,
        )
        self.target = target

    async def callback(self, interaction: discord.Interaction):
        await self.target.timeout_for(
            duration=timedelta(days=1), reason="Anti-Spam(Rapid post)"
        )
        view = discord.ui.View(timeout=None)
        view.add_item(Dis_Timeout())
        await interaction.message.edit(content=interaction.message.content, view=view)
        await interaction.response.send_message(
            content=f"{self.target.display_name} (ID:{self.target.id})を\n24時間タイムアウトしました。"
        )
        return


class Dis_Timeout(TimeoutButton):
    def __init__(self):
        super().__init__(disabled=True)


def setup(bot):
    return bot.add_cog(AntiSpam(bot))
