import discord
from discord.ext import commands


class Utils_Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    return bot.add_cog(Utils_Command(bot))
