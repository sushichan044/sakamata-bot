import os

import discord
from discord import Option
from discord.commands import message_command, slash_command
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

guild_id = int(os.environ["GUILD_ID"])


class SlowMode(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @message_command(guild_ids=[guild_id], name="スローモード切替")
    async def _slow_mode(self, ctx, message: discord.Message):
        res = await self._slow(message.channel)
        if res:
            deal = "ON"
        else:
            deal = "OFF"
        await ctx.respond(f"スローモードを{deal}にしました。", ephemeral=True)
        return

    @slash_command(guild_ids=[guild_id], name="slow")
    async def _slash_slow(
        self,
        ctx,
        channel: Option(discord.TextChannel, "対象のチャンネルを選択してください。"),
    ):
        """指定したチャンネルのスローモードを切り替えます。"""
        result = await self._slow(channel)
        if result:
            deal = "ON"
        else:
            deal = "OFF"
        await ctx.respond(f"スローモードを{deal}にしました。", ephemeral=True)
        return

    async def _slow(self, channel):
        if channel.slowmode_delay == 0:
            delay = 30
            await channel.edit(slowmode_delay=delay)
            return True
        else:
            delay = 0
            await channel.edit(slowmode_delay=delay)
            return False


def setup(bot):
    return bot.add_cog(SlowMode(bot))
