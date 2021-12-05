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
bot = commands.Bot(command_prefix="/",intents=intents)

#IDなど
guildid = 916965252896260117
logchannel = 916971090042060830
vclogchannel = 916988601902989373


#Bootmsg-console

async def greet():
    channel = bot.get_channel(logchannel)
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

#VC入退室ログ
@bot.event
async def on_voice_state_update(member,before,after) :
    if member.guild.id == guildid and (before.channel != after.channel):
        now = datetime.utcnow() + timedelta(hours=9)
        alert_channel = bot.get_channel(vclogchannel)
        vclogmention = f'<@{member.id}>'
        if before.channel is None:
            msg = f'{now:%m/%d-%H:%M:%S} に {vclogmention} が "{after.channel.name}" に参加しました。'
            await alert_channel.send(msg)
        elif after.channel is None:
            msg = f'{now:%m/%d-%H:%M:%S} に {vclogmention} が "{before.channel.name}" から退出しました。'
            await alert_channel.send(msg)
        else:
            msg = f'{now:%m/%d-%H:%M:%S} に {vclogmention} が "{before.channel.name}" から "{after.channel.name}" に移動しました。'
            await alert_channel.send(msg)


#oumu
@bot.command()
async def test(ctx):
    if ctx.author == bot.user:
        return
    await ctx.send("ongyaa")


bot.run(token)