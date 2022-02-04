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
        self.add_item(discord.ui.Button(label="公式マップ", url=cfg.official_map, row=0))
        self.add_item(
            discord.ui.Button(label="公式戦績", url=cfg.official_statistics, row=0)
        )
        self.add_item(discord.ui.Button(label="非公式マップ", url=cfg.unofficial_map, row=1))
        self.add_item(
            discord.ui.Button(label="資源特化マップ", url=cfg.unofficial_map_2, row=1)
        )


def setup(bot):
    return bot.add_cog(Portal(bot))
