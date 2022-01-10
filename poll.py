import os
import discord
from discord.ext import commands

server_member_role = os.environ['SERVER_MEMBER_ROLE']


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

    @commands.command()
    async def poll(self, ctx, title, *select):
        if select == ():
            embed = discord.Embed(
                title=title,
                description="\N{Large Green Circle}Yes\n\N{Large Red Circle}No",
                color=3447003,
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
            send_desc_list = []
            for num in range(len(select)):
                element = f'{poll_emoji_list[num]}{select[num]}'
                send_desc_list.append(element)
            send_desc = '\n'.join(send_desc_list)
            embed = discord.Embed(
                title=title,
                description=send_desc,
                color=3447003,
            )
            m = await ctx.send(embed=embed)
            for x in range(len(select)):
                await m.add_reaction(poll_emoji_list[x])
            return


def setup(bot):
    return bot.add_cog(Poll(bot))
