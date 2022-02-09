import logging
import os
import re
import traceback
from datetime import timedelta, timezone

import discord
from discord import Member
from discord.ext import commands

from Cogs.connect import connect
from Cogs.inquiry import InquiryView, SuggestionView
from Core.membership import MemberVerifyButton
from Genshin.portal import PortalView

logging.basicConfig(level=logging.INFO)

"""bot招待リンク
https://discord.com/api/oauth2/authorize?client_id=916956842440151070&permissions=1403113958646&scope=bot%20applications.commands


イベントハンドラ一覧(client)
async def の後を変えるだけで実行されるイベンドが変わる
メッセージ受信時に実行：   on_message(message)
Bot起動時に実行：      on_ready(message)
リアクション追加時に実行:  on_reaction_add(reaction, user)
新規メンバー参加時に実行： on_member_join(member)
ボイスチャンネル出入に実行： on_voice_state_update(member, before, after)"""

conn = connect()
utc = timezone.utc
jst = timezone(timedelta(hours=9), "Asia/Tokyo")

# onlinetoken@heroku
token = os.environ["DISCORD_BOT_TOKEN"]

# help-command-localize-test


class JapaneseHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()
        self.commands_heading = "コマンド:"
        self.no_category = "その他のコマンド"
        self.command_attrs["help"] = "コマンド一覧と簡単な説明を表示"

    def get_ending_note(self):
        return "各コマンドの説明: //help <コマンド名>\n"


intents = discord.Intents.all()
"""
bot = commands.Bot(command_prefix='//', intents=intents,
                   help_command=JapaneseHelpCommand())
                   """

CORE_EXTENSION_LIST = [
    "Core.ban",
    "Core.confirm",
    "Core.dm",
    "Core.error",
    "Core.kick",
    "Core.log_sender",
    "Core.logger",
    "Core.message",
    "Core.membership",
    "Core.timeout",
    "Core.utils",
]

EXTENSION_LIST = [
    "Cogs.concept",
    "Cogs.entrance",
    "Cogs.inquiry",
    "Cogs.member_count",
    "Cogs.ng_word",
    "Cogs.poll",
    "Cogs.slow",
    "Cogs.starboard",
    "Cogs.stream",
    "Cogs.thread",
    "Cogs.tool",
]

GENSHIN_EXTENSION_LIST = ["Genshin.portal"]


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="//", intents=intents, help_command=JapaneseHelpCommand()
        )
        self.persistent_views_added = False
        for cog in CORE_EXTENSION_LIST:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()
            else:
                print(f"Core extension [{cog}] is loaded!")
        for cog in EXTENSION_LIST:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()
            else:
                print(f"extension [{cog}] is loaded!")
        for cog in GENSHIN_EXTENSION_LIST:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()
            else:
                print(f"extension for Genshin [{cog}] is loaded!")

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(MemberVerifyButton())
            self.add_view(PortalView())
            self.add_view(InquiryView())
            self.add_view(SuggestionView())
            self.persistent_views_added = True
            print("Set Persistant Views!")
        print("------------------------------------------------------")
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------------------------------------------------------")
        channel = self.get_channel(log_channel)
        now = discord.utils.utcnow()
        await channel.send(
            f"起動完了({now.astimezone(jst):%m/%d-%H:%M:%S})\nBot ID:{self.user.id}"
        )
        return


bot = MyBot()


# ID-guild
guild_id = int(os.environ["GUILD_ID"])

# ID-role
everyone = int(os.environ["GUILD_ID"])
server_member_role = int(os.environ["SERVER_MEMBER_ROLE"])
mod_role = int(os.environ["MOD_ROLE"])
admin_role = int(os.environ["ADMIN_ROLE"])
yt_membership_role = int(os.environ["YT_MEMBER_ROLE"])
stop_role = int(os.environ["STOP_ROLE"])
vc_stop_role = int(os.environ["VC_STOP_ROLE"])

# ID-channel
alert_channel = int(os.environ["ALERT_CHANNEL"])
stream_channel = int(os.environ["STREAM_CHANNEL"])
star_channel = int(os.environ["STAR_CHANNEL"])
dm_box_channel = int(os.environ["DM_BOX_CHANNEL"])
alert_channel = int(os.environ["ALERT_CHANNEL"])
member_check_channel = int(os.environ["MEMBER_CHECK_CHANNEL"])

# ID-log
thread_log_channel = int(os.environ["THREAD_LOG_CHANNEL"])
join_log_channel = int(os.environ["JOIN_LOG_CHANNEL"])
log_channel = int(os.environ["LOG_CHANNEL"])
vc_log_channel = int(os.environ["VC_LOG_CHANNEL"])
error_log_channel = int(os.environ["ERROR_CHANNEL"])

# Id-vc
count_vc = int(os.environ["COUNT_VC"])


# emoji
accept_emoji = "\N{Heavy Large Circle}"
reject_emoji = "\N{Cross Mark}"


# pattern
# yyyy/mm/dd
date_pattern = re.compile(r"^\d{4}/\d{2}/\d{2}")

# discord's invite url
discord_pattern = re.compile(r"discord.gg/[\w]*")

# list
stop_list = [stop_role, vc_stop_role]

# other
env = os.environ["ENV"]  # main or alpha


"""
デフォルトで提供されている on_message をオーバーライドすると、コマンドが実行されなくなります。
これを修正するには on_message の最後に bot.process_commands(message) を追加してみてください。
https://discordbot.jp/blog/17/
"""


@bot.command(name="user")
@commands.has_role(mod_role)
async def _new_user(ctx, member: Member):
    """ユーザー情報を取得できます。"""
    guild = ctx.guild
    member = guild.get_member(member)
    # この先表示する用
    avatar_url = member.display_avatar.replace(size=1024, static_format="webp").url
    if member.avatar is None:
        avatar_url = "DefaultAvatar"
    member_reg_date = member.created_at.astimezone(jst)
    # NickNameあるか？
    if member.display_name == member.name:
        member_nickname = "None"
    else:
        member_nickname = member.display_name
    member_join_date = member.joined_at.astimezone(jst)
    # membermention = member.mention
    roles = [[x.name, x.id] for x in member.roles]
    # [[name,id],[name,id]...]
    x = ["/ID: ".join(str(y) for y in x) for x in roles]
    z = "\n".join(x)
    # Message成形-途中
    user_info_msg = f"```ユーザー名:{member} (ID:{member.id})\nBot?:{member.bot}\nAvatar url:{avatar_url}\nニックネーム:{member_nickname}\nアカウント作成日時:{member_reg_date:%Y/%m/%d %H:%M:%S}\n参加日時:{member_join_date:%Y/%m/%d %H:%M:%S}\n\n所持ロール:\n{z}```"
    await ctx.reply(user_info_msg, mention_author=False)
    return


# YoutubeAPI
API_KEY = os.environ["GOOGLE_API_KEY"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


if __name__ == "__main__":
    bot.run(token)
