import os
from datetime import timedelta, timezone

import discord
from discord.ext import commands

thread_log_channel = int(os.environ['THREAD_LOG_CHANNEL'])
jst = timezone(timedelta(hours=9), 'Asia/Tokyo')
mod_role = int(os.environ['MOD_ROLE'])


class Thread(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name='on_thread_join')
    async def detect_thread(self, thread):
        thread_member_list = await thread.fetch_members()
        if self.bot.user.id in [x.id for x in thread_member_list]:
            return
        else:
            channel = self.bot.get_channel(thread_log_channel)
            embed = await self.compose_thread_create_log(thread)
            await channel.send(embed=embed)
            return

    @commands.Cog.listener(name='on_thread_update')
    async def detect_archive(self, before, after):
        if after.locked and not before.locked:
            return
        elif after.archived and not before.archived:
            await after.edit(archived=False)
            return
        else:
            return

    @commands.command(name='thread_board')
    @commands.has_role(mod_role)
    async def _thread(self, ctx):
        guild_channels = await ctx.guild.fetch_channels
        channels = [
            channel for channel in guild_channels if channel.category.name == '🎮ゲームセンター/GAMING🎮']
        sort_channels = sorted(channels, key=lambda channel: channel.position)
        print(sort_channels)
        thread_dic = {}
        threads = [thread for thread in ctx.guild.threads if thread.invitable and not thread.locked and thread.parent.category.name == '🎮ゲームセンター/GAMING🎮']
        for thread in threads:
            thread_dic[thread] = thread.parent.position
        """
        thread_dic:
        {thread:pos,
        thread:pos,
        ...}
        """
        # sort_thread = sorted(thread_dic.items(), key=lambda i: i[1])
        for channel in channels:
            thread_board = []
            thread_board.append(channel.mention)
            child_thread = [
                thread for thread, parent in thread_dic.items() if parent == channel.position]
            # for thread in child_thread:

        pass

    async def compose_thread_create_log(self, thread):
        embed = discord.Embed(
            title='スレッドが作成されました。',
            url='',
            color=3447003,
            description='',
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(
            name=thread.owner.display_name,
            icon_url=thread.owner.display_avatar.url,
        )
        embed.add_field(
            name='作成元チャンネル',
            value=f'{thread.parent.mention}'
        )
        embed.add_field(
            name='作成スレッド',
            value=f'{thread.mention}'
        )
        embed.add_field(
            name='作成者',
            value=f'{thread.owner.mention}'
        )
        embed.add_field(
            name='作成日時',
            value=f'{discord.utils.utcnow().astimezone(jst):%Y/%m/%d %H:%M:%S}'
        )
        return embed


def setup(bot):
    return bot.add_cog(Thread(bot))
