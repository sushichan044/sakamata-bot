import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from Core.confirm import Confirm
from Core.dm import DM_Sys as DS
from Core.log_sender import LogSender as LS

load_dotenv()

admin_role = int(os.environ["ADMIN_ROLE"])


class Kick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="kick")
    @commands.has_role(admin_role)
    async def _kick_user(
        self, ctx: commands.Context, member: discord.Member, if_dm: str = "dm:true"
    ):
        """メンバーをキック"""
        role = ctx.guild.get_role(admin_role)
        valid_if_dm_list = ["dm:true", "dm:false"]
        if if_dm not in valid_if_dm_list:
            await ctx.reply(
                content="不明な引数を検知したため処理を終了しました。\nDM送信をOFFにするにはdm:falseを指定してください。",
                mention_author=False,
            )
            msg = "不明な引数を検知したため処理を終了しました。"
            desc_url = ""
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return
        else:
            deal = "kick"
            add_dm = ""
            DM_content = DS(self.bot).make_deal_dm(deal, add_dm)
            if if_dm == "dm:false":
                DM_content = ""
            else:
                pass
            confirm_msg = f"【kick実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{member}(ID:{member.id})\nDM送信:{if_dm}\nDM内容:{DM_content}"
            exe_msg = f"{member.mention}をキックしました。"
            non_exe_msg = f"{member.mention}のキックをキャンセルしました。"
            confirm_arg = ""
            result = await Confirm(self.bot).confirm(
                ctx, confirm_arg, role, confirm_msg
            )
            if result:
                msg = exe_msg
                if if_dm == "dm:true":
                    sent_dm = await member.send(DM_content)
                    desc_url = sent_dm.jump_url
                    await member.kick(reason=None)
                    await ctx.send("kicked!")
                    await LS(self.bot).send_exe_log(ctx, msg, desc_url)
                    return
                elif if_dm == "dm:false":
                    desc_url = ""
                    await member.kick(reason=None)
                    await ctx.send("kicked!")
                    await LS(self.bot).send_exe_log(ctx, msg, desc_url)
                    return
                else:
                    return
            else:
                msg = non_exe_msg
                desc_url = ""
                await LS(self.bot).send_exe_log(ctx, msg, desc_url)
                await ctx.send("Cancelled!")
                return


def setup(bot):
    return bot.add_cog(Kick(bot))
