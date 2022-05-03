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
        attachments: list[discord.File] | None = None,
    ) -> bool:
        send_confirm_msg_1 = f"{confirm_msg}\n------------------------{confirm_arg}"
        send_confirm_msg_2 = f"\nコマンド承認:{role.mention}\n実行に必要な承認人数: 1\n中止に必要な承認人数: 1"
        if attachments:
            send_confirm_msg_1 = (
                send_confirm_msg_1
                + f"\n添付ファイルの数:{len(attachments)}件\n------------------------"
            )
            send_confirm_msg_2 = (
                send_confirm_msg_2 + "\n------------------------\n添付ファイル:"
            )
        msg = send_confirm_msg_1 + send_confirm_msg_2
        if attachments:
            message = await ctx.send(content=msg, files=attachments)
        else:
            message = await ctx.send(content=msg)
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
        else:
            return False


def setup(bot):
    return bot.add_cog(Confirm(bot))
