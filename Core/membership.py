import asyncio
import os
import re
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands
from discord.ext.ui import MessageProvider, ViewTracker
from dotenv import load_dotenv

from Core.confirm import Confirm
from Core.log_sender import LogSender as LS
from Core.membership_ui import ConfirmView, RemoveView
from Core.post_sheet import PostToSheet as Sheet

load_dotenv()

utc = timezone.utc
jst = timezone(timedelta(hours=9), "Asia/Tokyo")

guild_id = int(os.environ["GUILD_ID"])

error_log_channel = int(os.environ["ERROR_CHANNEL"])
log_channel = int(os.environ["LOG_CHANNEL"])
member_check_channel = int(os.environ["MEMBER_CHECK_CHANNEL"])

yt_membership_role = int(os.environ["YT_MEMBER_ROLE"])
admin_role = int(os.environ["ADMIN_ROLE"])

date_pattern = re.compile(r"^\d{4}/\d{2}/\d{2}")


class Membership(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="check")
    @commands.dm_only()
    async def _check_member(self, ctx: commands.Context):
        """メンバーシップ認証用"""
        if ctx.message.attachments == []:
            await ctx.reply(
                content="画像が添付されていません。画像を添付して送り直してください。", mention_author=False
            )
            msg = "メンバー認証コマンドに画像が添付されていなかったため処理を停止しました。"
            desc_url = ""
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return
        else:
            await ctx.reply(content="認証要求を受理しました。\nしばらくお待ちください。", mention_author=False)
            channel = self.bot.get_channel(member_check_channel)
            guild = self.bot.get_guild(guild_id)
            exe_msg = f"{ctx.message.author.mention}のメンバーシップ認証を承認しました。"
            non_exe_msg = f"{ctx.message.author.mention}のメンバーシップ認証を否認しました。"
            future = asyncio.Future()
            view = ConfirmView(ctx, future)
            tracker = ViewTracker(view, timeout=None)
            await tracker.track(MessageProvider(channel))
            await future
            if future.done():
                if future.result():
                    btn_msg = tracker.message
                    msg = exe_msg
                    desc_url = tracker.message.jump_url
                    member = guild.get_member(ctx.message.author.id)
                    ref_msg = await btn_msg.reply(
                        f"{ctx.message.author.display_name}さんの次回支払日を返信してください。"
                    )

                    def check_date(message: discord.Message):
                        return (
                            bool(date_pattern.fullmatch(message.content))
                            and message.author != self.bot.user
                            and message.reference
                            and message.reference.message_id == ref_msg.id
                        )

                    date = await self.bot.wait_for("message", check=check_date)
                    status: str | None = Sheet(member, date.content).check_status()
                    if status is None:
                        await date.reply("シートに反映されました。", mention_author=False)
                        add_role = guild.get_role(yt_membership_role)
                        await member.add_roles(add_role)
                        await ctx.reply(
                            content="メンバーシップ認証を承認しました。\nメンバー限定チャンネルをご利用いただけます!",
                            mention_author=False,
                        )
                        log_channel_object = self.bot.get_channel(log_channel)
                        embed = discord.Embed(
                            title="実行ログ",
                            color=3447003,
                            description=msg,
                            url=f"{desc_url}",
                            timestamp=datetime.utcnow(),
                        )
                        embed.set_author(
                            name=self.bot.user,
                            icon_url=self.bot.user.display_avatar.url,
                        )
                        embed.add_field(
                            name="実行日時",
                            value=datetime.now(jst).strftime("%Y/%m/%d %H:%M:%S"),
                        )
                        await log_channel_object.send(embed=embed)
                        return
                    else:
                        await date.reply(
                            "予期せぬエラーによりシートに反映できませんでした。\nロールの付与は行われませんでした。",
                            mention_author=False,
                        )
                        channel = self.bot.get_channel(error_log_channel)
                        channel.send(status)
                else:
                    msg = non_exe_msg
                    desc_url = tracker.message.jump_url
                    get_reason = await tracker.message.reply(
                        content=f"DMで送信する{ctx.author.display_name}さんの不承認理由を返信してください。",
                        mention_author=False,
                    )

                    def check_reason(message):
                        return (
                            message.content
                            and message.author != self.bot.user
                            and message.reference
                            and message.reference.message_id == get_reason.id
                        )

                    message = await self.bot.wait_for("message", check=check_reason)
                    reply_msg = f"メンバーシップ認証を承認できませんでした。\n理由:\n　{message.content}"
                    await ctx.reply(content=reply_msg, mention_author=False)
                    await message.reply("否認理由を送信しました。", mention_author=False)
                    log_channel_object = self.bot.get_channel(log_channel)
                    embed = discord.Embed(
                        title="実行ログ",
                        color=3447003,
                        description=msg,
                        url=f"{desc_url}",
                        timestamp=datetime.utcnow(),
                    )
                    embed.set_author(
                        name=self.bot.user, icon_url=self.bot.user.display_avatar.url
                    )
                    embed.add_field(
                        name="実行日時",
                        value=datetime.now(jst).strftime("%Y/%m/%d %H:%M:%S"),
                    )
                    await log_channel_object.send(embed=embed)
                    return

    @commands.command(name="send_verify_button")
    @commands.has_role(admin_role)
    async def _send_verify_button(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Youtubeメンバーシップ認証",
            description="\N{Envelope with Downwards Arrow Above}を押すと認証が始まります。",
            color=15767485,
        )
        await ctx.send(embed=embed, view=MemberVerifyButton())
        return

    # remove-member

    @commands.command(name="remove-member")
    @commands.dm_only()
    async def _remove_member(self, ctx: commands.Context):
        """メンバーシップ継続停止時"""
        await ctx.reply(
            content="メンバーシップ継続停止を受理しました。\nしばらくお待ちください。", mention_author=False
        )
        channel = self.bot.get_channel(member_check_channel)
        guild = self.bot.get_guild(guild_id)
        exe_msg = f"{ctx.message.author.mention}のメンバーシップ継続停止を反映しました。"
        future = asyncio.Future()
        view = RemoveView(future, ctx)
        tracker = ViewTracker(view, timeout=None)
        await tracker.track(MessageProvider(channel))
        await future
        if future.done():
            if future.result():
                msg = exe_msg
                desc_url = tracker.message.jump_url
                member = guild.get_member(ctx.message.author.id)
                membership_role_object = guild.get_role(yt_membership_role)
                await member.remove_roles(membership_role_object)
                await ctx.reply(
                    content="メンバーシップ継続停止を反映しました。\nメンバーシップに再度登録された際は`//check`で再登録してください。",
                    mention_author=False,
                )
                log_channel_object = self.bot.get_channel(log_channel)
                embed = discord.Embed(
                    title="実行ログ",
                    color=3447003,
                    description=msg,
                    url=f"{desc_url}",
                    timestamp=datetime.utcnow(),
                )
                embed.set_author(
                    name=self.bot.user, icon_url=self.bot.user.display_avatar.url
                )
                embed.add_field(
                    name="実行日時",
                    value=datetime.now(jst).strftime("%Y/%m/%d %H:%M:%S"),
                )
                await log_channel_object.send(embed=embed)
                return

    # member-update-dm

    @commands.command(name="update-member")
    @commands.has_role(admin_role)
    async def _update_member(
        self, ctx: commands.Context, *update_member: discord.Member
    ):
        """メンバーシップ更新案内"""
        role = ctx.guild.get_role(admin_role)
        update_member_mention = [member.mention for member in update_member]
        update_member_str = "\n".join(update_member_mention)
        confirm_msg = f"【DM送信確認】\nメンバーシップ更新DMを\n{update_member_str}\nへ送信します。"
        exe_msg = f"{update_member_str}にメンバーシップ更新DMを送信しました。"
        non_exe_msg = f"{update_member_str}へのメンバーシップ更新DM送信をキャンセルしました。"
        DM_content = "【メンバーシップ更新のご案内】\n沙花叉のメンバーシップの更新時期が近づいた方にDMを送信させていただいております。\nお支払いが完了して次回支払日が更新され次第、以前と同じように\n`//check`\nで再認証を行ってください。\n\nメンバーシップを継続しない場合は\n`//remove-member`\nと送信してください。(__**メンバー限定チャンネルの閲覧ができなくなります。**__)"
        confirm_arg = f"\n{DM_content}\n------------------------"
        turned = await Confirm(self.bot).confirm(ctx, confirm_arg, role, confirm_msg)
        if turned:
            for member in update_member:
                await member.send(DM_content)
            await ctx.send("Sended!")
            msg = exe_msg
            desc_url = ""
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            return
        elif turned is False:
            msg = non_exe_msg
            desc_url = ""
            await LS(self.bot).send_exe_log(ctx, msg, desc_url)
            await ctx.send("Cancelled!")
            return
        else:
            return


class MemberVerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="認証を始める",
        style=discord.ButtonStyle.gray,
        emoji="\N{Envelope with Downwards Arrow Above}",
        custom_id="start_membership_verify_button",
    )
    async def _start_verify(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.defer()
        res_image_name = "receive_dm.png"
        path = os.path.join(os.path.dirname(__file__), r"../images/receive_dm.png")
        res_image = discord.File(fp=path, filename=res_image_name, spoiler=False)
        embed = discord.Embed(
            title="認証を開始します。",
            description="BotからのDMを確認してください。",
            color=15767485,
        )
        embed.add_field(
            name="BotからDMが届かない場合は？",
            value="サーバー設定の\n「プライバシー設定」から、\n「サーバーにいるメンバーからのダイレクトメッセージを許可する」\nをONにしてください。",
        )
        embed.set_image(url=f"attachment://{res_image_name}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                embed=embed, file=res_image, ephemeral=True
            )
        else:
            await interaction.followup.send(embed=embed, file=res_image, ephemeral=True)
        # Send DM
        DM_embed, dm_image = _compose_dm_embeds()
        try:
            await interaction.user.send(embed=DM_embed, file=dm_image)
        except discord.Forbidden as e:
            hook_image = discord.File(fp=path, spoiler=False)
            print("Error at start membership verify: ", e)
            await interaction.followup.send(
                content="DMの送信に失敗しました。\nDMが受信できない設定に\nなっている可能性があります。\n\nサーバー設定の\n「プライバシー設定」から、\n「サーバーにいるメンバーからのダイレクトメッセージを許可する」\nをONにしてください。",
                file=hook_image,
                ephemeral=True,
            )
        return


def _compose_dm_embeds() -> tuple[discord.Embed, discord.File]:
    image_name = "auth_1.png"
    path = os.path.join(os.path.dirname(__file__), r"../images/auth_1.png")
    image = discord.File(fp=path, filename=image_name, spoiler=False)
    embed = discord.Embed(
        title="メンバーシップ認証", description="以下の手順に従って\n認証を開始してください。", color=15767485
    )
    embed.add_field(
        inline=False,
        name="手順1",
        value="Discordアカウントの画像と、\n[こちら](https://www.youtube.com/paid_memberships)から確認できる\n__**次回支払日が確認できる画像**__\n(例:下の画像)を準備する。",
    )
    embed.add_field(
        inline=False,
        name="手順2",
        value="このDMに、\n__手順1で準備した画像を__\n__全て添付して__、\n`//check`と送信する。",
    )
    embed.add_field(
        inline=False,
        name="手順3",
        value="Botから\n```認証要求を受理しました。\nしばらくお待ちください。```\nと返信があれば完了です。\n管理者の対応をお待ちください。",
    )
    embed.add_field(
        name="Botから完了の返信が来ない場合は？",
        value="コマンドが間違っている\n(正しいコマンドは`//check`)、\n画像を添付していないなどの\n可能性があります。\n\n全て正しいのに解決しない場合は、\nこのDMにその旨を書いて\n送信してください。",
    )
    embed.set_image(url=f"attachment://{image_name}")
    return embed, image


def setup(bot):
    return bot.add_cog(Membership(bot))
