import discord
from discord.ext import commands

accept_emoji = "\N{Heavy Large Circle}"
reject_emoji = "\N{Cross Mark}"


class Confirm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def confirm(
        self,
        ctx: commands.Context,
        confirm_arg: str,
        role: discord.Role,
        confirm_msg: str,
    ) -> bool:
        send_confirm_msg = f"{confirm_msg}\n------------------------{confirm_arg}\nコマンド承認:{role.mention}\n実行に必要な承認人数: 1\n中止に必要な承認人数: 1"
        message = await ctx.send(send_confirm_msg)
        await message.add_reaction(accept_emoji)
        await message.add_reaction(reject_emoji)
        valid_reactions = [accept_emoji, reject_emoji]
        # wait-for-reaction

        def check_confirm(payload: discord.RawReactionActionEvent):
            return (
                role in payload.member.roles
                and str(payload.emoji) in valid_reactions
                and payload.message_id == message.id
            )

        payload = await self.bot.wait_for("raw_reaction_add", check=check_confirm)
        # exe
        if str(payload.emoji) == accept_emoji:
            return True
        return False


def setup(bot):
    return bot.add_cog(Confirm(bot))
