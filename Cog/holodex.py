import os

import aiohttp
import discord
from discord.ext import commands, tasks

from holodex.client import HolodexClient

from .connect import connect
from .holodex_process import TimeData

conn = connect()
admin_role = int(os.environ['ADMIN_ROLE'])
api_key = os.environ['HOLODEX_KEY']
headers = {
    'X-APIKEY': f'{api_key}'
}
stream_channel = int(os.environ['STREAM_CHANNEL'])


class StreamNotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._get_stream.start()

    def cog_unload(self):
        self._get_stream.cancel()

    @commands.command(name='stream')
    @commands.has_role(admin_role)
    async def get_stream(self, ctx):
        await self.get_stream_method()
        return

    @tasks.loop(minutes=1.5)
    async def _get_stream(self):
        await self.bot.wait_until_ready()
        await self.get_stream_method()

    # stream-body

    async def get_stream_method(self):
        async with HolodexClient(aiohttp.ClientSession(headers=headers)) as client:
            ch_id = os.environ['STREAM_YT_ID']
            lives = await client.live_streams(channel_id=ch_id)
            archives = await client.videos_from_channel(channel_id=ch_id, type='videos')
            yt_channel = await client.channel(channel_id=ch_id)
            lives_tuple = (x for x in lives.contents if x.status ==
                           'upcoming' and x.type == 'stream')
            nowgoing_tuple = (x for x in lives.contents if x.status ==
                              'live' and x.type == 'stream')
            ended_tuple = (x for x in archives.contents if x.status ==
                           'past' and x.type == 'stream')
            for x in lives_tuple:
                result = conn.get(x.id)
                if result is not None:
                    print('配信が重複していたためスキップします。')
                    continue
                else:
                    holodex = TimeData()
                    conn.set(f'{x.id}', 'notified', ex=604800)
                    date, time, timestamp, weekday_str, created = holodex.time_schedule(x)
                    embed = discord.Embed(
                        title=f'{x.title}',
                        description='**待機所が作成されました**',
                        url=f'https://youtu.be/{x.id}',
                        color=16711680,
                    )
                    embed.set_author(
                        name=f'{yt_channel.name}',
                        url=f'https://www.youtube.com/channel/{ch_id}'
                    )
                    embed.add_field(
                        name='**配信予定日(JST)**',
                        value=f'{date}({weekday_str})',
                    )
                    embed.add_field(
                        name='**配信予定時刻(JST)**',
                        value=f'{time}',
                    )
                    embed.add_field(
                        name='**配信予定時刻(Timestamp)**',
                        value=f'<t:{timestamp}:f>',
                        inline=False
                    )
                    embed.set_image(
                        url=f'https://i.ytimg.com/vi/{x.id}/maxresdefault.jpg'
                    )
                    embed.set_footer(
                        text=f'{yt_channel.name} ({created})',
                        icon_url=f'{yt_channel.photo}'
                    )
                    channel = self.bot.get_channel(stream_channel)
                    await channel.send(embed=embed)
                    continue
            for x in nowgoing_tuple:
                result = conn.get(x.id)
                if result == 'notified':
                    holodex = TimeData()
                    conn.set(f'{x.id}', 'started', ex=604800)
                    actual_start = holodex.time_going(x)
                    embed = discord.Embed(
                        title=f'{x.title}',
                        description='**ライブストリーミングが開始されました**',
                        url=f'https://youtu.be/{x.id}',
                        color=16711680,
                    )
                    embed.set_author(
                        name=f'{yt_channel.name}',
                        url=f'https://www.youtube.com/channel/{ch_id}'
                    )
                    embed.set_footer(
                        text=f'{yt_channel.name} ({actual_start})',
                        icon_url=f'{yt_channel.photo}'
                    )
                    embed.set_image(
                        url=f'https://i.ytimg.com/vi/{x.id}/maxresdefault.jpg'
                    )
                    channel = self.bot.get_channel(stream_channel)
                    await channel.send(embed=embed)
                else:
                    continue
            for x in ended_tuple:
                result = conn.get(x.id)
                if result == 'started':
                    holodex = TimeData()
                    conn.set(f'{x.id}', 'ended', ex=604800)
                    actual_end, end_date, end_time, duration_str, weekday_str = holodex.time_ended(x)
                    embed = discord.Embed(
                        title=f'{x.title}',
                        description='**ライブストリーミングが終了しました**',
                        url=f'https://youtu.be/{x.id}',
                        color=16711680,
                    )
                    embed.set_author(
                        name=f'{yt_channel.name}',
                        url=f'https://www.youtube.com/channel/{ch_id}'
                    )
                    embed.set_footer(
                        text=f'{yt_channel.name} ({actual_end})',
                        icon_url=f'{yt_channel.photo}'
                    )
                    embed.add_field(
                        name='**配信終了日(JST)**',
                        value=f'{end_date}({weekday_str})',
                    )
                    embed.add_field(
                        name='**配信終了時刻(JST)**',
                        value=f'{end_time}',
                    )
                    embed.add_field(
                        name='**総配信時間**',
                        value=f'{duration_str}',
                    )
                    embed.set_image(
                        url=f'https://i.ytimg.com/vi/{x.id}/maxresdefault.jpg'
                    )
                    channel = self.bot.get_channel(stream_channel)
                    await channel.send(embed=embed)
                else:
                    continue


def setup(bot):
    return bot.add_cog(StreamNotify(bot))
