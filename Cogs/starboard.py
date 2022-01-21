import os
from typing import Optional

import discord
from discord.ext import commands
from discord.errors import HTTPException

star_emoji = '\N{Blue Heart}'
# star_emoji = '<:c_Ofb4:926885084395606086>'
emoji_url = 'https://cdn.discordapp.com/emojis/926885084395606086.webp?size=1024&quality=lossless'
star_channel = int(os.environ['STAR_CHANNEL'])


class StarBoard(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def board_add(self, payload):
        if str(payload.emoji) == star_emoji:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if message.type != discord.MessageType.default:
                return
            reaction = self._get_reaction(message)
            if reaction and reaction.count == 3:
                count = reaction.count
                await self.post_board(message, count)
                print('Post Done')
                return
            elif reaction and reaction.count >= 4:
                count = reaction.count
                print(count)
                await self.refresh_board(message, count)
                print('Post Done')
                return
            else:
                return

    async def post_board(self, message: discord.Message, count: int):
        channel = self.bot.get_channel(star_channel)
        sent_embeds = []
        if message.content or message.attachments:
            base_embed = self.make_embed(message, count)
            sent_embeds.append(base_embed)
            for attachment in message.attachments[1:]:
                embed = discord.Embed(
                    color=3447003,
                )
                embed.set_image(
                    url=attachment.proxy_url
                )
                sent_embeds.append(embed)
        for embed in message.embeds:
            sent_embeds.append(embed)
        await channel.send(embeds=sent_embeds)
        return

    def make_embed(self, message: discord.Message, count: int) -> discord.Embed:
        embed = discord.Embed(
            description=message.content,
            color=3447003,
            timestamp=message.created_at
        )
        embed.set_author(
            name=f'{message.author} in #{message.channel.name}',
            url=message.jump_url,
            icon_url=message.author.display_avatar.url
        )
        embed.add_field(
            name='元のメッセージ',
            value=f'[クリック/タップで移動]({message.jump_url})',
        )
        embed.set_footer(
            text=str(count),
            icon_url=emoji_url
        )
        if message.attachments and message.attachments[0].proxy_url:
            embed.set_image(
                url=message.attachments[0].proxy_url
            )
        return embed

    async def refresh_board(self, message: discord.Message, count: int):
        channel = self.bot.get_channel(star_channel)
        history = await self._get_history(channel)
        if not history:
            return
        target = [x
                  for x in history if x.embeds[0].author.url == message.jump_url]
        embed = target[0].embeds[0]
        embed.set_footer(
            text=str(count),
            icon_url=emoji_url
        )
        await target[0].edit(embed=embed)
        return

    async def _get_history(self, channel) -> Optional[list[discord.Message]]:
        try:
            history = await channel.history().flatten()
        except HTTPException as e:
            print(f'{e.response}\n{e.text}')
            return
        else:
            print(history)
            return history

    def _get_reaction(self, message: discord.Message):
        reaction = discord.utils.get(message.reactions, emoji=star_emoji)
        return reaction


def setup(bot):
    return bot.add_cog(StarBoard(bot))
