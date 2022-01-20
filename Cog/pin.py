import os

import discord
from discord import permissions
from discord.commands import message_command
from discord.ext import commands

guild_id = int(os.environ['GUILD_ID'])
server_member_role = int(os.environ['SERVER_MEMBER_ROLE'])


class ContextPin(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @message_command(guild_ids=[guild_id], name='ピン留め')
    @permissions.has_role(server_member_role)
    async def _pin(self, ctx, message: discord.Message):
        try:
            await message.pin()
            await ctx.respond('ピン留めしました!', ephemeral=True)
            return
        except discord.HTTPException as e:
            print(e.code)
            await ctx.respond('システムメッセージをピン留めすることはできません。', ephemeral=True)
            return



def setup(bot):
    return bot.add_cog(ContextPin(bot))
