import discord
from discord.ext import commands

from . import cfg, embed_builder


class Portal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tool")
    async def portal(self, ctx):
        embed = embed_builder._portal()
        await ctx.message.channel.send(embed=embed, view=PortalView())
        return


class PortalView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="公式マップ", url=cfg.official_map))
        self.add_item(discord.ui.Button(label="公式戦席確認", url=cfg.official_statistics))
        self.add_item(discord.ui.Button(label="非公式マップ", url=cfg.unofficial_map))


def setup(bot):
    return bot.add_cog(Portal(bot))
