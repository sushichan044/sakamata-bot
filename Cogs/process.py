import asyncio
import os
import random
from datetime import datetime, timedelta, timezone

from discord import User, embeds

import discord
from discord import Member, Embed
from discord.commands import slash_command
from discord.ext import commands
from discord.ext.ui import (Button, InteractionProvider, Message,
                            MessageProvider, View, ViewTracker, state)

from Cogs.connect import connect

guild_id = int(os.environ['GUILD_ID'])
process_channel = int(os.environ['PROCESS_CATEGORY'])
utc = timezone.utc
jst = timezone(timedelta(hours=9), 'Asia/Tokyo')
conn = connect()


class Process(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @slash_command(guild_ids=[guild_id], name='process')
    async def _operate_game(self, ctx: discord.ApplicationContext) -> None:
        session_id: int = ctx.interaction.id
        view = CloseButton(ctx, session_id)
        tracker = ViewTracker(view, timeout=None)
        await tracker.track(InteractionProvider(ctx.interaction, ephemeral=True))
        conn.set(f'{session_id}.status', 'open', ex=1200)
        # get all players
        all_players = await self._send_invite(ctx, session_id)
        # select master and players
        master = random.choice(all_players)
        players = [player for player in all_players if player != master]
        # create game thread and invite all players
        game_thread = await ctx.interaction.channel.create_thread(name=f'Process (Session ID:{session_id})', message=None, auto_archive_duration=1440, type=discord.ChannelType.public_thread)
        for player in all_players:
            await game_thread.add_user(player)
        # create master thread and invite master
        master_thread = await ctx.interaction.channel.create_thread(name=f'[親専用スレッド] Process (Session ID:{session_id})', message=None, auto_archive_duration=1440, type=discord.ChannelType.public_thread)
        await master_thread.add_user(master)
        print('Invitation Completed')
        # start game
        await self._game_body(master, players, game_thread, master_thread, session_id)
        return

    # return player list
    async def _send_invite(self, ctx: discord.ApplicationContext, session_id: int) -> list[Member]:
        print('launched')
        channel = ctx.interaction.channel
        start_time = discord.utils.utcnow()
        exp_time = start_time + timedelta(minutes=10.0)
        view = JoinButton(ctx, start_time, exp_time)
        tracker = ViewTracker(view, timeout=30)
        await tracker.track(MessageProvider(channel))
        for i in range(30):
            if conn.get(f'{session_id}.status') == 'open':
                await asyncio.sleep(1)
            else:
                break
        """
        message_id: [user_id, user_id...]
        """
        ids = conn.smembers(str(tracker.message.id))
        print(ids)
        players = [await ctx.interaction.guild.fetch_member(id) for id in ids]
        conn.delete(str(tracker.message.id))
        target = tracker.message.embeds[0]
        target.title = 'この募集は終了しました。'
        await tracker.message.edit(embeds=[target], view=None)
        return players

    # Game Body

    async def _game_body(self, master: Member, players: list[Member], game_thread: discord.Thread, master_thread: discord.Thread, session_id: int):
        answer_word = await self.catch_answer(master, game_thread, master_thread, session_id)

        def detect_answer(message):
            return message.author != self.bot.user and message.content == answer_word and message.author in players
        answer_msg: discord.Message = await self.bot.wait_for('message', check=detect_answer)
        end_game_game_thread = _set_session_id(
            _end_game_game_thread(answer_word, answer_msg.author), session_id)
        await game_thread.send(embed=end_game_game_thread)
        return

    # set_answer

    async def catch_answer(self, master: Member, game_thread: discord.Thread, master_thread: discord.Thread, session_id: int) -> str:
        master_msg_1 = _set_session_id(
            _start_embed(master, game_thread), session_id)
        word_target = await master_thread.send(master.mention, embed=master_msg_1)

        def _catch_answer(message):
            return message.author != self.bot.user and message.reference and message.reference.message_id == word_target.id
        answer_word_msg = await self.bot.wait_for('message', check=_catch_answer)
        master_msg_2 = _set_session_id(_set_answer_embed(
            game_thread, answer_word_msg.content), session_id)
        await master_thread.send(embed=master_msg_2)
        return answer_word_msg.content


# 進行用Embeds

def _start_embed(master: Member, game_thread: discord.Thread) -> Embed:
    embed = Embed(
        title='Processへようこそ。',
        description=f'{master.mention}さんは親に選ばれました。\n回答にする単語をこのメッセージに__返信__してください。',
        color=15767485,
    )
    return embed


def _set_answer_embed(game_thread: discord.Thread, answer_word: str) -> Embed:
    embed = Embed(
        title='回答をセットしました。',
        description=f'セットされた回答: {answer_word}\n{game_thread.mention}でゲームを開始してください。',
        color=15767485,
    )
    return embed


def _rule_embed_player():
    pass


def _rule_embed_master():
    pass


def _end_game_game_thread(answer_word: str, winner: Member | User) -> Embed:
    embed = Embed(
        title='回答が入力されました。',
        description=f'勝者は{winner.mention}さんです！',
        color=15767485,
    )
    embed.add_field(
        name='回答',
        value=f'||{answer_word}||'
    )
    return embed


def _set_session_id(embed: Embed, session_id: int) -> Embed:
    embed.set_footer(
        text=f'Session ID: {str(session_id)}'
    )
    return embed

# 募集締め切り用ボタン


class CloseButton(View):
    status = state('status')
    l_str = state('l_str')
    r_str = state('r_str')
    text = state('text')
    title = state('title')

    def __init__(self, ctx, session_id: int):
        super().__init__()
        self.ctx = ctx
        self.l_str = '締め切り'
        self.r_str = '取り消し'
        self.status = None
        self.title = '募集を開始しました。'
        self.text = '締め切る際は締め切りボタンを押してください。\n締め切りボタンが押されなかった場合、10分後に自動で締め切られます。'
        self.session_id = session_id

    async def _ok(self, interaction: discord.Interaction):
        self.status = True
        self.title = '募集を締め切りました。'
        self.text = 'このメッセージを消去してスレッドでゲームを開始してください。'
        conn.set(f'{self.session_id}.status', 'close', ex=1200)
        self.stop()

    async def _ng(self, interaction: discord.Interaction):
        self.status = False
        self.title = '募集を取り消しました。'
        self.text = 'このメッセージを消去してください。'
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
                Button(self.l_str).style(discord.ButtonStyle.blurple).disabled(
                    self.status is not None).on_click(self._ok),
            ]
        )


"""
Button(self.r_str).style(discord.ButtonStyle.red).disabled(
    self.status is not None).on_click(self._ng)
"""

# 参加用ボタン


class JoinButton(View):
    status = state('status')
    title = state('title')
    label = state('label')

    def __init__(self, ctx, start: datetime, exp: datetime):
        super().__init__()
        self.ctx = ctx
        self.label = '参加'
        self.status = None
        self.start = start
        self.exp = exp

    async def _ok(self, interaction: discord.Interaction):
        if not str(interaction.user.id) in conn.smembers(str(interaction.message.id)):
            conn.sadd(str(interaction.message.id), str(interaction.user.id))
            if not interaction.response.is_done():
                await interaction.response.send_message('参加登録を行いました！\n開始までしばらくお待ちください！', ephemeral=True)
            else:
                await interaction.followup.send(content='参加登録を行いました！\n開始までしばらくお待ちください！', ephemeral=True)
            return
        else:
            if not interaction.response.is_done():
                await interaction.response.send_message('既に参加登録したユーザーです。', ephemeral=True)
            else:
                await interaction.followup.send(content='既に参加登録したユーザーです。', ephemeral=True)

    async def body(self) -> Message:
        exp_str = self.exp.astimezone(jst).strftime('%Y/%m/%d %H:%M:%S')
        embed = Embed(
            title='募集が開始されました。',
            description=f'有効期限:{exp_str}',
            color=15767485,
        )
        embed.set_author(
            name=self.ctx.interaction.user,
            icon_url=self.ctx.interaction.user.avatar.url
        )
        return Message(
            embeds=[embed],
            components=[
                Button(self.label).style(discord.ButtonStyle.blurple).disabled(
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
