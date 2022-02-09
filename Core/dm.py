import discord
from discord.ext import commands


class DM_Sys(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    return bot.add_cog(DM_Sys(bot))
