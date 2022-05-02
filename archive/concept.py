import asyncio
import os
import random
from datetime import datetime, timedelta, timezone
from typing import Tuple

import discord
from discord import Embed, Member, User
from discord.commands import permissions, slash_command
from discord.ext import commands
from discord.ext.ui import (
    Button,
    InteractionProvider,
    Message,
    MessageProvider,
    View,
    ViewTracker,
    state,
)

from archive.connect import connect
from Cogs.embed_builder import EmbedBuilder as EB

guild_id = int(os.environ["GUILD_ID"])
utc = timezone.utc
jst = timezone(timedelta(hours=9), "Asia/Tokyo")
conn = connect()
server_member_role = int(os.environ["SERVER_MEMBER_ROLE"])


class Concept(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @slash_command(guild_ids=[guild_id], name="concept")
    @permissions.has_role(server_member_role)
    async def _operate_game(self, ctx: discord.ApplicationContext) -> None:
        session_id: int = ctx.interaction.id
        print(f"Start Session: {session_id}")
        view = CloseButton(ctx, session_id)
        tracker = ViewTracker(view, timeout=None)
        await tracker.track(InteractionProvider(ctx.interaction, ephemeral=True))
        conn.set(f"{session_id}.status", "open", ex=1200)
        # get all players
        all_players = await self._send_invite(ctx, session_id)
        if len(all_players) >= 2:
            pass
        else:
            await ctx.interaction.followup.send(
                "参加者が不足しているか\n募集がキャンセルされたため\n進行を停止しました。", ephemeral=True
            )
            return
        # select master and players
        master = random.choice(all_players)
        players = [player for player in all_players if player != master]
        # create game thread and invite all players
        if ctx.interaction.guild.premium_tier >= 2:
            game_thread = await ctx.interaction.channel.create_thread(
                name=f"Concept (Session ID {session_id})",
                message=None,
                auto_archive_duration=1440,
                type=discord.ChannelType.private_thread,
            )
        else:
            game_thread = await ctx.interaction.channel.create_thread(
                name=f"Concept (Session ID {session_id})",
                message=None,
                auto_archive_duration=1440,
                type=discord.ChannelType.public_thread,
            )
        for player in all_players:
            await game_thread.add_user(player)
        # create master thread and invite master
        if ctx.interaction.guild.premium_tier >= 2:
            master_thread = await ctx.interaction.channel.create_thread(
                name=f"[親専用スレッド] Concept (Session ID {session_id})",
                message=None,
                auto_archive_duration=1440,
                type=discord.ChannelType.private_thread,
            )
        else:
            master_thread = await ctx.interaction.channel.create_thread(
                name=f"[親専用スレッド] Concept (Session ID {session_id})",
                message=None,
                auto_archive_duration=1440,
                type=discord.ChannelType.public_thread,
            )
        await master_thread.add_user(master)
        print("Invitation Completed")
        # start game
        await self._game_body(master, players, game_thread, master_thread, session_id)
        return

    # return player list
    async def _send_invite(
        self, ctx: discord.ApplicationContext, session_id: int
    ) -> list[Member]:
        channel = ctx.interaction.channel
        start_time = discord.utils.utcnow()
        exp_time = start_time + timedelta(minutes=5.0)
        view = JoinButton(ctx, start_time, exp_time)
        tracker = ViewTracker(view, timeout=300)
        await tracker.track(MessageProvider(channel))
        for i in range(300):
            if conn.get(f"{session_id}.status") == "open":
                await asyncio.sleep(1)
            else:
                break
        conn.set(f"{session_id}.status", "ongoing", ex=10800)
        """
        message_id: [user_id, user_id...]
        """
        ids = conn.smembers(str(tracker.message.id))
        print(ids)
        players = [await ctx.interaction.guild.fetch_member(id) for id in ids]
        conn.delete(str(tracker.message.id))
        target = tracker.message.embeds[0]
        target.title = "この募集は終了しました。"
        await tracker.message.edit(embeds=[target], view=None)
        return players

    # Game Body

    async def _game_body(
        self,
        master: Member,
        players: list[Member],
        game_thread: discord.Thread,
        master_thread: discord.Thread,
        session_id: int,
    ):
        answer_word = await self.catch_answer(
            master, game_thread, master_thread, session_id
        )

        def detect_answer(message):
            return (
                message.author.id != self.bot.user.id
                and message.author.id
                in [member.id for member in message.channel.members]
                and message.content == answer_word
            )

        answer_msg: discord.Message = await self.bot.wait_for(
            "message", check=detect_answer
        )
        end_embed, master_embed = _end_game_game_thread(
            answer_word, answer_msg.author, master
        )
        end_game_game_thread = _set_session_id(end_embed, session_id)
        await game_thread.send(embed=end_game_game_thread)
        await master_thread.send(embed=master_embed)
        await game_thread.send("このスレッドは2分後にロックされます。")
        await master_thread.send("このスレッドは2分後にロックされます。")
        lock_time = discord.utils.utcnow() + timedelta(seconds=120)
        for i in range(120):
            if lock_time > discord.utils.utcnow():
                await asyncio.sleep(1)
            else:
                break
        await game_thread.archive(locked=True)
        await master_thread.archive(locked=True)
        print(f"Completed Session: {str(session_id)}")
        conn.delete(f"{session_id}.status")
        return

    # set_answer

    async def catch_answer(
        self,
        master: Member,
        game_thread: discord.Thread,
        master_thread: discord.Thread,
        session_id: int,
    ) -> str:
        game_msg_1 = _set_session_id(EB()._concept_start(master), session_id)
        await game_thread.send(embed=game_msg_1)
        master_msg_1 = _set_session_id(EB()._concept_start_parent(master), session_id)
        word_target = await master_thread.send(embed=master_msg_1)

        def _catch_answer(message):
            return (
                message.author.id != self.bot.user.id
                and message.author.id == master.id
                and message.reference
                and message.reference.message_id == word_target.id
            )

        answer_word_msg: discord.Message = await self.bot.wait_for(
            "message", check=_catch_answer
        )
        master_msg_2 = _set_session_id(
            EB()._concept_set_answer_embed(
                game_thread, answer_word_msg.content, master
            ),
            session_id,
        )
        await master_thread.send(embed=master_msg_2)
        game_msg_2 = _set_session_id(EB()._concept_set_answer_embed_game(), session_id)
        await game_thread.send(embed=game_msg_2)
        return answer_word_msg.content


# 進行用Embeds


def _end_game_game_thread(
    answer_word: str, winner: Member | User, master: Member
) -> Tuple[Embed, Embed]:
    if winner.id == master.id:
        embed = Embed(
            title="ギブアップが行われました。",
            color=15767485,
        )
        master_embed = Embed(
            title="ギブアップが行われました。",
            description="次はもっとわかりやすいお題に\nすると良いかもしれません。",
            color=15767485,
        )
    else:
        embed = Embed(
            title="回答が入力されました。",
            description=f"勝者は{winner.mention}さんです！",
            color=15767485,
        )
        master_embed = Embed(
            title="ゲームが完了しました。",
            description="楽しんでいただけたなら幸いです！",
            color=15767485,
        )
    embed.add_field(name="回答", value=f"||{answer_word}||")
    return embed, master_embed


def _set_session_id(embed: Embed, session_id: int) -> Embed:
    embed.set_footer(text=f"Session ID: {str(session_id)}")
    return embed


# 募集締め切り用ボタン


class CloseButton(View):
    status = state("status")
    l_str = state("l_str")
    r_str = state("r_str")
    text = state("text")
    title = state("title")

    def __init__(self, ctx, session_id: int):
        super().__init__()
        self.ctx = ctx
        self.l_str = "締め切り"
        self.r_str = "取り消し"
        self.status = None
        self.title = "募集を開始しました。"
        self.text = "締め切る際は締め切りボタンを押してください。\n締め切りボタンが押されなかった場合、\n5分後に自動で締め切られます。\n\n募集をキャンセルする場合は\n参加者が0人か1人の状態で\n締め切りボタンを押してください。"
        self.session_id = session_id

    async def _ok(self, interaction: discord.Interaction):
        self.status = True
        self.title = "募集を締め切りました。"
        self.text = "このメッセージを消去してスレッドでゲームを開始してください。"
        conn.set(f"{self.session_id}.status", "close", ex=1200)
        self.stop()

    async def _ng(self, interaction: discord.Interaction):
        self.status = False
        self.title = "募集を取り消しました。"
        self.text = "このメッセージを消去してください。"
        self.stop()

    async def body(self) -> Message:
        return Message(
            embeds=[
                Embed(
                    title=self.title,
                    description=self.text,
                    color=15767485,
                ),
            ],
            components=[
                Button(self.l_str)
                .style(discord.ButtonStyle.blurple)
                .disabled(self.status is not None)
                .on_click(self._ok),
            ],
        )


"""
Button(self.r_str).style(discord.ButtonStyle.red).disabled(
    self.status is not None).on_click(self._ng)
"""

# 参加用ボタン


class JoinButton(View):
    status = state("status")
    title = state("title")
    label = state("label")

    def __init__(self, ctx, start: datetime, exp: datetime):
        super().__init__()
        self.ctx = ctx
        self.label = "参加"
        self.status = None
        self.start = start
        self.exp = exp

    async def _ok(self, interaction: discord.Interaction):
        if not str(interaction.user.id) in conn.smembers(str(interaction.message.id)):
            conn.sadd(str(interaction.message.id), str(interaction.user.id))
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "参加登録を行いました！\n開始までしばらくお待ちください！", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    content="参加登録を行いました！\n開始までしばらくお待ちください！", ephemeral=True
                )
            return
        else:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "既に参加登録したユーザーです。", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    content="既に参加登録したユーザーです。", ephemeral=True
                )

    async def body(self) -> Message:
        exp_str = self.exp.astimezone(jst).strftime("%Y/%m/%d %H:%M:%S")
        embed = Embed(
            title="募集が開始されました。",
            description=f"有効期限:{exp_str}",
            color=15767485,
        )
        embed.set_author(
            name=self.ctx.interaction.user,
            icon_url=self.ctx.interaction.user.display_avatar.url,
        )
        return Message(
            embeds=[embed],
            components=[
                Button(self.label)
                .style(discord.ButtonStyle.blurple)
                .disabled(self.status is not None)
                .on_click(self._ok),
            ],
        )


"""
定義:

1.チャンネルで開始コマンドを実行。
2.募集を開始(未定)
3.参加者のみのスレッドを親チャンネルから作成してゲームを進行
4.募集ちゃんねるに募集中のゲームと進行中のゲームが出せたらいいね
"""


def setup(bot):
    return bot.add_cog(Concept(bot))
