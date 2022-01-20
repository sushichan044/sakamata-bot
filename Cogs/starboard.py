import os

import discord
from discord.ext import commands


class StarBoard(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot


def setup(bot):
    return bot.add_cog(StarBoard(bot))
