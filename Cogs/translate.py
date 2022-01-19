import os
from typing import Literal

import deepl
import discord
import googletrans
from discord import Option, permissions
from discord.commands import message_command, slash_command
from discord.ext import commands

guild_id = int(os.environ['GUILD_ID'])
server_member_role = int(os.environ['SERVER_MEMBER_ROLE'])


class Translate(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.deepl_trans = deepl.Translator(os.environ['DEEPL_TOKEN'])
        self.google_trans = googletrans.Translator()

    @message_command(guild_ids=[guild_id], name='日本語に翻訳')
    @permissions.has_role(server_member_role)
    async def deepl_trans_to_jp(self, ctx, message: discord.Message):
        target = 'ja'
        r = self.deepl_trans_request(message.content, target)
        await ctx.respond(content=r, ephemeral=True)

    @message_command(guild_ids=[guild_id], name='Translate to English')
    @permissions.has_role(server_member_role)
    async def deepl_trans_to_en(self, ctx, message: discord.Message):
        target = 'en-US'
        r = self.deepl_trans_request(message.content, target)
        await ctx.respond(content=r, ephemeral=True)

    @slash_command(guild_ids=[guild_id], name='translate')
    @permissions.has_role(server_member_role)
    async def _trans_command(
            self,
            ctx,
            service: Option(str, 'Choose Translation Service',
                            choices=['DeepL', 'GoogleTrans']),
            language: Option(str, 'Choose Output Language', choices=['日本語', 'English']),
            text: Option(str, 'Input text to translate'),
    ):
        if service == 'DeepL':
            target = self.select_language(language)
            r = self.deepl_trans_request(text, target)
            await ctx.respond(content=r, ephemeral=True)
        else:
            target = self.select_language(language)
            if target == 'en-US':
                target = 'en'
            r = self.google_trans_request(text, target)
            await ctx.respond(content=r.text, ephemeral=True)
            pass

    def select_language(self, language: str) -> Literal['ja', 'en-US']:
        if language == '日本語':
            return 'ja'
        else:
            return 'en-US'

    def deepl_trans_request(self, text: str, target: Literal['ja', 'en-US']):
        result = self.deepl_trans.translate_text(text, target_lang=target)
        return result

    def google_trans_request(self, text: str, target):
        result = self.google_trans.translate(text, dest=target)
        return result


def setup(bot):
    return bot.add_cog(Translate(bot))
