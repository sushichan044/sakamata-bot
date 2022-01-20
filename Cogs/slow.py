import os
from typing import Literal

from discord import Option

import discord
from discord import permissions
from discord.commands import message_command, slash_command
from discord.ext import commands

guild_id = int(os.environ['GUILD_ID'])
server_member_role = int(os.environ['SERVER_MEMBER_ROLE'])


class SlowMode(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @message_command(guild_ids=[guild_id], name='スローモード')
    @permissions.has_role(server_member_role)
    async def _slow_mode(self, ctx, message: discord.Message):
        await message.channel.edit(slowmode_delay=60)
        await ctx.respond('スローモードをONにしました。', ephemeral=True)
        return

    @message_command(guild_ids=[guild_id], name='スローモード解除')
    @permissions.has_role(server_member_role)
    async def _un_slow_mode(self, ctx, message: discord.Message):
        await message.channel.edit(slowmode_delay=0)
        await ctx.respond('スローモードをOFFにしました。', ephemeral=True)
        return

    @slash_command(guild_ids=[guild_id], name='slow')
    @permissions.has_role(server_member_role)
    async def _slash_slow(
        self,
        ctx,
        channel: Option(discord.TextChannel, 'Choose Channel'),
        switch: Option(str, 'Choose ON/OFF', choices=['ON,OFF'], default='ON')
    ):
        if self.on_or_off(switch):
            delay = 60,
            deal = 'ON'
        else:
            delay = 0,
            deal = 'OFF'
        await channel.edit(slowmode_delay=delay)
        await ctx.respond(f'スローモードを{deal}にしました。', ephemeral=True)

    def on_or_off(self, switch: Literal['ON', 'OFF']) -> bool:
        if switch == 'ON':
            return True
        else:
            return False


def setup(bot):
    return bot.add_cog(SlowMode(bot))
