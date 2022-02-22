import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from unicodedata import name


import discord
from discord import Message
from discord.ext import commands

admin_role = int(os.environ["ADMIN_ROLE"])
security_channel = int(os.environ["SECURITY_CHANNEL"])
jst = timezone(timedelta(hours=9), "Asia/Tokyo")


class AntiSpam(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def _anti_rapid_post(self, message: Message):
        if message.channel.type == discord.DMChannel:
            return
        if message.author.id == self.bot.user.id or message.author.bot:
            return
        if admin_role in [r.id for r in message.author.roles]:
            return

        def check_rapid_post(m: Message):
            return (
                m.author == message.author
                and (
                    datetime.utcnow().astimezone(timezone.utc)
                    - m.created_at.astimezone(timezone.utc)
                ).seconds
                < 15
            )

        detected: tuple[Message] = tuple(
            filter(lambda m: check_rapid_post(m), self.bot.cached_messages)
        )
        if len(detected) >= 5:
            target = message.author
            channel = await message.guild.fetch_channel(security_channel)
            print("連投を検知")
            embed = _alert(detected=detected)
            await channel.send(
                content=f"<@&{admin_role}>", embed=embed, view=ExecView(target=target)
            )
            return  # alert 連投


def _alert(detected: tuple[Message]):
    embed = discord.Embed(
        title="不審な連投を検知しました。",
        description=f"対象ユーザー: {detected[0].author.mention} (ID: {detected[0].author.id})",
        color=16711680,
    )
    embed.set_footer(
        text=datetime.utcnow().astimezone(jst).strftime("%Y/%m/%d %H:%M:%S")
    )
    embed.set_author(
        name=detected[0].author.display_name,
        icon_url=detected[0].author.display_avatar.url,
    )
    embed.add_field(
        name="連投開始メッセージ",
        value=f"[移動]({detected[0].jump_url})",
        inline=False,
    )
    embed.add_field(
        name="連投終了メッセージ(現在も続いている可能性があります。)",
        value=f"[移動]({detected[-1].jump_url})",
        inline=False,
    )
    embed.add_field(
        name="組織的荒らしを受けている場合は？",
        value="`//slow-all`コマンドの仕様を検討してください。",
    )
    return embed


class ExecView(discord.ui.View):
    def __init__(self, *, target: discord.Member):
        super().__init__(timeout=None)
        self.add_item(TimeoutButton(target=target))
        self.add_item(IgnoreButton())


class Dis_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dis_Timeout())
        self.add_item(Dis_Ignore())


class TimeoutButton(discord.ui.Button):
    def __init__(self, *, target: Optional[discord.Member] = None, **kwargs):
        super().__init__(
            style=discord.ButtonStyle.danger,
            label="タイムアウト",
            custom_id="anti_spam_timeout",
            row=0,
            **kwargs,
        )
        self.target = target

    async def callback(self, interaction: discord.Interaction):
        await self.target.timeout_for(
            duration=timedelta(days=1), reason="Anti-Spam(Rapid post)"
        )
        view = Dis_View()
        await interaction.message.edit(view=view)
        await interaction.response.send_message(
            content=f"{self.target.display_name} (ID:{self.target.id})を\n24時間タイムアウトしました。"
        )
        return


class Dis_Timeout(TimeoutButton):
    def __init__(self):
        super().__init__(disabled=True)


class IgnoreButton(discord.ui.Button):
    def __init__(self, **kwargs):
        super().__init__(
            style=discord.ButtonStyle.blurple,
            label="問題ない",
            custom_id="anti_spam_ignore",
            row=0,
            **kwargs,
        )

    async def callback(self, interaction: discord.Interaction):
        view = Dis_View()
        await interaction.message.edit(view=view)
        await interaction.response.send_message(content="問題ないことが確認されました。")
        pass


class Dis_Ignore(IgnoreButton):
    def __init__(self):
        super().__init__(disabled=True)


def setup(bot):
    return bot.add_cog(AntiSpam(bot))
