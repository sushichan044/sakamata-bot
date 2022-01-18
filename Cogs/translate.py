import os

import deepl
import discord
from discord import permissions
from discord.commands import message_command
from discord.ext import commands

guild_id = int(os.environ['GUILD_ID'])
server_member_role = int(os.environ['SERVER_MEMBER_ROLE'])
DeepL_key = os.environ['DEEPL_TOKEN']


class Translate(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @message_command(guild_ids=[guild_id], name='EN→JP')
    @permissions.has_role(server_member_role)
    async def trans_en_to_jp(self, ctx, message: discord.Message):
        source = 'EN'
        target = 'JP'
        self.trans_request(message.content, source, target)

    def trans_request(self, text: str, source: str, target: str):
        params = {
            'auth_key': DeepL_key,
            'text': f'{text}',
            'source_lang': f'{source}',
            'target_lang': f'{target}',
        }
        r = requests.post()


def setup(bot):
    return bot.add_cog(Translate(bot))
