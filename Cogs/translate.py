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
        self.deepl_trans = deepl.Translator(auth_key=os.environ['DEEPL_TOKEN'])
        self.google_trans = googletrans.Translator()

    @message_command(guild_ids=[guild_id], name='日本語に翻訳')
    @permissions.has_role(server_member_role)
    async def deepl_trans_to_jp(self, ctx, message: discord.Message):
        if self.length_check(message.content):
            await ctx.respond('翻訳する文字は1024文字以下にしてください。', ephemeral=True)
            return
        else:
            pass
        target = 'ja'
        r = self.deepl_trans_request(message.content, target)
        if self.length_check_res(str(r)):
            await ctx.respond('翻訳結果が1024文字を超過しました。', ephemeral=True)
            return
        else:
            pass
        embeds = self.compose_embed(message.content, r, target, 'DeepL')
        await ctx.respond(embeds=embeds, ephemeral=True)
        return

    @message_command(guild_ids=[guild_id], name='Translate to English')
    @permissions.has_role(server_member_role)
    async def deepl_trans_to_en(self, ctx, message: discord.Message):
        if self.length_check(message.content):
            await ctx.respond(
                'The characters should be no more than 1024 characters.', ephemeral=True)
            return
        else:
            pass
        target = 'en-US'
        r = self.deepl_trans_request(message.content, target)
        if self.length_check_res(str(r)):
            await ctx.respond(
                'The translation result exceeded 1024 characters.', ephemeral=True)
            return
        else:
            pass
        target = 'en'
        embeds = self.compose_embed(message.content, r, target, 'DeepL')
        await ctx.respond(embeds=embeds, ephemeral=True)
        return

    @slash_command(guild_ids=[guild_id], name='translate')
    @permissions.has_role(server_member_role)
    async def _trans_command(
            self,
            ctx,
            service: Option(str, '翻訳サービスを選択してください。',
                            choices=['DeepL', 'GoogleTrans']),
            language: Option(str, '翻訳先の言語を選択してください。', choices=['日本語', 'English']),
            text: Option(str, '翻訳するテキストを入力してください。(最大1024文字)'),
    ):
        """翻訳機能"""
        if self.length_check(text):
            await ctx.respond('翻訳する文字は1024文字以下にしてください。', ephemeral=True)
            return
        else:
            pass
        if service == 'DeepL':
            target = self.select_language(language)
            r = self.deepl_trans_request(text, target)
            if self.length_check_res(str(r)):
                await ctx.respond('翻訳結果が1024文字を超過しました。', ephemeral=True)
                return
            else:
                pass
            if target == 'en-US':
                target = 'en'
            embeds = self.compose_embed(text, r, target, service)
            await ctx.respond(embeds=embeds, ephemeral=True)
            return
        else:
            target = self.select_language(language)
            if target == 'en-US':
                target = 'en'
            r = self.google_trans_request(text, target)
            if self.length_check_res(str(r)):
                await ctx.respond('翻訳結果が1024文字を超過しました。', ephemeral=True)
                return
            else:
                pass
            embeds = self.compose_embed(
                text, r.text, target, service)
            await ctx.respond(embeds=embeds, ephemeral=True)
            return

    def select_language(self, language: str) -> Literal['ja', 'en-US']:
        if language == '日本語':
            return 'ja'
        else:
            return 'en-US'

    def deepl_trans_request(self, text: str, target: Literal['ja', 'en-US']):
        result = self.deepl_trans.translate_text(
            text, target_lang=target)
        return result

    def google_trans_request(self, text: str, target: Literal['ja', 'en']):
        result = self.google_trans.translate(text, dest=target)
        return result

    def compose_embed(self, origin: str, result: str, output: Literal['ja', 'en'], service: Literal['DeepL', 'GoogleTrans']):
        if output == 'ja':
            _footer = f'{service}によって翻訳されました'
            _origin = '[翻訳元]'
            _result = '[翻訳結果]'
        else:
            _footer = f'Translated by {service}'
            _origin = '[Origin Text]'
            _result = '[Result]'
        embeds = []
        origin_embed = discord.Embed(
            color=15767485,
        )
        origin_embed.add_field(
            inline=False,
            name=_origin,
            value=origin,
        )
        embeds.append(origin_embed)
        res_embed = discord.Embed(
            color=3447003
        )
        res_embed.set_footer(
            text=_footer
        )
        res_embed.add_field(
            inline=False,
            name=_result,
            value=result,
        )
        embeds.append(res_embed)
        return embeds

    def length_check(self, text: str):
        if len(text) > 1024:
            return True
        else:
            return False

    def length_check_res(self, result: str):
        if len(result) > 1024:
            return True
        else:
            return False


def setup(bot):
    return bot.add_cog(Translate(bot))
