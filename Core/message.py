import os

import discord
from discord.ext import commands
from newdispanderfixed import dispand

from Core.confirm import Confirm
from Core.log_sender import LogSender as LS

admin_role = int(os.environ["ADMIN_ROLE"])


class Message_Sys(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message_dispand(self, message: discord.Message):
        avoid_word_list_prefix = ["//send-message", "//edit-message", "//send-dm"]
        if type(message.channel) == discord.DMChannel:
            return
        else:
            for word in avoid_word_list_prefix:
                if message.content.startswith(word):
                    return
            if message.content.endswith("中止に必要な承認人数: 1"):
                return
            else:
                await dispand(message)
                return

    @commands.command(name="send-message")
    @commands.has_role(admin_role)
    async def _messagesend(self, ctx: commands.Context, channel_id: int, *, arg: str):
        """メッセージ送信用"""
        # channel:送信先
        channel = self.bot.get_channel(channel_id)
        # role:承認可能ロール
        role = ctx.guild.get_role(admin_role)
        confirm_msg = f"【メッセージ送信確認】\n以下のメッセージを{channel.mention}へ送信します。"
        exe_msg = f"{channel.mention}にメッセージを送信しました。"
        non_exe_msg = f"{channel.mention}へのメッセージ送信をキャンセルしました。"
        confirm_arg = f"\n{arg}\n------------------------"
        result = await Confirm(self.bot).confirm(ctx, confirm_arg, role, confirm_msg)
        if result:
            msg = exe_msg
            message = await channel.send(arg)
            desc_url = message.jump_url
            await ctx.send("Sended!")
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return
        else:
            msg = non_exe_msg
            desc_url = ""
            await ctx.send("Cancelled!")
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return

    @commands.command(name="edit-message")
    @commands.has_role(admin_role)
    async def _editmessage(
        self, ctx: commands.Context, channel_id: int, message_id: int, *, arg: str
    ):
        """メッセージ編集用"""
        channel = self.bot.get_channel(channel_id)
        role = ctx.guild.get_role(admin_role)
        target = await channel.fetch_message(message_id)
        msg_url = (
            f"https://discord.com/channels/{ctx.guild.id}/{channel_id}/{message_id}"
        )
        confirm_msg = f"【メッセージ編集確認】\n{channel.mention}のメッセージ\n{msg_url}\nを以下のように編集します。"
        exe_msg = f"{channel.mention}のメッセージを編集しました。"
        non_exe_msg = f"{channel.mention}のメッセージの編集をキャンセルしました。"
        confirm_arg = f"\n{arg}\n------------------------"
        result = await Confirm(self.bot).confirm(ctx, confirm_arg, role, confirm_msg)
        if result:
            msg = exe_msg
            await target.edit(content=arg)
            desc_url = msg_url
            await ctx.send("Edited!")
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return
        else:
            msg = non_exe_msg
            desc_url = ""
            await ctx.send("Cancelled!")
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return


def setup(bot):
    return bot.add_cog(Message_Sys(bot))
