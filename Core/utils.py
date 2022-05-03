import os
from datetime import datetime, timedelta, timezone

import discord
from discord import ApplicationContext, Option
from discord.commands import slash_command
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

guild_id = int(os.environ["GUILD_ID"])

mod_role = int(os.environ["MOD_ROLE"])
admin_role = int(os.environ["ADMIN_ROLE"])
server_member_role = int(os.environ["SERVER_MEMBER_ROLE"])

stop_role = int(os.environ["STOP_ROLE"])
vc_stop_role = int(os.environ["VC_STOP_ROLE"])

utc = timezone.utc
jst = timezone(timedelta(hours=9), "Asia/Tokyo")

stop_list = [stop_role, vc_stop_role]


class Utils_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="user", guild_ids=[guild_id], default_permission=False)
    async def _newuser(
        self,
        ctx: ApplicationContext,
        member: Option(discord.Member, "対象のIDや名前を入力してください。"),
    ):
        """ユーザー情報を取得できます。"""
        # guild = ctx.guild
        # member = guild.get_member(int(id))
        # この先表示する用
        await ctx.defer()
        member_created: datetime = member.created_at.astimezone(jst)
        created = member_created.strftime("%Y/%m/%d %H:%M:%S")
        member_joined: datetime = member.joined_at.astimezone(jst)
        joined = member_joined.strftime("%Y/%m/%d %H:%M:%S")
        desc = f"対象ユーザー:{member.mention}\nユーザー名:{member}\nID:`{member.id}`\nBot:{member.bot}"
        roles = sorted(
            [role for role in member.roles],
            key=lambda role: role.position,
            reverse=True,
        )
        send_roles = "\n".join([role.mention for role in roles])
        avatars = [member.avatar, member.display_avatar]
        if member.default_avatar in avatars:
            avatar_url = member.default_avatar.url
        else:
            avatar_url = member.display_avatar.replace(
                size=1024, static_format="webp"
            ).url
        desc = desc + f"\n[Avatar url]({avatar_url})"
        deal = []
        if member.communication_disabled_until:
            until_jst: datetime = member.communication_disabled_until.astimezone(jst)
            until = until_jst.strftime("%Y/%m/%d %H:%M:%S")
            deal.append(f"Timeout: {until} に解除")
        stops = "\n".join([role.name for role in member.roles if role.id in stop_list])
        if stops:
            deal.append(stops)
        if not deal:
            send_deal = "なし"
        else:
            send_deal = "\n".join(deal)
        embed = discord.Embed(
            title="ユーザー情報照会結果",
            description=desc,
            color=3983615,
        )
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(
            name="アカウント作成日時",
            value=created,
        )
        embed.add_field(
            name="サーバー参加日時",
            value=joined,
        )
        embed.add_field(name=f"所持ロール({len(roles)})", value=send_roles, inline=False)
        embed.add_field(
            name="実行中措置",
            value=send_deal,
        )
        await ctx.respond(embed=embed)
        return

    @commands.command()
    @commands.has_role(mod_role)
    async def test(self, ctx: commands.Context):
        """生存確認用"""
        await ctx.send("hello")
        return

    @commands.command(name="private")
    @commands.has_role(admin_role)
    async def _private(self, ctx):
        role = ctx.guild.get_role(server_member_role)
        channels = sorted(
            [channel for channel in ctx.guild.channels if channel.category],
            key=lambda channel: channel.position,
        )
        for channel in channels:
            result = channel.permissions_for(role).view_channel
            print(channel.name, result)
        return

    @slash_command(guild_ids=[guild_id], name="ping")
    async def _ping(self, ctx: ApplicationContext):
        """生存確認用"""
        raw_ping = self.bot.latency
        ping = round(raw_ping * 1000)
        await ctx.respond(f"Pong!\nPing is {ping}ms")
        return


def setup(bot):
    return bot.add_cog(Utils_Command(bot))
