import os
from datetime import timedelta, timezone

import discord
from discord import commands

thread_log_channel = os.environ['THREAD_LOG_CHANNEL']
jst = timezone(timedelta(hours=9), 'Asia/Tokyo')


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
