import os

import discord
from discord.ext import commands

mod_role = int(os.environ["MOD_ROLE"])
admin_role = int(os.environ["ADMIN_ROLE"])
server_member_role = int(os.environ["SERVER_MEMBER_ROLE"])


class Utils_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="private")
    @commands.has_role(admin_role)
    async def _private(self, ctx):
        role = ctx.guild.get_role(server_member_role)
        channels = sorted(
            [channel for channel in ctx.guild.channels if channel.category],
            key=lambda channel: channel.position,
        )
        for channel in channels:
            result = channel.permissions_for(role).view_channel
            print(channel.name, result)
        return


def setup(bot):
    return bot.add_cog(Utils_Command(bot))
