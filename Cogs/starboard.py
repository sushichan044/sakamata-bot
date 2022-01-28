import os
from typing import Optional


import discord
from discord.ext import commands
from discord.errors import HTTPException

# star_emoji = '\N{Blue Heart}'
star_emoji = '<:c_Ofb4:926885084395606086>'
emoji_url = 'https://cdn.discordapp.com/emojis/926885084395606086.webp?size=1024&quality=lossless'
star_channel = int(os.environ['STAR_CHANNEL'])


class StarBoard(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def board_add(self, payload):
        # print(str(payload.emoji))
        if str(payload.emoji) == star_emoji:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            reaction = self._get_reaction(message)
            if reaction and reaction.count >= 3:
                if await self._get_history_post(message):
                    await self.post_board(message, reaction.count)
                    return
                else:
                    if reaction.count == 3:
                        return
                    else:
                        await self.refresh_board(message, reaction.count)
                        print('Complete Refresh')
                        return

    async def post_board(self, message: discord.Message, count: int):
        channel = self.bot.get_channel(star_channel)
        sent_embeds = []
        if message.content or message.attachments:
            base_embed = await self.make_embed(message, count)
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
        elif message.embeds and not message.content and not message.attachments:
            base_embed = await self.make_embed(message, count)
            if message.embeds[0].title:
                preview = message.embeds[0].title
            else:
                preview = '埋め込みメッセージ'
            base_embed.description = f'{preview}...(続きは元のメッセージへ)'
            sent_embeds.append(base_embed)
            await channel.send(embeds=sent_embeds)
            return

    async def make_embed(self, message: discord.Message, count: int) -> discord.Embed:
        embed = discord.Embed(
            description=message.content,
            color=3447003,
            timestamp=message.created_at
        )
        embed.set_author(
            name=f'{message.author.display_name} in #{message.channel.name}',
            url=message.jump_url,
            icon_url=message.author.display_avatar.url
        )
        embed.add_field(
            name='元のメッセージ',
            value=f'[クリックで移動]({message.jump_url})',
        )
        embed.set_footer(
            text=str(count),
            icon_url=emoji_url
        )
        if message.attachments and message.attachments[0].proxy_url:
            embed.set_image(
                url=message.attachments[0].proxy_url
            )
        if message.reference:
            ref_ch = self.bot.get_channel(message.reference.channel_id)
            ref_msg = await ref_ch.fetch_message(message.reference.message_id)
            embed.add_field(
                name='返信先',
                value=f'[クリックで移動]({ref_msg.jump_url})',
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
            # print(history)
            return history

    def _get_reaction(self, message: discord.Message):
        reaction = [x for x in message.reactions if str(x.emoji) == star_emoji]
        if not reaction[0]:
            print('Reaction Buggy')
        return reaction[0]

    async def _get_history_post(self, message: discord.Message) -> Optional[bool]:
        channel = self.bot.get_channel(star_channel)
        history = await self._get_history(channel)
        if not history:
            return True
        target = [x
                  for x in history if x.embeds and x.embeds[0].author.url == message.jump_url]
        if not target:
            return True
        else:
            return False


def setup(bot):
    return bot.add_cog(StarBoard(bot))
