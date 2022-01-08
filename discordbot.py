import asyncio
import logging
import os
import re
from datetime import datetime, timedelta, timezone

import discord
from discord.ui.button import button
import requests
from discord import Member
from discord.message import MessageType
from discord.channel import DMChannel
from discord.commands import Option, permissions
from discord.ext import commands, pages, tasks
from discord.ext.ui import (
    Button, Message, MessageProvider, View, ViewTracker, state)
from newdispanderfixed import dispand

logging.basicConfig(level=logging.INFO)

'''bot招待リンク
https://discord.com/api/oauth2/authorize?client_id=916956842440151070&permissions=1403113958646&scope=bot%20applications.commands
'''

'''イベントハンドラ一覧(client)
async def の後を変えるだけで実行されるイベンドが変わる
メッセージ受信時に実行：   on_message(message)
Bot起動時に実行：      on_ready(message)
リアクション追加時に実行:  on_reaction_add(reaction, user)
新規メンバー参加時に実行： on_member_join(member)
ボイスチャンネル出入に実行： on_voice_state_update(member, before, after)'''


utc = timezone.utc
jst = timezone(timedelta(hours=9), 'Asia/Tokyo')

# onlinetoken@heroku
token = os.environ['DISCORD_BOT_TOKEN']

# help-command-localize-test


class JapaneseHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.commands_heading = "コマンド:"
        self.no_category = "利用可能なコマンド"
        self.command_attrs["help"] = "コマンド一覧と簡単な説明を表示"

    def get_ending_note(self):
        return ('各コマンドの説明: /help <コマンド名>\n')


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents,
                   help_command=JapaneseHelpCommand())


# 本番鯖IDなど

guild_id = 915910043461890078
log_channel = 917009541433016370
vc_log_channel = 917009562383556678
dm_box_channel = 921781301101613076
error_log_channel = 924142068484440084
alert_channel = 924744385902575616
member_check_channel = 926777825925677096
thread_log_channel = 927110282675884082
join_log_channel = 929015822272299038
count_vc = 925256795491012668
server_member_role = 915915792275632139
mod_role = 916726433445986334
admin_role = 915954009343422494
everyone = 915910043461890078
yt_membership_role = 923789641159700500

'''
# 実験鯖IDなど
guild_id = 916965252896260117
log_channel = 916971090042060830
vc_log_channel = 916988601902989373
dm_box_channel = 918101377958436954
error_log_channel = 924141910321426452
alert_channel = 924744469327257602
member_check_channel = 926777719964987412
thread_log_channel = 927110073996693544
join_log_channel = 929015770539761715
count_vc = 925249967478673519
server_member_role = 923719282360188990
mod_role = 924355349308383252
admin_role = 917332284582031390
everyone = 916965252896260117
yt_membership_role = 926268230417408010
'''
# Classes


class MemberConfView(View):
    status = state('status')
    ok_str = state('ok_str')
    ng_str = state('ng_str')
    que = state('que')
    ng_url = state('ng_url')
    ng_style = state('ng_style')
    left_button = state('left_button')
    right_button = state('right_button')

    def __init__(self, future, ctx):
        super().__init__()
        self.future = future
        self.status = None
        self.ok_str = '承認'
        self.ng_str = '否認'
        self.ng_style = discord.ButtonStyle.red
        self.left_button = Button(self.ok_str).style(discord.ButtonStyle.green).disabled(self.status is not None).on_click(self.ok)
        self.right_button = Button(self.ng_str).style(self.ng_style).disabled(self.status is False).on_click(self.ng)
        self.ng_url = ''
        self.ctx = ctx
        self.que = '承認しますか？'

    async def ok(self, interaction: discord.Interaction):
        self.future.set_result(True)
        self.status = True
        self.que = '承認済み'
        self.ok_str = '承認されました'
        self.ng_str = 'スプレッドシート'
        self.ng_style = discord.ButtonStyle.link
        self.ng_url = os.environ['MEMBERSHIP_SPREADSHEET']
        self.left_button = Button(self.ok_str).style(discord.ButtonStyle.green).disabled(self.status is not None).on_click(self.ok)
        self.right_button = Button(self.ng_str).style(self.ng_style).disabled(self.status is False).on_click(self.ng).url(self.ng_url)
        await interaction.response.defer()
        return

    async def ng(self, interaction: discord.Interaction):
        self.future.set_result(False)
        self.status = False
        self.que = '否認済み'
        self.ng_str = '否認されました'
        self.left_button = Button(self.ng_str).style(discord.ButtonStyle.red).disabled(True)
        self.right_button = Button('承認').style(discord.ButtonStyle.green).disabled(True).on_click(self.ok)
        await interaction.response.defer()
        return

    async def body(self) -> Message:
        image_url = [x.url for x in self.ctx.message.attachments]
        embedimg = []
        embed = discord.Embed(
            title=self.que,
            description='メンバー認証コマンドを受信しました。',
            color=15767485,
            url=self.ctx.message.jump_url,
            timestamp=self.ctx.message.created_at
        )
        embed.set_author(
            name=self.ctx.message.author.display_name,
            icon_url=self.ctx.message.author.avatar.url
        )
        embed.add_field(
            name='送信者',
            value=f'{self.ctx.message.author.mention}'
        )
        embed.add_field(
            name='受信日時',
            value=f'{self.ctx.message.created_at.astimezone(jst):%Y/%m/%d %H:%M:%S}'
        )
        embedimg.append(embed)
        for x in image_url:
            embed = discord.Embed()
            embed.set_image(
                url=x
            )
            embedimg.append(embed)
        return Message(
            embeds=embedimg,
            components=[
                self.left_button,
                self.right_button
            ]
        )


class MemberRemoveView(View):
    status = state('status')
    que = state('que')
    sheet = state('sheet')
    complete = state('complete')

    def __init__(self, future, ctx):
        super().__init__()
        self.future = future
        self.ctx = ctx
        self.status = None
        self.que = 'スプレッドシートを更新してください。'
        self.sheet = 'スプレッドシート'
        self.complete = '更新完了'

    async def done(self, interaction: discord.Interaction):
        self.future.set_result(True)
        self.status = True
        self.que = '更新済み'
        self.complete = '更新されました'
        await interaction.response.defer()
        return

    async def body(self) -> Message:
        embed_list = []
        embed = discord.Embed(
            title=self.que,
            description='メンバー継続停止が通知されました。',
            color=15767485,
            url=self.ctx.message.jump_url,
            timestamp=self.ctx.message.created_at
        )
        embed.set_author(
            name=self.ctx.message.author.display_name,
            icon_url=self.ctx.message.author.avatar.url
        )
        embed.add_field(
            name='送信者',
            value=f'{self.ctx.message.author.mention}'
        )
        embed.add_field(
            name='受信日時',
            value=f'{self.ctx.message.created_at.astimezone(jst):%Y/%m/%d %H:%M:%S}'
        )
        embed_list.append(embed)
        return Message(
            embeds=embed_list,
            components=[
                Button(self.sheet)
                .style(discord.ButtonStyle.link)
                .disabled(self.status is not None)
                .url(os.environ['MEMBERSHIP_SPREADSHEET']),
                Button(self.complete)
                .style(discord.ButtonStyle.green)
                .disabled(self.status is not None)
                .on_click(self.done),
            ]
        )


# emoji
maru_emoji = "\N{Heavy Large Circle}"
batu_emoji = "\N{Cross Mark}"

# Boot-log


async def greet():
    channel = bot.get_channel(log_channel)
#    now = discord.utils.utcnow() + timedelta(hours=9)
    now = discord.utils.utcnow()
    await channel.send(f'起動完了({now.astimezone(jst):%m/%d-%H:%M:%S})\nBot ID:{bot.user.id}')
    return

# Task-MemberCount


@tasks.loop(minutes=30)
async def start_count():
    await bot.wait_until_ready()
    await membercount()

# 起動イベント


@bot.event
async def on_ready():
    print('logged in as {0.user}'.format(bot))
    await greet()
    return

# manualcount


@bot.command(name='manualcount')
@commands.has_role(admin_role)
async def _manual(ctx):
    await membercount()
    return

# Membercount本体


async def membercount():
    guild = bot.get_guild(guild_id)
    server_member_count = guild.member_count
    vc = bot.get_channel(count_vc)
    await vc.edit(name=f'Member Count: {server_member_count}')
    return

# error-log


@bot.event
async def on_error(event, something):
    channel = bot.get_channel(error_log_channel)
    now = discord.utils.utcnow().astimezone(jst)
    await channel.send(f'```エラーが発生しました。({now:%m/%d %H:%M:%S})\n{str(event)}\n{str(something)}```')
    return


@bot.event
async def on_command_error(ctx, error):
    channel = bot.get_channel(error_log_channel)
    now = discord.utils.utcnow().astimezone(jst)
    await channel.send(f'```エラーが発生しました。({now:%m/%d %H:%M:%S})\n{str(error)}```')
    if isinstance(error, commands.MissingRole):
        await ctx.reply(content='このコマンドを実行する権限がありません。', mention_author=False)
        return
    elif isinstance(error, commands.CommandNotFound):
        await ctx.reply(content='指定されたコマンドは存在しません。', mention_author=False)
        return
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.reply(content='Botに必要な権限がありません。', mention_author=False)
        return
    else:
        return

# error-logtest


@bot.command()
@commands.has_role(admin_role)
async def errortest(ctx):
    prin()

# Detect-NGword


@bot.listen('on_message')
async def detect_NGword(message):
    word_list = ['@everyone', '@here', '@飼育員たち']
    if message.author == bot.user:
        return
    elif type(message.channel) == DMChannel:
        return
    else:
        m = [x for x in word_list if x in message.content]
        prog = re.compile(r'discord.gg/[\w]*')
        n = prog.findall(message.content)
#        print(n)
        invites_list = await message.guild.invites()
        invites_url = [x.url for x in invites_list]
        replaced_invites = [item.replace('https://', '')
                            for item in invites_url]
#        print(f'{replaced_invites}')
        n = [x for x in n if x not in replaced_invites]
        if m != [] or n != []:
            m = m + n
            m = '\n'.join(m)
            await send_ng_log(message, m)
            return
        else:
            return

# send-nglog


async def send_ng_log(message, m):
    channel = bot.get_channel(alert_channel)
    embed = discord.Embed(
        title='NGワードを検知しました。',
        url=message.jump_url,
        color=16711680,
        description=message.content,
        timestamp=message.created_at
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar.url
    )
    embed.add_field(
        name='検知ワード',
        value=f'{m}'
    )
    embed.add_field(
        name='送信者',
        value=f'{message.author.mention}'
    )
    embed.add_field(
        name='送信先',
        value=f'{message.channel.mention}'
    )
    embed.add_field(
        name='送信日時',
        value=f'{message.created_at.astimezone(jst):%Y/%m/%d %H:%M:%S}'
    )
    await channel.send(embed=embed)
    return

# Dispander-All


@bot.listen('on_message')
async def on_message_dispand(message):
    avoid_word_list_head = ['/send-message', '/edit-message', '/send-dm']
    if type(message.channel) == DMChannel:
        return
    else:
        for x in avoid_word_list_head:
            if message.content.startswith(x):
                return
        if message.content.endswith('中止に必要な承認人数: 1'):
            return
        else:
            await dispand(message)
            return

'''
デフォルトで提供されている on_message をオーバーライドすると、コマンドが実行されなくなります。
これを修正するには on_message の最後に bot.process_commands(message) を追加してみてください。
https://discordbot.jp/blog/17/
'''

# VC入退室ログ


@bot.listen()
async def on_voice_state_update(member, before, after):
    if member.guild.id == guild_id and (before.channel != after.channel):
        channel = bot.get_channel(vc_log_channel)
        now = discord.utils.utcnow()
        vc_log_mention = member.mention
        if before.channel is None:
            msg = f'{now.astimezone(jst):%m/%d %H:%M:%S} : {vc_log_mention} が {after.channel.mention} に参加しました。'
            await channel.send(msg)
            return
        elif after.channel is None:
            msg = f'{now.astimezone(jst):%m/%d %H:%M:%S} : {vc_log_mention} が {before.channel.mention} から退出しました。'
            await channel.send(msg)
            return
        else:
            msg = f'{now.astimezone(jst):%m/%d %H:%M:%S} : {vc_log_mention} が {before.channel.mention} から {after.channel.mention} に移動しました。'
            await channel.send(msg)
            return

# hello?


@bot.command()
@commands.has_role(mod_role)
async def test(ctx):
    """生存確認用"""
    await ctx.send('hello')
    return
'''
# user-info-command
@bot.command()
@commands.has_role(mod_role)
async def user(ctx,id:int):
    """ユーザー情報取得"""
    guild = bot.get_guild(guild_id)
    member = guild.get_member(id)
    # この先表示する用
    member_if_bot = member.bot
    member_reg_date = member.created_at.astimezone(jst)
    # NickNameあるか？
    if member.display_name == member.name :
        member_if_nickname = 'None'
    else:
        member_if_nickname = member.display_name
    member_id = member.id
    member_join_date = member.joined_at.astimezone(jst)
    membermention = member.mention
    roles = [[x.name,x.id] for x in member.roles]
# [[name,id],[name,id]...]
    x = ['/ID: '.join(str(y) for y in x) for x in roles]
    z = '\n'.join(x)
    # Message成形-途中
    user_info_msg = f'```ユーザー名:{member} (ID:{member_id})\nBot?:{member_if_bot}\nニックネーム:{member_if_nickname}\nアカウント作成日時:{member_reg_date:%Y/%m/%d %H:%M:%S}\n参加日時:{member_join_date:%Y/%m/%d %H:%M:%S}\n\n所持ロール:\n{z}```'
    await ctx.send(user_info_msg)
'''


@bot.slash_command(name='user', guild_ids=[guild_id], default_permission=False)
@permissions.has_role(mod_role)
async def _newuser(
    ctx,
    member: Option(Member, '対象のIDや名前を入力してください。'),
):
    '''ユーザー情報を取得できます。'''
    # guild = ctx.guild
    # member = guild.get_member(int(id))
    # この先表示する用
    member_if_bot = member.bot
    member_reg_date = member.created_at.astimezone(jst)
    # NickNameあるか？
    if member.display_name == member.name:
        member_if_nickname = 'None'
    else:
        member_if_nickname = member.display_name
    member_id = member.id
    member_join_date = member.joined_at.astimezone(jst)
    # membermention = member.mention
    roles = [[x.name, x.id] for x in member.roles]
    # [[name,id],[name,id]...]
    x = ['/ID: '.join(str(y) for y in x) for x in roles]
    z = '\n'.join(x)
    # Message成形-途中
    user_info_msg = f'```ユーザー名:{member} (ID:{member_id})\nBot?:{member_if_bot}\nニックネーム:{member_if_nickname}\nアカウント作成日時:{member_reg_date:%Y/%m/%d %H:%M:%S}\n参加日時:{member_join_date:%Y/%m/%d %H:%M:%S}\n\n所持ロール:\n{z}```'
    await ctx.respond(user_info_msg)
    return


# new-user-info-command
'''
@bot.command()
@commands.has_role(mod_role)
async def user(ctx,id:int):
    """ユーザー情報取得"""
    target: Optional[Member,User]
    target = ctx.guild.get_member(id)
    if target is None:
        target = await bot.fetch_user(id)
    else:
        pass
    if isinstance(target,Member):
        targetin = 'True'
        targetjoindate = target.joined_at + timedelta(hours=9)
        targetroles = target.roles
        if target.display_name == target.name :
            targetifnick = 'None'
        else:
            targetifnick = target.display_name
    elif isinstance(target,User):
        targetifnick = 'None'
        targetin = 'False'
        targetjoindate = 'None'
        targetroles = 'None'
    else:
        pass
    targetregdate =target.created_at + timedelta(hours=9)
    # Message成形-途中
    targetinfomsg = f'```ユーザー名:{target} (ID:{target.id})\nBot?:{target.bot}\nin server?:{targetin}\nニックネーム:{targetifnick}\nアカウント作成日時:{targetregdate:%Y/%m/%d %H:%M:%S}\n参加日時:{targetjoindate:%Y/%m/%d %H:%M:%S}\n所持ロール:{targetroles}```'
    await ctx.send(targetinfomsg)
    return
'''
'''
    # サーバーメンバー判定
    targetregdate =target.created_at + timedelta(hours=9)
    if ctx.guild.id in target.mutual_guilds == True:
        targetinserver = 'True'
    else:
        targetinserver = 'False'
    # 同サーバー内のみ判定
    targetjoindate = 'None'
    targetroles = 'None'
    targetifnickname = 'None'
    if targetinserver == 'True':
        targetjoindate = target.joined_at + timedelta(hours=9)
        targetroles = target.roles
        if target.display_name == target.name :
            pass
        else:
            targetifnickname = target.display_name
    else:
        pass
    '''

# ping-test


@bot.command()
@commands.has_role(admin_role)
async def ping(ctx):
    """生存確認用"""
    raw_ping = bot.latency
    ping = round(raw_ping * 1000)
    await ctx.send(f'Pong!\nPing is {ping}ms')
    return

# recieve-dm


@bot.listen('on_message')
async def on_message_dm(message):
    avoid_dm_list = ['/check', '/remove-member']
    if type(message.channel) == DMChannel and bot.user == message.channel.me:
        if message.author.bot:
            return
        else:
            for x in avoid_dm_list:
                if message.content.startswith(x):
                    return
            if message.content == '/check':
                return
            channel = bot.get_channel(dm_box_channel)
            sent_messages = []
            if message.content or message.attachments:
                # Send the second and subsequent attachments with embed (named 'embed') respectively:
                embed = await compose_embed(message)
                sent_messages.append(embed)
                for attachment in message.attachments[1:]:
                    embed = discord.Embed()
                    embed.set_image(
                        url=attachment.proxy_url
                    )
                    sent_messages.append(embed)
            for embed in message.embeds:
                sent_messages.append(embed)
            await channel.send(embeds=sent_messages)
            return
    else:
        return

# send-message


@bot.command(name='send-message')
@commands.has_role(admin_role)
async def _messagesend(ctx, channel_id: int, *, arg):
    """メッセージ送信用"""
    # channel:送信先
    channel = bot.get_channel(channel_id)
    # role:承認可能ロール
    role = ctx.guild.get_role(admin_role)
    confirm_msg = f'【メッセージ送信確認】\n以下のメッセージを{channel.mention}へ送信します。'
    exe_msg = f'{channel.mention}にメッセージを送信しました。'
    non_exe_msg = f'{channel.mention}へのメッセージ送信をキャンセルしました。'
    confirm_arg = f'\n{arg}\n------------------------'
    turned = await confirm(ctx, confirm_arg, role, confirm_msg)
    if turned:
        msg = exe_msg
        m = await channel.send(arg)
        desc_url = m.jump_url
        await ctx.send('Sended!')
        await send_exe_log(ctx, msg, desc_url)
        return
    elif turned is False:
        msg = non_exe_msg
        desc_url = ''
        await send_exe_log(ctx, msg, desc_url)
        await ctx.send('Cancelled!')
        return
    else:
        return

# send-dm


@bot.command(name='send-dm')
@commands.has_role(admin_role)
async def _dmsend(ctx, user: Member, *, arg):
    """DM送信用"""
    role = ctx.guild.get_role(admin_role)
    confirm_msg = f'【DM送信確認】\n以下のDMを{user.mention}へ送信します。'
    exe_msg = f'{user.mention}にDMを送信しました。'
    non_exe_msg = f'{user.mention}へのDM送信をキャンセルしました。'
    confirm_arg = f'\n{arg}\n------------------------'
    turned = await confirm(ctx, confirm_arg, role, confirm_msg)
    if turned:
        msg = exe_msg
        m = await user.send(arg)
        desc_url = m.jump_url
        await ctx.send('Sended!')
        await send_exe_log(ctx, msg, desc_url)
        return
    elif turned is False:
        msg = non_exe_msg
        desc_url = ''
        await send_exe_log(ctx, msg, desc_url)
        await ctx.send('Cancelled!')
        return
    else:
        return

# edit-message


@bot.command(name='edit-message')
@commands.has_role(admin_role)
async def _editmessage(ctx, channel_id: int, message_id: int, *, arg):
    """メッセージ編集用"""
    channel = bot.get_channel(channel_id)
    role = ctx.guild.get_role(admin_role)
    edit_target = await channel.fetch_message(message_id)
    msg_url = f'https://discord.com/channels/{ctx.guild.id}/{channel_id}/{message_id}'
    confirm_msg = f'【メッセージ編集確認】\n{channel.mention}のメッセージ\n{msg_url}\nを以下のように編集します。'
    exe_msg = f'{channel.mention}のメッセージを編集しました。'
    non_exe_msg = f'{channel.mention}のメッセージの編集をキャンセルしました。'
    confirm_arg = f'\n{arg}\n------------------------'
    turned = await confirm(ctx, confirm_arg, role, confirm_msg)
    if turned:
        msg = exe_msg
        await edit_target.edit(content=arg)
        desc_url = msg_url
        await ctx.send('Edited!')
        await send_exe_log(ctx, msg, desc_url)
        return
    elif turned is False:
        msg = non_exe_msg
        desc_url = ''
        await send_exe_log(ctx, msg, desc_url)
        await ctx.send('Cancelled!')
        return
    else:
        return

# PollEmoji
poll_emoji_list = [
    '\N{Large Red Circle}',
    '\N{Large Green Circle}',
    '\N{Large Orange Circle}',
    '\N{Large Blue Circle}',
    # '\N{Large Yellow Circle}',
    '\N{Large Brown Circle}',
    '\N{Large Purple Circle}',
    # '\N{Medium Black Circle}',
    # '\N{Medium White Circle}',
    '\N{Large Red Square}',
    '\N{Large Green Square}',
    '\N{Large Orange Square}',
    '\N{Large Blue Square}',
    # '\N{Large Yellow Square}',
    '\N{Large Brown Square}',
    '\N{Large Purple Square}',
    # '\N{Black Large Square}',
    # '\N{White Large Square}',
    '\N{Large Orange Diamond}',
    '\N{Large Blue Diamond}',
    '\N{Heavy Black Heart}',
    '\N{Green Heart}',
    '\N{Orange Heart}',
    '\N{Blue Heart}',
    '\N{Brown Heart}',
    '\N{Purple Heart}',
]
# Poll


@bot.command(name='poll')
@commands.has_role(server_member_role)
async def _poll(ctx, title, *select):
    if select == ():
        embed = discord.Embed(
            title=title,
            description="\N{Large Green Circle}Yes\n\N{Large Red Circle}No",
            color=3447003,
        )
        poll_yes_emoji = '\N{Large Green Circle}'
        poll_no_emoji = '\N{Large Red Circle}'
        m = await ctx.send(embed=embed)
        await m.add_reaction(poll_yes_emoji)
        await m.add_reaction(poll_no_emoji)
        return
    elif len(select) > 20:
        embed = discord.Embed(
            title='選択肢が多すぎます。',
            color=16098851,
        )
        await ctx.send(embed=embed)
        return
    else:
        send_desc_list = []
        for num in range(len(select)):
            element = f'{poll_emoji_list[num]}{select[num]}'
            send_desc_list.append(element)
        send_desc = '\n'.join(send_desc_list)
        embed = discord.Embed(
            title=title,
            description=send_desc,
            color=3447003,
        )
        m = await ctx.send(embed=embed)
        for x in range(len(select)):
            await m.add_reaction(poll_emoji_list[x])
        return

# deal-member
# deal:対処。ban/kick
deal = None
# add_dm:デフォルトDMに追加で送信するコンテンツ
add_dm = None

# timeout-member


@bot.command(name='timeout')
@commands.has_role(mod_role)
async def _timeout(ctx, member: Member, input_until: str, if_dm: str = 'True'):
    '''メンバーをタイムアウト'''
    until = datetime.strptime(input_until, '%Y%m%d')
    until_jst = until.replace(tzinfo=jst)
    role = ctx.guild.get_role(mod_role)
    valid_if_dm_list = ['True', 'False']
    until_str = datetime.strftime(until_jst, '%Y/%m/%d/%H:%M')
    if if_dm not in valid_if_dm_list:
        await ctx.reply(content='不明な引数を検知したため処理を終了しました。\nDM送信をOFFにするにはFalseを指定してください。', mention_author=False)
        msg = '不明な引数を検知したため処理を終了しました。'
        desc_url = ''
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        deal = 'timeout'
        add_dm = f'あなたは{until_str}までサーバーでの発言とボイスチャットへの接続を制限されます。'
        DM_content = await makedealdm(ctx, deal, add_dm)
        if if_dm == 'False':
            DM_content = ''
        else:
            pass
        confirm_msg = f'【timeout実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{member}(ID:{member.id})\n期限:{until_str}\nDM送信:{if_dm}\nDM内容:{DM_content}'
        exe_msg = f'{member.mention}をタイムアウトしました。'
        non_exe_msg = f'{member.mention}のタイムアウトをキャンセルしました。'
        confirm_arg = ''
        turned = await confirm(ctx, confirm_arg, role, confirm_msg)
        if turned:
            msg = exe_msg
            if if_dm == 'True':
                m = await member.send(DM_content)
                desc_url = m.jump_url
                await member.timeout(until_jst.astimezone(utc), reason=None)
                await ctx.send('timeouted!')
                await sendtolog(ctx, msg, desc_url, until_str)
                return
            elif if_dm == 'False':
                desc_url = ''
                await member.timeout(until_jst + timedelta(hours=-9), reason=None)
                await ctx.send('timeouted!')
                await sendtolog(ctx, msg, desc_url, until_str)
                return
            else:
                return
        elif turned is False:
            msg = non_exe_msg
            desc_url = ''
            await send_exe_log(ctx, msg, desc_url)
            await ctx.send('Cancelled!')
            return
        else:
            return

# untimeout-member


@bot.command(name='untimeout')
@commands.has_role(admin_role)
async def _untimeout(ctx, member: Member):
    '''メンバーのタイムアウトを解除'''
    role = ctx.guild.get_role(admin_role)
    confirm_msg = f'【untimeout実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{member}(ID:{member.id})'
    exe_msg = f'{member.mention}のタイムアウトの解除をしました。'
    non_exe_msg = f'{member.mention}のタイムアウトの解除をキャンセルしました。'
    confirm_arg = ''
    turned = await confirm(ctx, confirm_arg, role, confirm_msg)
    if turned:
        msg = exe_msg
        desc_url = ''
        await member.timeout(None, reason=None)
        await ctx.send('untimeouted!')
        await send_exe_log(ctx, msg, desc_url)
        return
    elif turned is False:
        msg = non_exe_msg
        desc_url = ''
        await send_exe_log(ctx, msg, desc_url)
        await ctx.send('Cancelled!')
        return
    else:
        return


# kick-member


@bot.command(name='kick')
@commands.has_role(admin_role)
async def _kickuser(ctx, member: Member, if_dm: str = 'True'):
    '''メンバーをキック'''
    role = ctx.guild.get_role(admin_role)
    valid_if_dm_list = ['True', 'False']
    if if_dm not in valid_if_dm_list:
        await ctx.reply(content='不明な引数を検知したため処理を終了しました。\nDM送信をOFFにするにはFalseを指定してください。', mention_author=False)
        msg = '不明な引数を検知したため処理を終了しました。'
        desc_url = ''
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        deal = 'kick'
        add_dm = ''
        DM_content = await makedealdm(ctx, deal, add_dm)
        if if_dm == 'False':
            DM_content = ''
        else:
            pass
        confirm_msg = f'【kick実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{member}(ID:{member.id})\nDM送信:{if_dm}\nDM内容:{DM_content}'
        exe_msg = f'{member.mention}をキックしました。'
        non_exe_msg = f'{member.mention}のキックをキャンセルしました。'
        confirm_arg = ''
        turned = await confirm(ctx, confirm_arg, role, confirm_msg)
        if turned:
            msg = exe_msg
            if if_dm == 'True':
                m = await member.send(DM_content)
                desc_url = m.jump_url
                await member.kick(reason=None)
                await ctx.send('kicked!')
                await send_exe_log(ctx, msg, desc_url)
                return
            elif if_dm == 'False':
                desc_url = ''
                await member.kick(reason=None)
                await ctx.send('kicked!')
                await send_exe_log(ctx, msg, desc_url)
                return
            else:
                return
        elif turned is False:
            msg = non_exe_msg
            desc_url = ''
            await send_exe_log(ctx, msg, desc_url)
            await ctx.send('Cancelled!')
            return
        else:
            return

# ban-member


@bot.command(name='ban')
@commands.has_role(admin_role)
async def _banuser(ctx, member: Member, if_dm: str = 'True'):
    '''メンバーをBAN'''
    role = ctx.guild.get_role(admin_role)
    valid_if_dm_list = ['True', 'False']
    if if_dm not in valid_if_dm_list:
        await ctx.reply(content='不明な引数を検知したため処理を終了しました。\nDM送信をOFFにするにはFalseを指定してください。', mention_author=False)
        msg = '不明な引数を検知したため処理を終了しました。'
        desc_url = ''
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        deal = 'BAN'
        add_dm = '''
今後、あなたはクロヱ水族館に参加することはできません。

BANの解除を希望する場合は以下のフォームをご利用ください。
クロヱ水族館BAN解除申請フォーム
https://forms.gle/mR1foEyd9JHbhYdCA
'''
        DM_content = await makedealdm(ctx, deal, add_dm)
        if if_dm == 'False':
            DM_content = ''
        else:
            pass
        confirm_msg = f'【BAN実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{member}(ID:{member.id})\nDM送信:{if_dm}\nDM内容:{DM_content}'
        exe_msg = f'{member.mention}をBANしました。'
        non_exe_msg = f'{member.mention}のBANをキャンセルしました。'
        confirm_arg = ''
        turned = await confirm(ctx, confirm_arg, role, confirm_msg)
        if turned:
            msg = exe_msg
            if if_dm == 'True':
                m = await member.send(DM_content)
                desc_url = m.jump_url
                await member.ban(reason=None)
                await ctx.send('baned!')
                await send_exe_log(ctx, msg, desc_url)
                return
            elif if_dm == 'False':
                desc_url = ''
                await member.ban(reason=None)
                await ctx.send('baned!')
                await send_exe_log(ctx, msg, desc_url)
                return
            else:
                return
        elif turned is False:
            msg = non_exe_msg
            desc_url = ''
            await ctx.send('Cancelled!')
            await send_exe_log(ctx, msg, desc_url)
            return
        else:
            return

# Unban-member


@bot.command(name='unban')
@commands.has_role(admin_role)
async def _unbanuser(ctx, id: int):
    '''ユーザーのBANを解除'''
    user = await bot.fetch_user(id)
    banned_users = await ctx.guild.bans()
    role = ctx.guild.get_role(admin_role)
    for ban_entry in banned_users:
        if ban_entry.user.id == user.id:
            confirm_msg = f'【Unban実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{user}(ID:{user.id})'
            exe_msg = f'{user.mention}のBANを解除しました。'
            non_exe_msg = f'{user.mention}のBANの解除をキャンセルしました。'
            confirm_arg = ''
            turned = await confirm(ctx, confirm_arg, role, confirm_msg)
            if turned:
                msg = exe_msg
                desc_url = ''
                await ctx.guild.unban(user)
                await ctx.send('Unbaned!')
                await send_exe_log(ctx, msg, desc_url)
                return
            elif turned is False:
                msg = non_exe_msg
                desc_url = ''
                await ctx.send('Cancelled!')
                await send_exe_log(ctx, msg, desc_url)
                return
            else:
                return
        else:
            await ctx.reply('BANリストにないユーザーを指定したため処理を停止します。', mention_author=False)
            msg = 'BANリストにないユーザーを指定したため処理を停止しました。'
            desc_url = ''
            await send_exe_log(ctx, msg, desc_url)
            return

# check-member


@bot.command(name='check')
@commands.dm_only()
async def _check_member(ctx):
    '''メンバーシップ認証用'''
    if ctx.message.attachments == []:
        await ctx.reply(content='画像が添付されていません。画像を添付して送り直してください。', mention_author=False)
        msg = 'メンバー認証コマンドに画像が添付されていなかったため処理を停止しました。'
        desc_url = ''
        await send_exe_log(ctx, msg, desc_url)
        return
    else:
        await ctx.reply(content='認証要求を受理しました。\nしばらくお待ちください。', mention_author=False)
        channel = bot.get_channel(member_check_channel)
        guild = bot.get_guild(guild_id)
        exe_msg = f'{ctx.message.author.mention}のメンバーシップ認証を承認しました。'
        non_exe_msg = f'{ctx.message.author.mention}のメンバーシップ認証を否認しました。'
        future = asyncio.Future()
        view = MemberConfView(future, ctx)
        tracker = ViewTracker(view, timeout=None)
        await tracker.track(MessageProvider(channel))
        await future
        if future.done():
            if future.result():
                msg = exe_msg
                desc_url = tracker.message.jump_url
                member = guild.get_member(ctx.message.author.id)
                membership_role_object = guild.get_role(yt_membership_role)
                await member.add_roles(membership_role_object)
                await ctx.reply(content='メンバーシップ認証を承認しました。\nメンバー限定チャンネルをご利用いただけます!', mention_author=False)
                log_channel_object = bot.get_channel(log_channel)
                embed = discord.Embed(
                    title='実行ログ',
                    color=3447003,
                    description=msg,
                    url=f'{desc_url}',
                    timestamp=discord.utils.utcnow()
                )
                embed.set_author(
                    name=bot.user,
                    icon_url=bot.user.display_avatar.url
                )
                embed.add_field(
                    name='実行日時',
                    value=f'{discord.utils.utcnow().astimezone(jst):%Y/%m/%d %H:%M:%S}'
                )
                await log_channel_object.send(embed=embed)
                return
            else:
                msg = non_exe_msg
                desc_url = tracker.message.jump_url
                await tracker.message.reply(content='DMで送信する不承認理由を入力してください。', mention_author=False)

                def check(message):
                    return message.content is not None and message.channel == channel and message.author != bot.user
                message = await bot.wait_for('message', check=check)
                reply_msg = f'メンバーシップ認証を承認できませんでした。\n理由:\n　{message.content}'
                await ctx.reply(content=reply_msg, mention_author=False)
                log_channel_object = bot.get_channel(log_channel)
                embed = discord.Embed(
                    title='実行ログ',
                    color=3447003,
                    description=msg,
                    url=f'{desc_url}',
                    timestamp=discord.utils.utcnow()
                )
                embed.set_author(
                    name=bot.user,
                    icon_url=bot.user.display_avatar.url
                )
                embed.add_field(
                    name='実行日時',
                    value=f'{discord.utils.utcnow().astimezone(jst):%Y/%m/%d %H:%M:%S}'
                )
                await log_channel_object.send(embed=embed)
                return


# remove-member


@bot.command(name='remove-member')
@commands.dm_only()
async def _remove_member(ctx):
    await ctx.reply(content='メンバーシップ継続停止を受理しました。\nしばらくお待ちください。', mention_author=False)
    channel = bot.get_channel(member_check_channel)
    guild = bot.get_guild(guild_id)
    exe_msg = f'{ctx.message.author.mention}のメンバーシップ継続停止を反映しました。'
    future = asyncio.Future()
    view = MemberRemoveView(future, ctx)
    tracker = ViewTracker(view, timeout=None)
    await tracker.track(MessageProvider(channel))
    await future
    if future.done():
        if future.result():
            msg = exe_msg
            desc_url = tracker.message.jump_url
            member = guild.get_member(ctx.message.author.id)
            membership_role_object = guild.get_role(yt_membership_role)
            await member.remove_roles(membership_role_object)
            await ctx.reply(content='メンバーシップ継続停止を反映しました。\nメンバーシップに再度登録された際は`/check`で再登録してください。', mention_author=False)
            log_channel_object = bot.get_channel(log_channel)
            embed = discord.Embed(
                title='実行ログ',
                color=3447003,
                description=msg,
                url=f'{desc_url}',
                timestamp=discord.utils.utcnow()
            )
            embed.set_author(
                name=bot.user,
                icon_url=bot.user.display_avatar.url
            )
            embed.add_field(
                name='実行日時',
                value=f'{discord.utils.utcnow().astimezone(jst):%Y/%m/%d %H:%M:%S}'
            )
            await log_channel_object.send(embed=embed)
            return

# member-update-dm


@bot.command(name='update-member')
@commands.has_role(admin_role)
async def _update_member(ctx, *update_member: Member):
    role = ctx.guild.get_role(admin_role)
    update_member_mention = [x.mention for x in update_member]
    update_member_str = '\n'.join(update_member_mention)
    confirm_msg = f'【DM送信確認】\nメンバーシップ更新DMを\n{update_member_str}\nへ送信します。'
    exe_msg = f'{update_member_str}にメンバーシップ更新DMを送信しました。'
    non_exe_msg = f'{update_member_str}へのメンバーシップ更新DM送信をキャンセルしました。'
    DM_content = '【メンバーシップ更新のご案内】\n沙花叉のメンバーシップの更新時期が近づいた方にDMを送信させていただいております。\nお支払いが完了して次回支払日が更新され次第、以前と同じように\n`/check`\nで再認証を行ってください。\nメンバーシップを継続しない場合は\n`/remove-member`\nと送信してください。'
    confirm_arg = f'\n{DM_content}\n------------------------'
    turned = await confirm(ctx, confirm_arg, role, confirm_msg)
    if turned:
        for x in update_member:
            await x.send(DM_content)
        await ctx.send('Sended!')
        msg = exe_msg
        desc_url = ''
        await send_exe_log(ctx, msg, desc_url)
        return
    elif turned is False:
        msg = non_exe_msg
        desc_url = ''
        await send_exe_log(ctx, msg, desc_url)
        await ctx.send('Cancelled!')
        return
    else:
        return

# save-img


async def download_img(url, file_name):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(r.content)


# Deal-DM


async def makedealdm(ctx, deal, add_dm):
    DM_content = f'''【あなたは{deal}されました】
クロヱ水族館/Chloeriumの管理者です。

あなたのサーバーでの行為がサーバールールに違反していると判断し、{deal}しました。
{add_dm}'''
    return DM_content

# confirm-system


async def confirm(ctx, confirm_arg, role, confirm_msg) -> bool:
    send_confirm_msg = f'{confirm_msg}\n------------------------{confirm_arg}\nコマンド承認:{role.mention}\n実行に必要な承認人数: 1\n中止に必要な承認人数: 1'
    m = await ctx.send(send_confirm_msg)
    await m.add_reaction(maru_emoji)
    await m.add_reaction(batu_emoji)
    valid_reactions = [maru_emoji, batu_emoji]
    # wait-for-reaction

    def checkconf(payload):
        return role in payload.member.roles and str(payload.emoji) in valid_reactions and payload.message_id == m.id
    payload = await bot.wait_for('raw_reaction_add', check=checkconf)
    # exe
    if str(payload.emoji) == maru_emoji:
        return True
    else:
        return False

# send-exe-log


async def send_exe_log(ctx, msg, desc_url):
    channel = bot.get_channel(log_channel)
    embed = discord.Embed(
        title='実行ログ',
        color=3447003,
        description=msg,
        url=f'{desc_url}',
        timestamp=discord.utils.utcnow()
    )
    embed.set_author(
        name=bot.user,
        icon_url=bot.user.display_avatar.url
    )
    embed.add_field(
        name='実行者',
        value=f'{ctx.author.mention}'
    )
    embed.add_field(
        name='実行コマンド',
        value=f'[コマンドリンク]({ctx.message.jump_url})'
    )
    embed.add_field(
        name='実行日時',
        value=f'{discord.utils.utcnow().astimezone(jst):%Y/%m/%d %H:%M:%S}'
    )
    await channel.send(embed=embed)
    return

# send-timeout-log


async def sendtolog(ctx, msg, desc_url, until_str):
    channel = bot.get_channel(log_channel)
    embed = discord.Embed(
        title='実行ログ',
        color=3447003,
        description=msg,
        url=f'{desc_url}',
        timestamp=discord.utils.utcnow()
    )
    embed.set_author(
        name=bot.user,
        icon_url=bot.user.display_avatar.url
    )
    embed.add_field(
        name='実行者',
        value=f'{ctx.author.mention}'
    )
    embed.add_field(
        name='実行コマンド',
        value=f'[コマンドリンク]({ctx.message.jump_url})'
    )
    embed.add_field(
        name='解除日時',
        value=f'{until_str}'
    )
    embed.add_field(
        name='実行日時',
        value=f'{discord.utils.utcnow().astimezone(jst):%Y/%m/%d %H:%M:%S}'
    )
    await channel.send(embed=embed)
    return


# compose-embed


async def compose_embed(message):
    embed = discord.Embed(
        title='DMを受信しました。',
        url=message.jump_url,
        color=3447003,
        description=message.content,
        timestamp=message.created_at
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar.url,
    )
    embed.add_field(
        name='送信者',
        value=f'{message.author.mention}'
    )
    embed.add_field(
        name='受信日時',
        value=f'{message.created_at.astimezone(jst):%Y/%m/%d %H:%M:%S}'
    )
    if message.attachments and message.attachments[0].proxy_url:
        embed.set_image(
            url=message.attachments[0].proxy_url
        )
    return embed

# notice-thread/send-log


@bot.listen('on_thread_join')
async def detect_thread(thread):
    channel = bot.get_channel(thread_log_channel)
    thread_member_list = await thread.fetch_members()
    if bot.user.id in [x.id for x in thread_member_list]:
        return
    else:
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
        await channel.send(embed=embed)
        return

# detect-thread-archive


@bot.listen('on_thread_update')
async def detect_archive(before, after):
    if after.locked and not before.locked:
        return
    elif after.archived and not before.archived:
        await after.edit(archived=False)
        return
    else:
        return

# YoutubeAPI
API_KEY = os.environ['GOOGLE_API_KEY']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

'''
# create-event
@bot.command(name='make-event')
@commands.has_role(mod_role)
async def _createevent(ctx,event_name,stream_url:str,start_time:str,duration:int,):
    guild = ctx.guild
    if len(start_time)==4:
        todate = datetime.now(timezone.utc).astimezone(jst)
        starttime = datetime.strptime(start_time,'%H%M')
        true_start_jst = datetime.replace(starttime,year=todate.year,month=todate.month,day=todate.day,tzinfo=jst)
    elif len(start_time)==12:
        true_start = datetime.strptime(start_time,'%Y%m%d%H%M')
        true_start_jst = datetime.replace(true_start,tzinfo=jst)
    else:
        await ctx.reply(content='正しい時間を入力してください。\n有効な時間は\n```202205182100(2022年5月18日21:00)もしくは\n2100(入力した日の21:00)です。```',mention_author=False)
        return
    true_duration = timedelta(hours=duration)
    true_end = true_start_jst + true_duration
    await guild.create_scheduled_event(name = f'【配信】{event_name}',
                                       description='',
                                       start_time = true_start_jst.astimezone(utc),
                                       end_time = true_end,
                                       location = stream_url,
                                       )
    return
'''

# create-event-slash


@bot.slash_command(guild_ids=[guild_id], default_permission=False, name='make-event')
@permissions.has_role(mod_role)
async def _newcreateevent(ctx,
                          event_name: Option(str, '配信の名前(例:マリカ,歌枠,など)'),
                          stream_url: Option(str, '配信のURL'),
                          start_time: Option(str, '配信開始時間(202205182100または2100(当日))'),
                          duration: Option(float, '予想される配信の長さ(単位:時間)(例:1.5)'),
                          ):
    '''配信を簡単にイベントに登録できます。'''
    guild = ctx.guild
    if len(start_time) == 4:
        todate = datetime.now(timezone.utc).astimezone(jst)
        start_time_object = datetime.strptime(start_time, '%H%M')
        true_start_jst = start_time_object.replace(
            year=todate.year, month=todate.month, day=todate.day, tzinfo=jst)
    elif len(start_time) == 12:
        true_start = datetime.strptime(start_time, '%Y%m%d%H%M')
        true_start_jst = true_start.replace(tzinfo=jst)
    else:
        await ctx.respond(content='正しい時間を入力してください。\n有効な時間は\n```202205182100(2022年5月18日21:00)もしくは\n2100(入力した日の21:00)です。```', mention_author=False)
        return
    true_duration = timedelta(hours=duration)
    true_end = true_start_jst + true_duration
    await guild.create_scheduled_event(name=f'{event_name}',
                                       description='',
                                       start_time=true_start_jst.astimezone(
                                           utc),
                                       end_time=true_end,
                                       location=stream_url,
                                       )
    await ctx.respond('配信を登録しました。')
    return

# Member-join-or-leave-log


@bot.listen('on_member_join')
async def on_join(member):
    status = '参加'
    await _send_member_log(member, status)
    return


@bot.listen('on_member_remove')
async def on_leave(member):
    status = '退出'
    await _send_member_log(member, status)
    return


# send-join-leave-log
async def _send_member_log(member, status):
    channel = bot.get_channel(join_log_channel)
    now = discord.utils.utcnow().astimezone(jst)
    send_time = datetime.strftime(now, '%Y/%m/%d %H:%M:%S')
    count = member.guild.member_count
    send_msg = f"時刻: {send_time}\n{status}メンバー名: {member.name} (ID:{member.id})\nメンション: {member.mention}\nアカウント作成時刻: {member.created_at.astimezone(jst):%Y/%m/%d %H:%M:%S}\n現在のメンバー数:{count}\n"
    await channel.send(send_msg)
    return


start_count.start()
bot.run(token)
