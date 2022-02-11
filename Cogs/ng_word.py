import os
import re
from datetime import timedelta, timezone

import discord
from discord.ext import commands

jst = timezone(timedelta(hours=9), "Asia/Tokyo")
alert_channel = int(os.environ["ALERT_CHANNEL"])
alert_channel_mods = int(os.environ["ALERT_CHANNEL_MODS"])
admin_role = int(os.environ["ADMIN_ROLE"])


class NGWordSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def detect_NG_word(self, message: discord.Message):
        word_list_high = ["@everyone", "@here", "@飼育員たち"]
        word_list_low = ["るしあ", "ルシア", "まふまふ"]
        if (
            message.author == self.bot.user
            or type(message.channel) == discord.DMChannel
        ):
            return
        else:
            high_ng_msg = [x for x in word_list_high if x in message.content]
            low_ng_msg = [word for word in word_list_low if word in message.content]
            prog = re.compile(r"discord.gg/[\w]*")
            links = prog.findall(message.content)
            # print(n)
            # invites_list = await message.guild.invites()
            invites_url = [x.url for x in await message.guild.invites()]
            allowed_urls = [item.replace("https://", "") for item in invites_url]
            # print(f'{replaced_invites}')
            ng_url = [link for link in links if link not in allowed_urls]
            if high_ng_msg != [] or ng_url != []:
                ng_content = high_ng_msg + ng_url
                ng_content = "\n".join(ng_content)
                await self.send_ng_log_high(message, ng_content)
                return
            elif low_ng_msg != []:
                ng_content = "\n".join(low_ng_msg)
                await self.send_ng_log_low(message, ng_content)
            else:
                return

            # send_ng_log

    async def send_ng_log_high(self, message: discord.Message, ng_content: str):
        channel = self.bot.get_channel(alert_channel)
        text = "要注意メッセージを検知しました。"
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
