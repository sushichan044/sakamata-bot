import os
import asyncio

from discord import Option

import discord
from discord.commands import message_command, slash_command, permissions
from discord.ext import commands

guild_id = int(os.environ["GUILD_ID"])
mod_role = int(os.environ["MOD_ROLE"])
admin_role = int(os.environ["ADMIN_ROLE"])


class Slow(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.group(name="slow-all")
    @commands.has_role(admin_role)
    @commands.guild_only()
    async def slow_all(self, ctx: commands.Context):

        if ctx.invoked_subcommand is None:
            await ctx.reply(content="このコマンドはモード指定が必要です。\nONまたはOFFでモードを指定してください。")
            return

    @slow_all.command()
    async def on(self, ctx: commands.Context):
        channels: list[discord.TextChannel] = [
            ch
            for ch in await ctx.guild.fetch_channels()
            if type(ch) == discord.TextChannel
        ]
        for channel in channels:
            try:
                await channel.edit(slowmode_delay=60)
            except Exception as e:
                print(e)
            else:
                print(f"slowed down [{channel.name}]")
            await asyncio.sleep(delay=1)
        await ctx.reply(content="全チャンネルのスローモードをONにしました。")
        return

    @slow_all.command()
    async def off(self, ctx: commands.Context):
        channels: list[discord.TextChannel] = [
            ch
            for ch in await ctx.guild.fetch_channels()
            if ch.type == discord.TextChannel
        ]
        for channel in channels:
            try:
                await channel.edit(slowmode_delay=0)
            except Exception as e:
                print(e)
            else:
                print(f"slowed down [{channel.name}]")
            await asyncio.sleep(delay=1)
        await ctx.reply(content="全チャンネルのスローモードをOFFにしました。")
        return

    @message_command(guild_ids=[guild_id], name="スローモード切替")
    @permissions.has_role(mod_role)
    async def _slow_mode(self, ctx, message: discord.Message):
        res = await self._slow(message.channel)
        if res:
            deal = "ON"
        else:
            deal = "OFF"
        await ctx.respond(f"スローモードを{deal}にしました。", ephemeral=True)
        return

    @slash_command(guild_ids=[guild_id], name="slow")
    @permissions.has_role(mod_role)
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
    return bot.add_cog(Slow(bot))
