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

deepl_lang_dic = {
    'BG': 'ブルガリア語/Bulgarian',
    'CS': 'チェコ語/Czech',
    'DA': 'デンマーク語/Danish',
    'DE': 'ドイツ語/German',
    'EL': 'ギリシャ語/Greek',
    'EN': '英語/English',
    'ES': 'スペイン語/Spanish',
    'ET': 'エストニア語/Estonian',
    'FI': 'フィンランド語/Finnish',
    'FR': 'フランス語/French',
    'HU': 'ハンガリー語/Hungarian',
    'IT': 'イタリア語/Italian',
    'JA': '日本語/Japanese',
    'LT': 'リトアニア語/Lithuanian',
    'LV': 'ラトビア語/Latvian',
    'NL': 'オランダ語/Dutch',
    'PL': 'ポーランド語/Polish',
    'PT': 'ポルトガル語/Portuguese',
    'RO': 'ルーマニア語/Romanian',
    'RU': 'ロシア語/Russian',
    'SK': 'スロバキア語/Slovak',
    'SL': 'スロベニア語/Slovenian',
    'SV': 'スウェーデン語/Swedish',
    'ZH': '中国語/Chinese'
}


class Translate(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.deepl_trans = deepl.Translator(auth_key=os.environ['DEEPL_TOKEN'])
        self.google_trans = googletrans.Translator()

    @message_command(guild_ids=[guild_id], name='日本語に翻訳')
    @permissions.has_role(server_member_role)
    async def deepl_trans_to_jp(self, ctx, message: discord.Message):
        if not message.content and message.embeds:
            await ctx.respond('現在埋め込みメッセージには対応しておりません。', ephemeral=True)
            return
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
        if not message.content and message.embeds:
            await ctx.respond('Currently, embedded messages are not supported.', ephemeral=True)
            return
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

    @message_command(name='翻译成中文')
    @permissions.has_role(server_member_role)
    async def _deepl_trans_to_zh(self, ctx, message: discord.Message):
        if not message.content and message.embeds:
            await ctx.respond('目前不支持嵌入式信息。', ephemeral=True)
            return
        if self.length_check(message.content):
            await ctx.respond(
                '长于1024个字符的信息不能被翻译。', ephemeral=True)
            return
        else:
            pass
        target = 'zh'
        r = self.deepl_trans_request(message.content, target)
        if self.length_check_res(str(r)):
            await ctx.respond(
                '译文长度超过1024个字符，无法发送。', ephemeral=True)
            return
        else:
            pass
        embeds = self.compose_embed(message.content, r, 'DeepL')
        await ctx.respond(embeds=embeds, ephemeral=True)
        return

    @slash_command(name='translate')
    @permissions.has_role(server_member_role)
    async def _trans_command(
            self,
            ctx,
            service: Option(str, '翻訳サービス/Select Translation Service',
                            choices=['DeepL', 'GoogleTrans']),
            language: Option(str, '翻訳先の言語/Select language you want to translate to', choices=['日本語', 'English', '中文(简体)']),
            text: Option(str, '翻訳するテキスト(最大1024文字)/ Input text you want to translate(MAX:1024 Charactors)'),
    ):
        """翻訳機能/Translator/翻译机"""
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
            embeds = self.compose_embed(text, r, service)
            await ctx.respond(embeds=embeds, ephemeral=True)
            return
        else:
            target = self.select_language(language)
            if target == 'en-US':
                target = 'en'
            if target == 'zh':
                target = 'zh-cn'
            r = self.google_trans_request(text, target)
            if self.length_check_res(str(r)):
                await ctx.respond('翻訳結果が1024文字を超過しました。', ephemeral=True)
                return
            else:
                pass
            embeds = self.compose_embed(
                text, r.text, service)
            await ctx.respond(embeds=embeds, ephemeral=True)
            return

    def select_language(self, language: str) -> Literal['ja', 'en-US', 'zh']:
        if language == '日本語':
            return 'ja'
        elif language == 'English':
            return 'en-US'
        else:
            return 'zh'

    def deepl_trans_request(self, text: str, target: Literal['ja', 'en-US', 'zh']):
        result = self.deepl_trans.translate_text(
            text, target_lang=target)
        return result

    def google_trans_request(self, text: str, target: Literal['ja', 'en', 'zh-cn']):
        result = self.google_trans.translate(text, dest=target)
        return result

    def compose_embed(self, origin: str, result, service: Literal['DeepL', 'GoogleTrans']):
        _footer = f'Translated by {service}'
        _origin = '[翻訳元/Origin]'
        _result = '[翻訳結果/Result]'
        embeds = []
        origin_embed = discord.Embed(
            color=15767485,
        )
        origin_embed.add_field(
            inline=False,
            name=_origin,
            value=origin,
        )
        if service == 'DeepL':
            _src = deepl_lang_dic[result.detected_source_lang]
            origin_embed.set_footer(
                text=f'Language:{_src}'
            )
        else:
            pass
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
