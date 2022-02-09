from datetime import timedelta, timezone

import discord
from discord import ApplicationContext, Embed
from discord.ext import commands

utc = timezone.utc
jst = timezone(timedelta(hours=9), "Asia/Tokyo")


def create_base_log_embed(ctx: commands.Context, msg: str, desc_url: str) -> Embed:
    embed = discord.Embed(
        title="実行ログ",
        color=3447003,
        description=msg,
        url=f"{desc_url}",
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="実行者", value=f"{ctx.author.mention}")
    embed.add_field(name="実行コマンド", value=f"[コマンドリンク]({ctx.message.jump_url})")
    embed.add_field(
        name="実行日時",
        value=discord.utils.utcnow().astimezone(jst).strftime("%Y/%m/%d %H:%M:%S"),
    )
    return embed


def create_base_context_log_embed(
    ctx: ApplicationContext, msg: str, desc_url: str
) -> Embed:
    embed = discord.Embed(
        title="Context Menu 実行ログ",
        color=3447003,
        description=msg,
        url=f"{desc_url}",
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="実行者", value=ctx.interaction.user.mention)
    embed.add_field(
        name="実行日時",
        value=discord.utils.utcnow().astimezone(jst).strftime("%Y/%m/%d %H:%M:%S"),
    )
    return embed


def compose_embed_dm_box(message: discord.Message) -> Embed:
    embed = discord.Embed(
        title="DMを受信しました。",
        url=message.jump_url,
        color=3447003,
        description=message.content,
        timestamp=message.created_at,
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=avatar_check(message.author),
    )
    embed.add_field(name="送信者", value=f"{message.author.mention}")
    embed.add_field(
        name="受信日時",
        value=message.created_at.astimezone(jst).strftime("%Y/%m/%d %H:%M:%S"),
    )
    if message.attachments and message.attachments[0].proxy_url:
        embed.set_image(url=message.attachments[0].proxy_url)
    return embed


def avatar_check(member: discord.User | discord.Member) -> str:
    avatars = [member.avatar, member.display_avatar]
    if member.default_avatar in avatars:
        avatar_url = member.default_avatar.url
        return avatar_url
    else:
        avatar_url = member.display_avatar.replace(size=1024, static_format="webp").url
        return avatar_url
