import logging
import os
import re
import traceback
from datetime import timedelta, timezone

import discord
from discord import Member
from discord.ext import commands

from Cogs.inquiry import InquiryView, SuggestionView
from Core.membership import MemberVerifyButton
from Genshin.portal import PortalView

logging.basicConfig(level=logging.INFO)

utc = timezone.utc
jst = timezone(timedelta(hours=9), "Asia/Tokyo")

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

SONG_DB_EXTENSION_LIST = ["SongDB.command"]


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="//",
            intents=discord.Intents.all(),
            help_command=JapaneseHelpCommand(),
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
        for cog in SONG_DB_EXTENSION_LIST:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()
            else:
                print(f"extension for SongDB [{cog}] is loaded!")

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
            f"起動完了({now.astimezone(jst).strftime('%m/%d %H:%M:%S')})\nBot ID:{self.user.id}"
        )
        return


bot = MyBot()


# ID-guild
guild_id = int(os.environ["GUILD_ID"])

# ID-role
everyone = int(os.environ["GUILD_ID"])
mod_role = int(os.environ["MOD_ROLE"])
stop_role = int(os.environ["STOP_ROLE"])
vc_stop_role = int(os.environ["VC_STOP_ROLE"])

# ID-log
log_channel = int(os.environ["LOG_CHANNEL"])

# emoji
accept_emoji = "\N{Heavy Large Circle}"
reject_emoji = "\N{Cross Mark}"

# pattern(yyyy/mm/dd)
date_pattern = re.compile(r"^\d{4}/\d{2}/\d{2}")

# discord's invite url
discord_pattern = re.compile(r"discord.gg/[\w]*")

# tweet url
tweet_pattern = re.compile(
    r"https://twitter.com/(?P<account>[\w]+)/status/(?P<id>[\d]+)"
)

# list
stop_list = [stop_role, vc_stop_role]

# other
env = os.environ["ENV"]  # main or alpha


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
