import os
from datetime import datetime, timedelta, timezone

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

join_log_channel = int(os.environ["JOIN_LOG_CHANNEL"])
jst = timezone(timedelta(hours=9), "Asia/Tokyo")


class EnctranceLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_member_join")
    async def on_join(self, member):
        status = "参加"
        await self._send_member_log(member, status)
        return

    @commands.Cog.listener(name="on_member_remove")
    async def on_leave(self, member):
        status = "退出"
        await self._send_member_log(member, status)
        return

    async def _send_member_log(self, member, status):
        channel = self.bot.get_channel(join_log_channel)
        now = datetime.now(tz=jst).strftime("%Y/%m/%d %H:%M:%S")
        count = member.guild.member_count
        send_msg = f"時刻: {now}\n{status}メンバー名: {member.name} (ID:{member.id})\nメンション: {member.mention}\nアカウント作成時刻: {member.created_at.astimezone(jst):%Y/%m/%d %H:%M:%S}\n現在のメンバー数:{count}\n"
        await channel.send(send_msg)
        return


def setup(bot):
    return bot.add_cog(EnctranceLog(bot))
