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
        except discord.HTTPException as e:
            print(f'これはテストです。\n{e.text}')
        else:
            await ctx.respond('ピン留めしました!', ephemeral=True)
            return
            '''
            if e == 'Maximum number of pins reached (50)':
                await ctx.respond('ピン留め数に上限に達しています。', ephemeral=True)
            elif e == 'Cannot execute action on a system message':
                await ctx.respond('システムメッセージをピン留めすることはできません。', ephemeral=True)
            else:
                await ctx.respond('予期せぬエラーが発生しました。', ephemeral=True)
                '''


def setup(bot):
    return bot.add_cog(ContextPin(bot))
