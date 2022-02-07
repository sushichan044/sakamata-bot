import discord
from discord.ext import commands
import pya3rt


class ChatBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    return bot.add_cog(ChatBot(bot))
