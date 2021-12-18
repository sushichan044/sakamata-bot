from logging import debug
import discord
import os
import traceback
from datetime import datetime, timedelta
import sys
from discord.channel import DMChannel
from discord.ext.commands.core import dm_only
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
bot = commands.Bot(command_prefix='/',intents=intents)


'''
#本番鯖IDなど

guildid = 915910043461890078
logchannel = 917009541433016370
vclogchannel = 917009562383556678
commandchannel = 917788634655109200
dmboxchannel = 921781301101613076

'''
#実験鯖IDなど
guildid = 916965252896260117
logchannel = 916971090042060830
vclogchannel = 916988601902989373
commandchannel = 917788514903539794
dmboxchannel = 918101377958436954


#Bootmsg-serverlogchannel/console
async def greet():
    channel = bot.get_channel(logchannel)
    now = datetime.utcnow() + timedelta(hours=9)
    await channel.send(f'起動完了({now:%m/%d-%H:%M:%S})')

@bot.event
async def on_ready():
    print('logged in as {0.user}'.format(bot))
    await greet()


'''
#Dispander-botreject-ugokanai
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await dispand(message)
    await bot.process_commands(message)
'''

#Dispander-All
@bot.event
async def on_message(message):
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
        nowvclog = datetime.utcnow() + timedelta(hours=9)
        vclogmention = f'<@{member.id}>'
        if before.channel is None:
            msg = f'{nowvclog:%m/%d %H:%M:%S} : {vclogmention} が "{after.channel.name}" に参加しました。'
            await alert_channel.send(msg)
        elif after.channel is None:
            msg = f'{nowvclog:%m/%d %H:%M:%S} : {vclogmention} が "{before.channel.name}" から退出しました。'
            await alert_channel.send(msg)
        else:
            msg = f'{nowvclog:%m/%d %H:%M:%S} : {vclogmention} が "{before.channel.name}" から "{after.channel.name}" に移動しました。'
            await alert_channel.send(msg)

#hello?>>
@bot.command()
async def test(ctx):
    await ctx.send('hello')

#user-info-command
@bot.command()
async def user(ctx,id: int):
    user = bot.get_user(id)
    guild = bot.get_guild(guildid)
    member = guild.get_member(id)
    channel = bot.get_channel(commandchannel)
    #この先表示する用
    memberifbot = member.bot
    memberregdate = member.created_at
    #NickNameあるか？
    membername = member.name
    membernickname = member.display_name
    if membernickname == membername :
        memberifnickname = "None"
    else:
        memberifnickname = membernickname
    memberid = member.id
    memberjoindate = member.joined_at
    membermention = member.mention
    memberroles = member.roles
    #Message成形-途中
    userinfomsg = f'```ユーザー名:{member} (ID:{memberid})\nBot?:{memberifbot}\nニックネーム:{memberifnickname}\nアカウント作成日時:{memberregdate:%Y/%m/%d %H:%M:%S}\n参加日時:{memberjoindate:%Y/%m/%d %H:%M:%S}\n所持ロール:{memberroles}```'
    await channel.send(userinfomsg)

#ping-test
@bot.command()
async def ping(ctx):
    rawping = bot.latency
    ping = round(rawping * 1000)
    await ctx.send(f'Ping is {ping}ms')

#send-dm
@bot.command(name='send-dm')
async def dmsend(ctx,id:int,*,arg):
    guild = bot.get_guild(guildid)
    member = guild.get_member(id)
    await member.send(arg)

#recieve-dm
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    elif type(message.channel) == discord.DMChannel and bot.user == message.channel.me:
        channel = bot.get_channel(dmboxchannel)
        embed = discord.Embed(
        color=3447003,
        description=message.content,
        timestamp=message.created_at,
        )
        embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar_url,
        url=message.jump_url
        )
        embed.add_field(
            name='送信者',
            value=f'<@{message.author.id}>'
        )
        await channel.send(embed=embed)
    await bot.process_commands(message)


bot.run(token)