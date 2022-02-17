import discord
from discord import ApplicationContext
from discord.commands import slash_command
from discord.ext import commands

from . import cfg, embed_builder


class Portal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="gtool")
    async def portal(self, ctx: ApplicationContext):
        embed = embed_builder._portal()
        await ctx.respond(embed=embed, view=PortalView(), ephemeral=True)
        return


class PortalView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="公式マップ", url=cfg.official_map, row=0))
        self.add_item(discord.ui.Button(label="非公式マップ", url=cfg.unofficial_map, row=0))
        self.add_item(discord.ui.Button(label="コード受け取り", url=cfg.redeem_code, row=1))
        self.add_item(discord.ui.Button(label="ログインボーナス", url=cfg.login_bonus, row=1))


def setup(bot):
    return bot.add_cog(Portal(bot))
