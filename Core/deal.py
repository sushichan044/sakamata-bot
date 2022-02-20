import os
from datetime import datetime, timedelta, timezone

import discord
from discord import ApplicationContext
from discord.commands import permissions, user_command
from discord.ext import commands

from Core.confirm import Confirm
from Core.dm import DM_Sys as DS
from Core.log_sender import LogSender as LS

log_channel = int(os.environ["LOG_CHANNEL"])

utc = timezone.utc
jst = timezone(timedelta(hours=9), "Asia/Tokyo")

guild_id = int(os.environ["GUILD_ID"])

mod_role = int(os.environ["MOD_ROLE"])

admin_role = int(os.environ["ADMIN_ROLE"])


class Dealer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    @commands.has_role(admin_role)
    async def _ban_user(
        self, ctx: commands.Context, member: discord.Member, if_dm: str = "dm:true"
    ):
        """メンバーをBAN"""
        role = ctx.guild.get_role(admin_role)
        valid_list = ["dm:true", "dm:false"]
        if if_dm not in valid_list:
            await ctx.reply(
                content="不明な引数を検知したため処理を終了しました。\nDM送信をOFFにするにはdm:falseを指定してください。",
                mention_author=False,
            )
            msg = "不明な引数を検知したため処理を終了しました。"
            desc_url = ""
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return
        else:
            deal = "BAN"
            add_dm = """
    今後、あなたはクロヱ水族館に参加することはできません。

    BANの解除を希望する場合は以下のフォームをご利用ください。
    クロヱ水族館BAN解除申請フォーム
    https://forms.gle/mR1foEyd9JHbhYdCA
    """
            DM_content = DS(self.bot).make_deal_dm(deal, add_dm)
            if if_dm == "dm:false":
                DM_content = ""
            confirm_msg = f"【BAN実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{member}(ID:{member.id})\nDM送信:{if_dm}\nDM内容:{DM_content}"
            exe_msg = f"{member.mention}をBANしました。"
            non_exe_msg = f"{member.mention}のBANをキャンセルしました。"
            confirm_arg = ""
            result = await Confirm(self.bot).confirm(
                ctx, confirm_arg, role, confirm_msg
            )
            if result is True:
                msg = exe_msg
                if if_dm == "dm:true":
                    sent_dm = await member.send(DM_content)
                    desc_url = sent_dm.jump_url
                    await member.ban(reason=None)
                    await ctx.send("baned!")
                    await LS(self.bot).send_exe_log(ctx, msg, desc_url)
                    return
                elif if_dm == "dm:false":
                    desc_url = ""
                    await member.ban(reason=None)
                    await ctx.send("baned!")
                    await LS(self.bot).send_exe_log(ctx, msg, desc_url)
                    return
                else:
                    return
            else:
                msg = non_exe_msg
                desc_url = ""
                await ctx.send("Cancelled!")
                await LS(self.bot).send_exe_log(ctx, msg, desc_url)
                return

    @commands.command(name="unban")
    @commands.has_role(admin_role)
    async def _unban_user(self, ctx: commands.Context, id: int):
        """ユーザーのBANを解除"""
        user = await self.bot.fetch_user(id)
        role = ctx.guild.get_role(admin_role)
        target = [user for entry in await ctx.guild.bans() if entry.user.id == user.id]
        if not target:
            await ctx.reply("BANリストにないユーザーを指定したため処理を停止します。", mention_author=False)
            msg = "BANリストにないユーザーを指定したため処理を停止しました。"
            desc_url = ""
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return
        else:
            confirm_msg = f"【Unban実行確認】\n実行者:{ctx.author.display_name}(アカウント名:{ctx.author},ID:{ctx.author.id})\n対象者:\n　{user}(ID:{user.id})"
            exe_msg = f"{user.mention}のBANを解除しました。"
            non_exe_msg = f"{user.mention}のBANの解除をキャンセルしました。"
            confirm_arg = ""
            result = await Confirm(self.bot).confirm(
                ctx, confirm_arg, role, confirm_msg
            )
            if result is True:
                msg = exe_msg
                desc_url = ""
                await ctx.guild.unban(user)
                await ctx.send("Unbaned!")
                await LS(self.bot).send_exe_log(ctx, msg, desc_url)
                return
            msg = non_exe_msg
            desc_url = ""
            await ctx.send("Cancelled!")
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return

    @commands.command(name="kick")
    @commands.has_role(admin_role)
    async def _kick_user(
        self, ctx: commands.Context, member: discord.Member, if_dm: str = "dm:true"
    ):
        """メンバーをキック"""
        role = ctx.guild.get_role(admin_role)
        valid_list = ["dm:true", "dm:false"]
        if if_dm not in valid_list:
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
            msg = non_exe_msg
            desc_url = ""
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            await ctx.send("Cancelled!")
            return

    @user_command(guild_ids=[guild_id], name="緊急タイムアウト")
    @permissions.has_role(mod_role)
    # user commands return the member
    async def _emergency_timeout(self, ctx: ApplicationContext, member: discord.Member):
        await member.timeout_for(duration=timedelta(days=1), reason="Emergency Timeout")
        await ctx.respond(f"{member.mention}を緊急タイムアウトしました。", ephemeral=True)
        msg = f"{member.mention}を緊急タイムアウトしました。"
        desc_url = ""
        until = discord.utils.utcnow().astimezone(jst) + timedelta(days=1)
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
                timestamp=discord.utils.utcnow(),
            )
            await channel.send(embed=embed)
            return


def setup(bot):
    return bot.add_cog(Dealer(bot))
