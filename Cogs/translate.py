import os

import deepl
import discord
from discord import permissions
from discord.commands import message_command
from discord.ext import commands

guild_id = int(os.environ['GUILD_ID'])
server_member_role = int(os.environ['SERVER_MEMBER_ROLE'])


class Translate(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.translator = deepl.Translator(os.environ['DEEPL_TOKEN'])

    @message_command(guild_ids=[guild_id], name='日本語に翻訳')
    @permissions.has_role(server_member_role)
    async def trans_to_jp(self, ctx, message: discord.Message):
        target = 'ja'
        r = self.trans_request(message.content, target)
        await ctx.respond(content=r, ephemeral=True)

    def trans_request(self, text: str, target: str):
        result = self.translator.translate_text(text, target_lang=target)
        return result


def setup(bot):
    return bot.add_cog(Translate(bot))
