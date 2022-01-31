import os
from datetime import timedelta, timezone

import discord
from discord import Option, permissions
from discord.commands import slash_command
from discord.ext import commands
from discord.ext.ui import (
    Button,
    InteractionProvider,
    Message,
    View,
    ViewTracker,
    state,
)

thread_log_channel = int(os.environ["THREAD_LOG_CHANNEL"])
jst = timezone(timedelta(hours=9), "Asia/Tokyo")
mod_role = int(os.environ["MOD_ROLE"])
admin_role = int(os.environ["ADMIN_ROLE"])
guild_id = int(os.environ["GUILD_ID"])


class Thread(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_thread_join")
    async def detect_thread(self, thread):
        thread_member_list = await thread.fetch_members()
        if self.bot.user.id in [x.id for x in thread_member_list]:
            return
        else:
            channel = self.bot.get_channel(thread_log_channel)
            embed = await self.compose_thread_create_log(thread)
            await channel.send(embed=embed)
            return

    @commands.Cog.listener(name="on_thread_update")
    async def detect_archive(self, before, after):
        if after.locked and not before.locked:
            return
        elif after.archived and not before.archived:
            await after.edit(archived=False)
            return
        else:
            return

    """
    Thread Board Parts
    normal
    ┣

    bottom
    ┗
    """

    @slash_command(guild_ids=[guild_id], name="board")
    @permissions.has_role(admin_role)
    async def _board_slash(
        self,
        ctx,
        category: Option(discord.CategoryChannel, "対象のカテゴリを選択してください。"),
    ):
        board = self._make_board(ctx.interaction, category.id)
        print(board)
        # await ctx.respond('Done', ephemeral=True)
        view = EscapeButton(board)
        tracker = ViewTracker(view, timeout=None)
        await tracker.track(InteractionProvider(ctx.interaction))
        return

    @commands.command(name="thread_board")
    @commands.has_role(admin_role)
    async def _thread(self, ctx):
        text = self._make_board(ctx, ctx.message.channel.category.id)
        await ctx.send(text)
        return

    def _make_board(self, ctx, category_id: int) -> str:
        channels = [
            channel
            for channel in ctx.guild.channels
            if channel.category and channel.category.id == category_id
        ]
        sort_channels = sorted(channels, key=lambda channel: channel.position)
        # print(channels)
        thread_dic = {}
        threads = [
            thread
            for thread in ctx.guild.threads
            if not thread.is_private()
            and not thread.locked
            and thread.parent.category.id == category_id
        ]
        # print(threads)
        for thread in threads:
            thread_dic[thread] = thread.parent.position
        """
        thread_dic:
        {thread:pos,
        thread:pos,
        ...}
        """
        final_board = []
        for channel in sort_channels:
            thread_board = [f"<#{channel.id}>"]
            child_thread = sorted(
                [
                    f"<#{thread.id}>"
                    for thread, parent in thread_dic.items()
                    if parent == channel.position
                ],
                key=lambda thread: len(thread.name),
            )
            if child_thread:
                board = thread_board + child_thread
                board_text_draft = "\n┣".join(board[:-1])
                board_text = f"{board_text_draft}\n┗{board[-1]}"
                final_board.append(board_text)
            else:
                final_board.append(f"<#{channel.id}>")
        final_text = "\n\n".join(final_board)
        return final_text

    async def compose_thread_create_log(self, thread):
        embed = discord.Embed(
            title="スレッドが作成されました。",
            url="",
            color=3447003,
            description="",
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(
            name=thread.owner.display_name,
            icon_url=thread.owner.display_avatar.url,
        )
        embed.add_field(name="作成元チャンネル", value=f"{thread.parent.mention}")
        embed.add_field(name="作成スレッド", value=f"{thread.mention}")
        embed.add_field(name="作成者", value=f"{thread.owner.mention}")
        embed.add_field(
            name="作成日時",
            value=f"{discord.utils.utcnow().astimezone(jst):%Y/%m/%d %H:%M:%S}",
        )
        return embed


class EscapeButton(View):
    status = state("status")
    text = state("text")

    def __init__(self, text: str):
        super().__init__()
        self.text = text
        self.l_str = "OK"
        self.r_str = "取り消し"
        self.status = None

    async def _ok(self, interaction: discord.Interaction):
        self.status = True
        self.text = f"```{self.text}```"
        self.stop()
        return

    async def _ng(self, interaction: discord.Interaction):
        self.status = False
        await interaction.message.delete()
        self.stop()
        return

    async def body(self) -> Message:
        return Message(
            content=self.text,
            embeds=[
                discord.Embed(
                    title="スレッド一覧プレビュー",
                    description="この内容で更新用メッセージを送信しますか？",
                    color=15767485,
                ),
            ],
            components=[
                Button(self.l_str)
                .style(discord.ButtonStyle.green)
                .disabled(self.status is not None)
                .on_click(self._ok),
                Button(self.r_str)
                .style(discord.ButtonStyle.red)
                .disabled(self.status is not None)
                .on_click(self._ng),
            ],
        )


def setup(bot):
    return bot.add_cog(Thread(bot))
