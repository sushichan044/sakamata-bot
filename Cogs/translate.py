import discord
from discord.ext import commands


class Translate(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot


def setup(bot):
    return bot.add_cog(Translate(bot))
