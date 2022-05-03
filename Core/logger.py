import os
from datetime import timedelta, timezone

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

utc = timezone.utc
jst = timezone(timedelta(hours=9), "Asia/Tokyo")

guild_id = int(os.environ["GUILD_ID"])

vc_log_channel = int(os.environ["VC_LOG_CHANNEL"])


class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_voice_state_update")
    async def vc_log(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if member.guild.id == guild_id and (before.channel != after.channel):
            channel = self.bot.get_channel(vc_log_channel)
            now = discord.utils.utcnow().astimezone(jst)
            if before.channel is None:
                message = f"{now:%m/%d %H:%M:%S} : {member.name}(ID: {member.id}) が {after.channel.mention} に参加しました。"
                await channel.send(message)
                return
            elif after.channel is None:
                message = f"{now:%m/%d %H:%M:%S} : {member.name}(ID: {member.id}) が {before.channel.mention} から退出しました。"
                await channel.send(message)
                return
            else:
                message = f"{now:%m/%d %H:%M:%S} : {member.name}(ID: {member.id}) が {before.channel.mention} から {after.channel.mention} に移動しました。"
                await channel.send(message)
                return


def setup(bot):
    return bot.add_cog(Logger(bot))
