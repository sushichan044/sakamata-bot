import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from newdispanderfixed import dispand

from Core.confirm import Confirm
from Core.download import download
from Core.log_sender import LogSender as LS

load_dotenv()

admin_role = int(os.environ["ADMIN_ROLE"])


class Message_Sys(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message_dispand(self, message: discord.Message):
        avoid_prefix_list = [
            "//send-message",
            "//edit-message",
            "//send-dm",
            "【メッセージ送信確認】",
            "【メッセージ編集確認】",
        ]
        avoid_suffix_list = []
        if type(message.channel) == discord.DMChannel:
            return
        else:
            for prefix in avoid_prefix_list:
                if message.content.startswith(prefix):
                    return
            for suffix in avoid_suffix_list:
                if message.content.endswith(suffix):
                    return
            else:
                embeds = await dispand(self.bot, message)
                if embeds == []:
                    return
                await message.reply(embeds=embeds, mention_author=False)
                return

    @commands.command(name="send-message")
    @commands.has_role(admin_role)
    async def _send(self, ctx: commands.Context, channel_id: str, *, text: str):
        """メッセージ送信用"""
        channel = self.bot.get_channel(int(channel_id))
        if channel is None:
            channel = await self.bot.fetch_channel(int(channel_id))
        permitted_role = ctx.guild.get_role(admin_role)
        confirm_msg = f"【メッセージ送信確認】\n以下のメッセージを{channel.mention}へ送信します。"
        exe_msg = f"{channel.mention}にメッセージを送信しました。"
        non_exe_msg = f"{channel.mention}へのメッセージ送信をキャンセルしました。"
        confirm_arg = f"\n{text}\n------------------------"
        if ctx.message.attachments:
            files: list[discord.File] = [
                await attachment.to_file() for attachment in ctx.message.attachments
            ]
            result = await Confirm(self.bot).confirm(
                ctx, confirm_arg, permitted_role, confirm_msg, files
            )
        else:
            files = []
            result = await Confirm(self.bot).confirm(
                ctx, confirm_arg, permitted_role, confirm_msg
            )
        if result:
            if files != []:
                names = []
                for attachment in ctx.message.attachments:
                    names.append(attachment.filename)
                    download(attachment.filename, attachment.url)
                print(names)
                # print("complete download")
                sent_files = [
                    discord.File(
                        os.path.join(os.path.dirname(__file__), f"/tmp/{name}"),
                        filename=name,
                        spoiler=False,
                    )
                    for name in names
                ]
                sent_message = await channel.send(content=text, files=sent_files)
                for name in names:
                    os.remove(os.path.join(os.path.dirname(__file__), f"/tmp/{name}"))
            else:
                sent_message = await channel.send(content=text)
            msg = exe_msg
            desc_url = sent_message.jump_url
            await ctx.send("Sended!")
        else:
            msg = non_exe_msg
            desc_url = ""
            await ctx.send("Cancelled!")
        await LS(self.bot).send_exe_log(ctx, msg, desc_url)
        return

    @commands.command(name="edit-message")
    @commands.has_role(admin_role)
    async def _editmessage(
        self, ctx: commands.Context, channel_id: int, message_id: int, *, text: str
    ):
        """メッセージ編集用"""
        channel = self.bot.get_channel(int(channel_id))
        if channel is None:
            channel = await self.bot.fetch_channel(int(channel_id))
        permitted_role = ctx.guild.get_role(admin_role)
        if not permitted_role:
            await ctx.reply("Admin role not found.")
            return
        target = await channel.fetch_message(message_id)
        msg_url = (
            f"https://discord.com/channels/{ctx.guild.id}/{channel_id}/{message_id}"
        )
        confirm_msg = f"【メッセージ編集確認】\n{channel.mention}のメッセージ\n{msg_url}\nを以下のように編集します。"
        exe_msg = f"{channel.mention}のメッセージを編集しました。"
        non_exe_msg = f"{channel.mention}のメッセージの編集をキャンセルしました。"
        confirm_arg = f"\n{text}\n------------------------"
        if ctx.message.attachments:
            files: list[discord.File] = [
                await attachment.to_file() for attachment in ctx.message.attachments
            ]

            result = await Confirm(self.bot).confirm(
                ctx, confirm_arg, permitted_role, confirm_msg, files
            )
        else:
            files = []
            result = await Confirm(self.bot).confirm(
                ctx, confirm_arg, permitted_role, confirm_msg
            )
        if result:
            if files != []:
                names = []
                for attachment in ctx.message.attachments:
                    names.append(attachment.filename)
                    download(attachment.filename, attachment.url)
                # print("complete download")
                sent_files = [
                    discord.File(
                        os.path.join(os.path.dirname(__file__), f"/tmp/{name}"),
                        filename=name,
                        spoiler=False,
                    )
                    for name in names
                ]
                sent_message = await target.edit(
                    content=text, attachments=target.attachments, files=sent_files
                )
                for name in names:
                    os.remove(os.path.join(os.path.dirname(__file__), f"/tmp/{name}"))
                # print("complete delete")
            else:
                sent_message = await target.edit(content=text)
            msg = exe_msg
            desc_url = sent_message.jump_url
            await ctx.send("Edited!")
        else:
            msg = non_exe_msg
            desc_url = ""
            await ctx.send("Cancelled!")
        await LS(self.bot).send_exe_log(ctx, msg, desc_url)
        return


def setup(bot):
    return bot.add_cog(Message_Sys(bot))
