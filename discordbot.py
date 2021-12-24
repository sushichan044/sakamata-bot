from logging import debug
import discord
import os
import traceback
from datetime import datetime, timedelta
import sys
from discord import channel
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

#help-command-localize-test
class JapaneseHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.commands_heading = "コマンド:"
        self.no_category = "利用可能なコマンド"
        self.command_attrs["help"] = "コマンド一覧と簡単な説明を表示"

    def get_ending_note(self):
        return (f"各コマンドの説明: /help <コマンド名>\n"
                f"各カテゴリの説明: /help <カテゴリ名>\n")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/',intents=intents,help_command=JapaneseHelpCommand())


'''
#本番鯖IDなど

guildid = 915910043461890078
logchannel = 917009541433016370
vclogchannel = 917009562383556678
commandchannel = 917788634655109200
dmboxchannel = 921781301101613076
siikuinrole = 915915792275632139

'''
#実験鯖IDなど
guildid = 916965252896260117
logchannel = 916971090042060830
vclogchannel = 916988601902989373
commandchannel = 917788514903539794
dmboxchannel = 918101377958436954
siikuinrole = 923719282360188990


#Bootmsg-serverlogchannel/console
async def greet():
    channel = bot.get_channel(logchannel)
    now = datetime.utcnow() + timedelta(hours=9)
    await channel.send(f'起動完了({now:%m/%d-%H:%M:%S})')

@bot.event
async def on_ready():
    print('logged in as {0.user}'.format(bot))
    await greet()

#error-log
@bot.event
async def on_command_error(ctx,error):
    channel = bot.get_channel(logchannel)
    await channel.send(f'エラーが発生しました。\n{str(error)}')

#error-logtest
@bot.command()
async def errortest(ctx):
    prin()

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
@bot.listen()
async def on_message(message):
    if type(message.channel) == discord.DMChannel:
        return
    else:
        await dispand(message)

'''
デフォルトで提供されている on_message をオーバーライドすると、コマンドが実行されなくなります。
これを修正するには on_message の最後に bot.process_commands(message) を追加してみてください。
'''

#VC入退室ログ
@bot.listen()
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
    """生存確認用"""
    await ctx.send('hello')

#user-info-command
@bot.command()
async def user(ctx,id: int):
    """ユーザー情報取得"""
    user = bot.get_user(id)
    guild = bot.get_guild(guildid)
    member = guild.get_member(id)
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
    await ctx.send(userinfomsg)

#ping-test
@bot.command()
async def ping(ctx):
    """生存確認用"""
    rawping = bot.latency
    ping = round(rawping * 1000)
    await ctx.send(f'Ping is {ping}ms')

#send-dm
@bot.command(name='send-dm')
async def _dmsend(ctx,id:int,*,arg):
    """DM送信用"""
    user = bot.get_user(id)
    await user.send(arg)

#recieve-dm
@bot.listen()
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
    else:
        return

#send-message
@bot.command(name='send-message')
async def _messagesend(ctx,channelid:int,*,arg):
    """メッセージ送信用"""
    channel=bot.get_channel(channelid)
    role = ctx.guild.get_role(siikuinrole)
    if role.mention in arg:
        await ctx.send(embed=await confirmmessage(ctx,channelid,arg))
    else:
        await channel.send(arg)

#confirm-message
async def confirmmessage(ctx,channelid:int,arg):
    channel=bot.get_channel(ctx)
    embed = discord.Embed(
    color=3447003,
    description=arg,
    timestamp=datetime.utcnow()
    )
    embed.add_field(
        name='確認',
        value=f'以上のメッセージを<#{channelid}>へ送信しますか?'
        )
    return embed

#reaction_check
#async def reactioncheck():

bot.run(token)