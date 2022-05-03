import os

from discord.commands import slash_command
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

count_vc = int(os.environ["COUNT_VC"])
guild_id = int(os.environ["GUILD_ID"])


class MemberCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_count.start()

    def cog_unload(self):
        self.start_count.cancel()

    @tasks.loop(minutes=30)
    async def start_count(self):
        await self.bot.wait_until_ready()
        await self.membercount()

    @slash_command(guild_ids=[guild_id], default_permission=False, name="manualcount")
    async def _manual(self, ctx):
        """メンバーカウントの手動更新用"""
        await self.membercount()
        await ctx.respond(content="更新が完了しました。", ephemeral=True)
        return

    async def membercount(self):
        guild = self.bot.get_guild(guild_id)
        server_member_count = guild.member_count
        vc = self.bot.get_channel(count_vc)
        await vc.edit(name=f"Member Count: {server_member_count}")
        return


def setup(bot):
    return bot.add_cog(MemberCount(bot))
