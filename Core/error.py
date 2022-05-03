import os
import traceback
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

error_log_channel = int(os.environ["ERROR_CHANNEL"])
jst = timezone(timedelta(hours=9), "Asia/Tokyo")
admin_role = int(os.environ["ADMIN_ROLE"])


class InteractionError(Exception):
    def __init__(
        self,
        *,
        interaction: discord.Interaction | None = None,
        cls: object | None = None,
        reason: str | None = None,
    ) -> None:
        traceback.print_exc()
        now = datetime.now(jst).strftime("%Y/%m/%d %H:%M:%S")
        output = f"[Interaction Error]\n\nTime: ({now})"
        if interaction and interaction.id:
            output = f"{output}\n\nID: {interaction.id}"
        if cls:
            output = f"{output}\n\nclass: {cls.__class__.__name__}"
        if reason:
            output = f"{output}\n\nreason: {reason}"
        if output:
            output = f"--------------------\n{output}\n--------------------"
        print(output)


class ErrorNotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_error")
    async def _on_error(self, event, something):
        channel = self.bot.get_channel(error_log_channel)
        now = datetime.now(jst).strftime("%Y/%m/%d %H:%M:%S")
        msg = f"エラーが発生しました。({now:%m/%d %H:%M:%S})\n{str(event)}\n{str(something)}"
        print(msg)
        await channel.send(f"```{msg}```")
        return

    @commands.Cog.listener(name="on_command_error")
    async def _on_command_error(self, ctx, error):
        channel = self.bot.get_channel(error_log_channel)
        now = datetime.now(jst).strftime("%Y/%m/%d %H:%M:%S")
        await channel.send(f"```エラーが発生しました。({now:%m/%d %H:%M:%S})\n{str(error)}```")
        if isinstance(error, commands.MissingRole):
            await ctx.reply(content="このコマンドを実行する権限がありません。", mention_author=False)
            return
        elif isinstance(error, commands.CommandNotFound):
            await ctx.reply(content="指定されたコマンドは存在しません。", mention_author=False)
            return
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(content="Botに必要な権限がありません。", mention_author=False)
            return
        return

    @commands.Cog.listener(name="on_application_command_error")
    async def _on_application_command_error(self, ctx, exception):
        now = datetime.now(jst).strftime("%Y/%m/%d %H:%M:%S")
        msg = f"エラーが発生しました。({now})\n{str(exception)}"
        if len(msg) >= 4000:
            print(msg)
            return
        channel = self.bot.get_channel(error_log_channel)
        await channel.send(f"```{msg}```")
        return

    @commands.command(name="errortest")
    @commands.has_role(admin_role)
    async def _errortest(self, ctx):
        """エラー出力テスト"""
        prin()


def setup(bot):
    return bot.add_cog(ErrorNotify(bot))
