import os
from typing import Literal

import deepl
import discord
from discord import Option, permissions
from discord.commands import message_command, slash_command
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

    @message_command(guild_ids=[guild_id], name='Translate to English')
    @permissions.has_role(server_member_role)
    async def trans_to_en(self, ctx, message: discord.Message):
        target = 'en-US'
        r = self.trans_request(message.content, target)
        await ctx.respond(content=r, ephemeral=True)

    @slash_command(guild_ids=[guild_id], name='translate')
    @permissions.has_role(server_member_role)
    async def _trans_command(
            self,
            ctx,
            language: Option(str, 'Choose Output Language', choices=['日本語', 'English']),
            text: Option(str, 'Input text to translate'),
    ):
        target = self.select_language(language)
        r = self.trans_request(text, target)
        await ctx.respond(content=r, ephemeral=True)

    def select_language(self, language: str) -> Literal['ja', 'en-US']:
        if language == '日本語':
            return 'ja'
        else:
            return 'en-US'

    def trans_request(self, text: str, target: str):
        result = self.translator.translate_text(text, target_lang=target)
        return result


def setup(bot):
    return bot.add_cog(Translate(bot))
