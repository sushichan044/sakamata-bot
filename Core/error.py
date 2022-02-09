import os
from datetime import timedelta, timezone

import discord
from discord.ext import commands

error_log_channel = int(os.environ["ERROR_CHANNEL"])
jst = timezone(timedelta(hours=9), "Asia/Tokyo")
admin_role = int(os.environ["ADMIN_ROLE"])


class ErrorNotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_error")
    async def _on_error(self, event, something):
        channel = self.bot.get_channel(error_log_channel)
        now = discord.utils.utcnow().astimezone(jst)
        msg = f"エラーが発生しました。({now:%m/%d %H:%M:%S})\n{str(event)}\n{str(something)}"
        print(msg)
        await channel.send(f"```{msg}```")
        return

    @commands.Cog.listener(name="on_command_error")
    async def _on_command_error(self, ctx, error):
        channel = self.bot.get_channel(error_log_channel)
        now = discord.utils.utcnow().astimezone(jst)
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
        else:
            return

    @commands.Cog.listener(name="on_application_command_error")
    async def _on_application_command_error(self, ctx, exception):
        channel = self.bot.get_channel(error_log_channel)
        now = discord.utils.utcnow().astimezone(jst)
        await channel.send(f"```エラーが発生しました。({now:%m/%d %H:%M:%S})\n{str(exception)}```")
        return

    @commands.command(name="errortest")
    @commands.has_role(admin_role)
    async def _errortest(self, ctx):
        """エラー出力テスト"""
        prin()


def setup(bot):
    return bot.add_cog(ErrorNotify(bot))
