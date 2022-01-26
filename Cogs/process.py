import asyncio
import os

import discord
from discord.commands import slash_command
from discord.ext import commands
from discord.ext.ui import (Button, InteractionProvider, Message, View,
                            ViewTracker, state)

guild_id = int(os.environ['GUILD_ID'])
process_channel = int(os.environ['PROCESS_CATEGORY'])


class Process(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[guild_id], name='process')
    async def _start_game(self, ctx):
        view = JoinButton(ctx)
        tracker = ViewTracker(view, timeout=None)
        await tracker.track(InteractionProvider(ctx.interaction, ephemeral=True))
        return


class JoinButton(View):
    status = state('status')
    l_str = state('l_str')
    r_str = state('r_str')
    text = state('text')
    title = state('title')

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.l_str = '締め切り'
        self.r_str = '取り消し'
        self.status = None
        self.title = '募集を開始しました。'
        self.text = '締め切る際はこのメッセージの締め切りボタンを押してください。\n募集を取り消す場合は取り消しボタンを押してください。'

    async def _ok(self, interaction: discord.Interaction):
        self.status = True
        self.title = '募集を締め切りました。'
        self.text = 'このメッセージを消去してスレッドでゲームを開始してください。'
        self.stop()

    async def _ng(self, interaction: discord.Interaction):
        self.status = False
        self.title = '募集を取り消しました。'
        self.text = 'このメッセージを消去してください。'
        self.stop()

    async def body(self) -> Message:
        return Message(
            embeds=[
                discord.Embed(
                    title=self.title,
                    description=self.text,
                    color=15767485,
                ),
            ],
            components=[
                Button(self.l_str).style(discord.ButtonStyle.blurple).disabled(
                    self.status is not None).on_click(self._ok),
                Button(self.r_str).style(discord.ButtonStyle.red).disabled(
                    self.status is not None).on_click(self._ng)
            ]
        )


class CloseButton(View):
    status = state('status')
    text = state('text')

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.text = '参加'
        self.status = None

    async def body(self) -> Message:
        embed = discord.Embed(
            title='募集を開始しました。',
            description='この内容で更新用メッセージを送信しますか？',
            color=15767485,
        )
        embed.set_author(
            name=self.ctx.author,
            icon_url=self.ctx.message.author.avatar.url
        )
        return Message(
            embeds=[embed],
            components=[
                Button(self.str).style(discord.ButtonStyle.green).disabled(
                    self.status is not None).on_click(self._ok),
            ]
        )


"""
定義:

1.チャンネルで開始コマンドを実行。
2.募集を開始(未定)
3.参加者のみのスレッドを親チャンネルから作成してゲームを進行
4.募集ちゃんねるに募集中のゲームと進行中のゲームが出せたらいいね
"""


def setup(bot):
    return bot.add_cog(Process(bot))
