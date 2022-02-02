import os
import re
from datetime import timedelta, timezone

import discord
from discord.ext import commands

jst = timezone(timedelta(hours=9), "Asia/Tokyo")
alert_channel = int(os.environ["ALERT_CHANNEL"])
admin_role = int(os.environ["ADMIN_ROLE"])


class NGWordSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def detect_NG_word(self, message):
        word_list = ["@everyone", "@here", "@飼育員たち"]
        if (
            message.author == self.bot.user
            or type(message.channel) == discord.DMChannel
        ):
            return
        else:
            ng_msg = [x for x in word_list if x in message.content]
            prog = re.compile(r"discord.gg/[\w]*")
            links = prog.findall(message.content)
            # print(n)
            # invites_list = await message.guild.invites()
            invites_url = [x.url for x in await message.guild.invites()]
            allowed_urls = [item.replace("https://", "") for item in invites_url]
            # print(f'{replaced_invites}')
            ng_url = [link for link in links if link not in allowed_urls]
            if ng_msg != [] or ng_url != []:
                ng_content = ng_msg + ng_url
                ng_content = "\n".join(ng_content)
                await self.send_ng_log(message, ng_content)
                return
            else:
                return

            # send_ng_log

    async def send_ng_log(self, message, m):
        channel = self.bot.get_channel(alert_channel)
        embed = discord.Embed(
            title="要注意メッセージを検知しました。",
            url=message.jump_url,
            color=16711680,
            description=message.content,
            timestamp=message.created_at,
        )
        embed.set_author(
            name=message.author.display_name, icon_url=message.author.avatar.url
        )
        embed.add_field(name="検知ワード", value=f"{m}")
        embed.add_field(name="送信者", value=f"{message.author.mention}")
        embed.add_field(name="送信先", value=f"{message.channel.mention}")
        embed.add_field(
            name="送信日時", value=f"{message.created_at.astimezone(jst):%Y/%m/%d %H:%M:%S}"
        )
        await channel.send(content=f"<@&{admin_role}>", embed=embed)
        return


def setup(bot):
    return bot.add_cog(NGWordSystem(bot))
