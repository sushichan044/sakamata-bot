import os

import discord
from discord.ext import commands

from . import embed_builder as EB
from .confirm import Confirm
from .log_sender import LogSender as LS

admin_role = int(os.environ["ADMIN_ROLE"])

dm_box_channel = int(os.environ["DM_BOX_CHANNEL"])


class DM_Sys(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="send-dm")
    @commands.has_role(admin_role)
    async def _send_dm(
        self, ctx: commands.Context, user: discord.Member, *, arg: str
    ) -> None:
        """DM送信用"""
        role = ctx.guild.get_role(admin_role)
        confirm_msg = f"【DM送信確認】\n以下のDMを{user.mention}へ送信します。"
        exe_msg = f"{user.mention}にDMを送信しました。"
        non_exe_msg = f"{user.mention}へのDM送信をキャンセルしました。"
        confirm_arg = f"\n{arg}\n------------------------"
        result = await Confirm(self.bot).confirm(ctx, confirm_arg, role, confirm_msg)
        if result:
            msg = exe_msg
            message = await user.send(arg)
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

    def make_deal_dm(self, deal: str, add_dm: str) -> str:
        DM_content = f"""【あなたは{deal}されました】
    クロヱ水族館/Chloeriumの管理者です。

    あなたのサーバーでの行為がサーバールールに違反していると判断し、{deal}しました。
    {add_dm}"""
        return DM_content

    @commands.Cog.listener("on_message")
    async def on_message_dm(self, message: discord.Message) -> None:
        avoid_dm_list = ["//check", "//remove-member"]
        if (
            type(message.channel) == discord.DMChannel
            and self.bot.user == message.channel.me
        ):
            if message.author.bot:
                return
            else:
                for word in avoid_dm_list:
                    if message.content.startswith(word):
                        return
                channel = self.bot.get_channel(dm_box_channel)
                embeds = []
                if message.content or message.attachments:
                    embed = EB.compose_embed_dm_box(message)
                    embeds.append(embed)
                    for attachment in message.attachments[1:]:
                        embed = discord.Embed(
                            color=3447003,
                        )
                        embed.set_image(url=attachment.proxy_url)
                        embeds.append(embed)
                for embed in message.embeds:
                    embeds.append(embed)
                await channel.send(embeds=embeds)
                return
        else:
            return


def setup(bot):
    return bot.add_cog(DM_Sys(bot))
