import os
from typing import Optional
from unicodedata import name
import discord
from discord.ext import commands
from discord.commands import message_command

guild_id = int(os.environ['GUILD_ID'])
server_member_role = int(os.environ['SERVER_MEMBER_ROLE'])


# PollEmoji
poll_emoji_list = [
    '\N{Large Red Circle}',
    '\N{Large Green Circle}',
    '\N{Large Orange Circle}',
    '\N{Large Blue Circle}',
    # '\N{Large Yellow Circle}',
    '\N{Large Brown Circle}',
    '\N{Large Purple Circle}',
    # '\N{Medium Black Circle}',
    # '\N{Medium White Circle}',
    '\N{Large Red Square}',
    '\N{Large Green Square}',
    '\N{Large Orange Square}',
    '\N{Large Blue Square}',
    # '\N{Large Yellow Square}',
    '\N{Large Brown Square}',
    '\N{Large Purple Square}',
    # '\N{Black Large Square}',
    # '\N{White Large Square}',
    '\N{Large Orange Diamond}',
    '\N{Large Blue Diamond}',
    '\N{Heavy Black Heart}',
    '\N{Green Heart}',
    '\N{Orange Heart}',
    '\N{Blue Heart}',
    '\N{Brown Heart}',
    '\N{Purple Heart}',
]


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='poll')
    @commands.has_role(server_member_role)
    async def _poll(self, ctx, title, *select):
        if select == ():
            embed = discord.Embed(
                title=title,
                color=3447003,
            )
            embed.add_field(
                name='\N{Large Green Circle}',
                value='Yes',
            )
            embed.add_field(
                name='\N{Large Red Circle}',
                value='No'
            )
            poll_yes_emoji = '\N{Large Green Circle}'
            poll_no_emoji = '\N{Large Red Circle}'
            m = await ctx.send(embed=embed)
            await m.add_reaction(poll_yes_emoji)
            await m.add_reaction(poll_no_emoji)
            return
        elif len(select) > 20:
            embed = discord.Embed(
                title='選択肢が多すぎます。',
                color=16098851,
            )
            await ctx.send(embed=embed)
            return
        else:
            embed = discord.Embed(
                title=title,
                color=3447003,
            )
            for num in range(len(select)):
                embed.add_field(
                    name=poll_emoji_list[num],
                    value=select[num]
                )
            m = await ctx.send(embed=embed)
            for x in range(len(select)):
                await m.add_reaction(poll_emoji_list[x])
            return

    @message_command(guild_ids=[guild_id], name='投票集計')
    async def _result_poll(self, ctx, message: discord.Message):
        counts = [reaction.count for reaction in message.reactions]
        values = [field.value for field in message.embeds[0].fields]
        titles = [embed.title for embed in message.embeds]
        d = dict(zip(values, counts))
        embed = discord.Embed(
            title='集計結果',
            description=f'{titles[0]}',
            color=3447003,
        )
        for value, count in d.items():
            embed.add_field(
                name=value,
                value=str(count-1)
            )
        await ctx.send(embed=embed)
        await ctx.respond('集計完了', ephemeral=True)
        pass


def setup(bot):
    return bot.add_cog(Poll(bot))
