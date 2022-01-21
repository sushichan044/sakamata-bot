import os

import discord
from discord.ext import commands

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
            reaction = discord.utils.get(message.reactions, emoji=star_emoji)
            if reaction and reaction.count >= 3:
                count = reaction.count
                print('Event Get Done')
                await self.post_board(message, count)
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


def setup(bot):
    return bot.add_cog(StarBoard(bot))
