import discord
from discord.ext import commands


class Message_Sys(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    return bot.add_cog(Message_Sys(bot))