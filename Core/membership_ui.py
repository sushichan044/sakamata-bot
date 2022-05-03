import os
from datetime import timedelta, timezone

import discord
from discord.ext.ui import Button, Message, View, state
from dotenv import load_dotenv

load_dotenv()

jst = timezone(timedelta(hours=9), "Asia/Tokyo")

# Classes


class ConfirmView(View):
    ctx = state("ctx")
    status = state("status")
    ok_str = state("ok_str")
    ng_str = state("ng_str")
    que = state("que")

    def __init__(self, ctx, future):
        super().__init__()
        self.ctx = ctx
        self.future = future
        self.status = None
        self.ok_str = "承認"
        self.ng_str = "否認"
        self.que = "承認しますか？"

    async def ok(self, interaction: discord.Interaction):
        self.future.set_result(True)
        self.status = True
        self.que = "承認済み"
        self.ok_str = "承認されました"
        await interaction.response.defer()
        return

    async def ng(self, interaction: discord.Interaction):
        self.future.set_result(False)
        self.status = False
        self.que = "否認済み"
        self.ng_str = "否認されました"
        await interaction.response.defer()
        return

    async def body(self) -> Message:
        image_url = [x.url for x in self.ctx.message.attachments]
        embed_list = []
        embed = discord.Embed(
            title=self.que,
            description="メンバー認証コマンドを受信しました。",
            color=15767485,
            url=self.ctx.message.jump_url,
            timestamp=self.ctx.message.created_at,
        )
        embed.set_author(
            name=self.ctx.message.author.display_name,
            icon_url=self.ctx.message.author.avatar.url,
        )
        embed.add_field(name="送信者", value=f"{self.ctx.message.author.mention}")
        embed.add_field(
            name="受信日時",
            value=f"{self.ctx.message.created_at.astimezone(jst):%Y/%m/%d %H:%M:%S}",
        )
        embed_list.append(embed)
        for x in image_url:
            embed = discord.Embed(
                color=15767485,
            )
            embed.set_image(url=x)
            embed_list.append(embed)
        return Message(
            embeds=embed_list,
            components=[
                Button(self.ok_str)
                .style(discord.ButtonStyle.green)
                .disabled(self.status is not None)
                .on_click(self.ok),
                Button(self.ng_str)
                .style(discord.ButtonStyle.red)
                .disabled(self.status is not None)
                .on_click(self.ng),
            ],
        )


class RemoveView(View):
    status = state("status")
    que = state("que")
    sheet = state("sheet")
    complete = state("complete")

    def __init__(self, future, ctx):
        super().__init__()
        self.future = future
        self.ctx = ctx
        self.status = None
        self.que = "スプレッドシートを更新してください。"
        self.sheet = "スプレッドシート"
        self.complete = "更新完了"

    async def done(self, interaction: discord.Interaction):
        self.future.set_result(True)
        self.status = True
        self.que = "更新済み"
        self.complete = "更新されました"
        await interaction.response.defer()
        return

    async def body(self) -> Message:
        embed_list = []
        embed = discord.Embed(
            title=self.que,
            description="メンバー継続停止が通知されました。",
            color=15767485,
            url=self.ctx.message.jump_url,
            timestamp=self.ctx.message.created_at,
        )
        embed.set_author(
            name=self.ctx.message.author.display_name,
            icon_url=self.ctx.message.author.avatar.url,
        )
        embed.add_field(name="送信者", value=f"{self.ctx.message.author.mention}")
        embed.add_field(
            name="受信日時",
            value=f"{self.ctx.message.created_at.astimezone(jst):%Y/%m/%d %H:%M:%S}",
        )
        embed_list.append(embed)
        return Message(
            embeds=embed_list,
            components=[
                Button(self.sheet)
                .style(discord.ButtonStyle.link)
                .disabled(self.status is not None)
                .url(os.environ["MEMBERSHIP_SPREADSHEET"]),
                Button(self.complete)
                .style(discord.ButtonStyle.green)
                .disabled(self.status is not None)
                .on_click(self.done),
            ],
        )
