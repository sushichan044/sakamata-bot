import os
from datetime import datetime, timedelta, timezone

import discord
from discord import ApplicationContext
from discord.commands import user_command
from discord.ext import commands
from dotenv import load_dotenv

from Core.confirm import Confirm
from Core.dm import DM_Sys as DS
from Core.log_sender import LogSender as LS

load_dotenv()

utc = timezone.utc
jst = timezone(timedelta(hours=9), "Asia/Tokyo")

guild_id = int(os.environ["GUILD_ID"])

mod_role = int(os.environ["MOD_ROLE"])
admin_role = int(os.environ["ADMIN_ROLE"])

log_channel = int(os.environ["LOG_CHANNEL"])


class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @user_command(guild_ids=[guild_id], name="緊急タイムアウト")
    # user commands return the member
    async def _emergency_timeout(self, ctx: ApplicationContext, member: discord.Member):
        await member.timeout_for(duration=timedelta(days=1), reason="Emergency Timeout")
        await ctx.respond(f"{member.mention}を緊急タイムアウトしました。", ephemeral=True)
        msg = f"{member.mention}を緊急タイムアウトしました。"
        desc_url = ""
        until = datetime.now(jst) + timedelta(days=1)
        until_str = until.strftime("%Y/%m/%d %H:%M:%S")
        await LS(self.bot).send_context_timeout_log(ctx, msg, desc_url, until_str)
        return

    @commands.command(name="timeout")
    @commands.has_role(mod_role)
    async def _timeout(
        self,
        ctx: commands.Context,
        member: discord.Member,
        input_until: str,
        if_dm: str = "dm:true",
    ):
        """メンバーをタイムアウト"""
        until = datetime.strptime(input_until, "%Y%m%d")
        until_jst = until.replace(tzinfo=jst)
        role = ctx.guild.get_role(mod_role)
        valid_if_dm_list = ["dm:true", "dm:false"]
        until_str = until_jst.strftime("%Y/%m/%d/%H:%M")
        if if_dm not in valid_if_dm_list:
            await ctx.reply(
                content="不明な引数を検知したため処理を終了しました。\nDM送信をOFFにするにはFalseを指定してください。",
                mention_author=False,
            )
            msg = "不明な引数を検知したため処理を終了しました。"
            desc_url = ""
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return
        else:
            deal = "timeout"
            add_dm = f"あなたは{until_str}までサーバーでの発言とボイスチャットへの接続を制限されます。"
            DM_content = DS(self.bot).make_deal_dm(deal, add_dm)
            if if_dm == "dm:false":
                DM_content = ""
            else:
                pass
            confirm_msg = f"【timeout実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{member}(ID:{member.id})\n期限:{until_str}\nDM送信:{if_dm}\nDM内容:{DM_content}"
            exe_msg = f"{member.mention}をタイムアウトしました。"
            non_exe_msg = f"{member.mention}のタイムアウトをキャンセルしました。"
            confirm_arg = ""
            result = await Confirm(self.bot).confirm(
                ctx, confirm_arg, role, confirm_msg
            )
            if result:
                msg = exe_msg
                if if_dm == "dm:true":
                    sent_dm = await member.send(DM_content)
                    desc_url = sent_dm.jump_url
                    await member.timeout(until_jst.astimezone(utc), reason=None)
                    await ctx.send("timeouted!")
                    await LS(self.bot).send_timeout_log(ctx, msg, desc_url, until_str)
                    return
                elif if_dm == "dm:false":
                    desc_url = ""
                    await member.timeout(until_jst.astimezone(utc), reason=None)
                    await ctx.send("timeouted!")
                    await LS(self.bot).send_timeout_log(ctx, msg, desc_url, until_str)
                    return
                else:
                    return
            else:
                msg = non_exe_msg
                desc_url = ""
                await LS(self.bot).send_exe_log(ctx, msg, desc_url)
                await ctx.send("Cancelled!")
                return

    @commands.command(name="untimeout")
    @commands.has_role(admin_role)
    async def _untimeout(self, ctx: commands.Context, member: discord.Member):
        """メンバーのタイムアウトを解除"""
        role = ctx.guild.get_role(admin_role)
        confirm_msg = f"【untimeout実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{member}(ID:{member.id})"
        exe_msg = f"{member.mention}のタイムアウトを解除しました。"
        non_exe_msg = f"{member.mention}のタイムアウトの解除をキャンセルしました。"
        confirm_arg = ""
        result = await Confirm(self.bot).confirm(ctx, confirm_arg, role, confirm_msg)
        if result:
            msg = exe_msg
            desc_url = ""
            await member.remove_timeout(reason=None)
            await ctx.send("untimeouted!")
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return
        else:
            msg = non_exe_msg
            desc_url = ""
            await ctx.send("Cancelled!")
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return

    @commands.Cog.listener("on_member_update")
    async def _on_member_untimeout(self, before: discord.Member, after: discord.Member):
        if before.timed_out and not after.timed_out:
            channel = self.bot.get_channel(log_channel)
            embed = discord.Embed(
                title="Timeout 解除通知",
                color=3447003,
                description=f"{after.mention}のタイムアウトが終了しました。",
                timestamp=datetime.now(),
            )
            await channel.send(embed=embed)
            return


def setup(bot):
    return bot.add_cog(Timeout(bot))
