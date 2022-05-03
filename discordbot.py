import logging
import os
import re
import traceback
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands
from dotenv import load_dotenv

from Cogs.inquiry import InquiryView, SuggestionView
from Core.membership import MemberVerifyButton
from Event.birth_mishmash import MishMash_View

load_dotenv()

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
    "Event.birth_mishmash",
]


SONG_DB_EXTENSION_LIST = [
    # "SongDB.main",
]


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
            self.add_view(MishMash_View())
            self.persistent_views_added = True
            print("Set Persistant Views!")
        print("------------------------------------------------------")
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------------------------------------------------------")
        channel = self.get_channel(log_channel)
        now = datetime.now(jst)
        await channel.send(
            f"起動完了({now.strftime('%m/%d %H:%M:%S')})\nBot ID:{self.user.id}"
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


# YoutubeAPI
API_KEY = os.environ["GOOGLE_API_KEY"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


if __name__ == "__main__":
    bot.run(token)
