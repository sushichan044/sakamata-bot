import discord
from discord.ext import commands


class SongDB(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    return bot.add_cog(SongDB(bot))
