import discord
import os
import traceback
from datetime import datetime, timedelta
import sys
import requests
from dispander import dispand

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
client = discord.Client(intents=intents)

#Bootmsg-console
@client.event
async def on_ready():
    print('logged in as {0.user}'.format(client))

#Dispander
@client.event
async def on_message(message):
    if message.author.bot:
        return
    await dispand(message)

client.run(token)