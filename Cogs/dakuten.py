import os
from discord import Option, permissions
from discord.ext import commands

from discord.commands import slash_command

guild_id = int(os.environ['GUILD_ID'])
server_member_role = int(os.environ['SERVER_MEMBER_ROLE'])


class Dakuten(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[guild_id], name='dakuten')
    @permissions.has_role(server_member_role)
    async def _dakuten(
        self,
        ctx,
        text: Option(str, '濁点をつけるテキストを入力してください。'),
    ):
        out_text = ''.join([text[num] + '゛' for num in range(len(text))])
        await ctx.respond(out_text, ephemeral=True)
        return


def setup(bot):
    return bot.add_cog(Dakuten(bot))
