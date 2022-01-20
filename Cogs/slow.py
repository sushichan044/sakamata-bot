import os

import discord
from discord import permissions
from discord.commands import message_command
from discord.ext import commands

guild_id = int(os.environ['GUILD_ID'])
server_member_role = int(os.environ['SERVER_MEMBER_ROLE'])


class SlowMode(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @message_command(guild_ids=[guild_id], name='スローモード')
    @permissions.has_role(server_member_role)
    async def _slow_mode(self, ctx, message: discord.Message):
        channel = self.bot.get_channel(message.channel)
        await channel.edit(slowmode_delay=60)
        await ctx.respond('スローモードをONにしました。', ephemeral=True)
        return

    @message_command(guild_ids=[guild_id], name='スローモード解除')
    @permissions.has_role(server_member_role)
    async def _un_slow_mode(self, ctx, message: discord.Message):
        channel = self.bot.get_channel(message.channel)
        await channel.edit(slowmode_delay=0)
        await ctx.respond('スローモードをOFFにしました。', ephemeral=True)
        return


def setup(bot):
    return bot.add_cog(SlowMode(bot))
