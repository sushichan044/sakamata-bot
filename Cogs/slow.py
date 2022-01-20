import os
from typing import Literal

from discord import Option

import discord
from discord import permissions
from discord.commands import message_command, slash_command
from discord.ext import commands

guild_id = int(os.environ['GUILD_ID'])
mod_role = int(os.environ['MOD_ROLE'])


class SlowMode(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @message_command(guild_ids=[guild_id], name='スローモード')
    @permissions.has_role(mod_role)
    async def _slow_mode(self, ctx, message: discord.Message):
        res = await self._slow(message.channel)
        if res:
            deal = 'ON'
        else:
            deal = 'OFF'
        await ctx.respond(f'スローモードを{deal}にしました。', ephemeral=True)
        return

    @slash_command(guild_ids=[guild_id], name='slow')
    @permissions.has_role(mod_role)
    async def _slash_slow(
        self,
        ctx,
        channel: Option(discord.TextChannel, 'Choose Channel'),
    ):
        res = await self._slow(channel)
        if res:
            deal = 'ON'
        else:
            deal = 'OFF'
        await ctx.respond(f'スローモードを{deal}にしました。', ephemeral=True)
        return

    async def _slow(self, channel):
        if channel.slowmode_delay == 0:
            delay = 60
            await channel.edit(slowmode_delay=delay)
            return True
        else:
            delay = 0
            await channel.edit(slowmode_delay=delay)
            return False


def setup(bot):
    return bot.add_cog(SlowMode(bot))
