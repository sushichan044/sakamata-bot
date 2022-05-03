import json
import os
import re
from datetime import timedelta, timezone

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


jst = timezone(timedelta(hours=9), "Asia/Tokyo")
alert_channel = int(os.environ["ALERT_CHANNEL"])
alert_channel_mods = int(os.environ["ALERT_CHANNEL_MODS"])
admin_role = int(os.environ["ADMIN_ROLE"])


class NGWordSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        d: dict[str, str] = {}
        print(os.path.dirname(__file__))
        path = os.path.join(os.path.dirname(__file__), r"./ng_word.json")
        with open(path, mode="r") as f:
            d = json.load(f)
        self.ng_high = [k for k, v in d.items() if v == "high"]
        self.ng_low = [k for k, v in d.items() if v == "low"]
        self.prog = re.compile(r"discord.gg/[\w]*")
        print(self.ng_high, self.ng_low)

    @commands.Cog.listener(name="on_message")
    async def detect_NG_word(self, message: discord.Message):
        if (
            message.author == self.bot.user
            or message.channel.type == discord.DMChannel
            or message.webhook_id
        ):
            return
        if type(message.author) == discord.Member:
            if admin_role in [role.id for role in message.author.roles]:
                return
        detected_high = [word for word in self.ng_high if word in message.content]
        detected_low = [word for word in self.ng_low if word in message.content]
        links: list[str] = self.prog.findall(message.content)
        ng_url = []
        if links:
            allowed_urls = [
                item.replace("https://", "")
                for item in [x.url for x in await message.guild.invites()]
            ]
            ng_url = [link for link in links if link not in allowed_urls]
        if detected_high != [] or ng_url != []:
            ng_content = detected_high + ng_url
            ng_content = "\n".join(ng_content)
            await self.send_ng_log_high(message, ng_content)
            return
        elif detected_low != []:
            ng_content = "\n".join(detected_low)
            await self.send_ng_log_low(message, ng_content)
        else:
            return

    async def send_ng_log_high(self, message: discord.Message, ng_content: str):
        channel = self.bot.get_channel(alert_channel)
        text = "要注意ワードを検知しました。"
        embed = self._embed(message, ng_content, text)
        await channel.send(content=f"<@&{admin_role}>", embed=embed)
        return

    async def send_ng_log_low(self, message: discord.Message, ng_content: str):
        channel = self.bot.get_channel(alert_channel)
        text = "要注意ワード検知"
        embed = self._embed(message, ng_content, text)
        await channel.send(embed=embed)
        return

    def _embed(self, message: discord.Message, ng_content: str, text: str):
        embed = discord.Embed(
            title=text,
            url=message.jump_url,
            color=16711680,
            description=message.content,
            timestamp=message.created_at,
        )
        embed.set_author(
            name=message.author.display_name, icon_url=message.author.avatar.url
        )
        embed.add_field(name="検知ワード", value=f"{ng_content}")
        embed.add_field(name="送信者", value=f"{message.author.mention}")
        embed.add_field(name="送信先", value=f"{message.channel.mention}")
        embed.add_field(
            name="送信日時",
            value=message.created_at.astimezone(jst).strftime("%Y/%m/%d %H:%M:%S"),
        )
        return embed


def setup(bot):
    return bot.add_cog(NGWordSystem(bot))
