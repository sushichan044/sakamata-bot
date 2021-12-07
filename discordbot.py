import discord
import os
import traceback
from datetime import datetime, timedelta
import sys
import requests
from dispanderfixed import dispand
from discord.ext import commands

'''bot招待リンク
https://discord.com/api/oauth2/authorize?client_id=916956842440151070&permissions=543816019030&scope=bot
'''

### イベントハンドラ一覧(client) #################################################
# async def の後を変えるだけで実行されるイベンドが変わる
# メッセージ受信時に実行：   on_message(message)
# Bot起動時に実行：      on_ready(message)
# リアクション追加時に実行:  on_reaction_add(reaction, user)
# 新規メンバー参加時に実行： on_member_join(member)
# ボイスチャンネル出入に実行： on_voice_state_update(member, before, after)
###################################################################

#onlinetoken@heroku
token = os.environ['DISCORD_BOT_TOKEN']

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/",intents=intents)

#IDなど
guildid = 915910043461890078
logchannel = 917009541433016370
vclogchannel = 917009562383556678


#Bootmsg-serverlogchannel/console
now = datetime.utcnow() + timedelta(hours=9)

async def greet():
    channel = bot.get_channel(logchannel)
    await channel.send(f'起動完了。({now:%m/%d-%H:%M:%S})')

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
    await bot.process_commands(message)

'''
デフォルトで提供されている on_message をオーバーライドすると、コマンドが実行されなくなります。
これを修正するには on_message の最後に bot.process_commands(message) を追加してみてください。
'''

#VC入退室ログ
@bot.event
async def on_voice_state_update(member,before,after) :
    if member.guild.id == guildid and (before.channel != after.channel):
        alert_channel = bot.get_channel(vclogchannel)
        vclogmention = f'<@{member.id}>'
        if before.channel is None:
            msg = f'({now:%m/%d-%H:%M:%S}):{vclogmention} が "{after.channel.name}" に参加しました。'
            await alert_channel.send(msg)
        elif after.channel is None:
            msg = f'({now:%m/%d-%H:%M:%S}):{vclogmention} が "{before.channel.name}" から退出しました。'
            await alert_channel.send(msg)
        else:
            msg = f'({now:%m/%d-%H:%M:%S}):{vclogmention} が "{before.channel.name}" から "{after.channel.name}" に移動しました。'
            await alert_channel.send(msg)

#変更前形式
# {now:%m/%d-%H:%M:%S} に {}...aaa


bot.run(token)