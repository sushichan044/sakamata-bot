import os
from datetime import datetime, timedelta

import discord
from discord import Option, permissions
from discord.commands import slash_command
from discord.ext import commands

guild_id = int(os.environ['GUILD_ID'])
server_member_role = int(os.environ['SERVER_MEMBER_ROLE'])


class Tool(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[guild_id], name='dakuten')
    @permissions.has_role(server_member_role)
    async def _dakuten(
        self,
        ctx,
        text: Option(str, '濁点をつけるテキストを入力してください。'),
    ):
        """濁点を付けて自慢しよう！"""
        out_text = ''.join([text[num] + '゛' for num in range(len(text))])
        await ctx.respond(out_text, ephemeral=True)
        return

    @slash_command(guild_ids=[guild_id], name='timestamp')
    @permissions.has_role(server_member_role)
    async def _make_timestamp(self,
                              ctx: discord.ApplicationContext,
                              date_str: Option(str, '日付を入力してください。(例:20220518)'),
                              time_str: Option(
                                  str, '時間を入力してください。(例:1234)', default='0000')
                              ):
        await ctx.defer(ephemeral=True)
        date = datetime.strptime(date_str, '%Y%m%d')
        delta = timedelta(
            hours=int(time_str[0:2] - 9), minutes=int(time_str[2:4]))
        timestamp = discord.utils.format_dt(date + delta, style='f')
        raw_timestamp = discord.utils.escape_markdown(
            timestamp, as_needed=True)
        await ctx.interaction.followup.send(timestamp, ephemeral=True)
        await ctx.interaction.followup.send(raw_timestamp, ephemeral=True)
        return


def setup(bot):
    return bot.add_cog(Tool(bot))
