import discord
import os
import traceback
from datetime import datetime, timedelta
import sys
import requests
from dispander import dispand
from discord.ext import commands


### イベントハンドラ一覧 #################################################
# async def の後を変えるだけで実行されるイベンドが変わる
# メッセージ受信時に実行：   on_message(message)
# Bot起動時に実行：      on_ready(message)
# リアクション追加時に実行:  on_reaction_add(reaction, user)
# 新規メンバー参加時に実行： on_member_join(member)
# ボイスチャンネル出入に実行： on_voice_state_update(member, before, after)
###################################################################

token = os.environ['DISCORD_BOT_TOKEN']

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix="/",
    intents=intents
)

#Bootmsg-console
channel_id = 916971090042060830

async def greet():
    channel = bot.get_channel(channel_id)
    await channel.send('起動完了')

@bot.event
async def on_ready():
    print('logged in as {0.user}'.format(bot))
    await greet()

#Dispander
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await dispand(message)

#/ping
@bot.command(name='ping')
async def _sen_ping_dm(ctx, arg):
    await ctx.send('peeeeeeee')

bot.run(token)