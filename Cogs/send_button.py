import asyncio
import os

import discord
from discord.commands import slash_command
from discord.ext import commands
from discord.ui import InputText, Modal
from dotenv import load_dotenv
from Event.birth_mishmash import Yosetti_View

load_dotenv()

guild_id = int(os.environ["GUILD_ID"])


class ButtonSender(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @slash_command(name="send-button")
    async def send_button(
        self,
        ctx: discord.ApplicationContext,
        channel: discord.Option(discord.TextChannel, required=True),
        attachment: discord.Option(discord.Attachment, required=False),
    ):
        # get content
        content = await self.get_content(ctx.interaction)
        if not content:
            await ctx.respond("メッセージ内容を正しく入力できませんでした。", ephemeral=True)
            return
        if (count := len(content)) > 2000:
            await ctx.respond(f"メッセージ内容が長すぎます。\n文字数が{count}文字です。", ephemeral=True)
            return
        if not isinstance(channel, discord.TextChannel):
            await ctx.respond("メッセージを送信するチャンネルを正しく指定できませんでした。", ephemeral=True)
            return
        # select button
        button = await self.get_button(ctx.interaction)
        if not button:
            await ctx.respond("ボタンを正しく指定できませんでした。", ephemeral=True)
        else:
            view = button_dict[button]
            msg = await channel.send(content=content, view=view)
            embed = discord.Embed(
                title="メッセージを送信しました。",
                color=15767485,
            )
            embed.add_field(name="送信先", value=f"[クリックして移動]({msg.jump_url})")
            await ctx.respond("ボタンを送信しました。", ephemeral=True)
            return

    @staticmethod
    async def get_content(interaction: discord.Interaction) -> str | None:
        future = asyncio.Future()
        if interaction.response.is_done():
            await interaction.followup.send(content="入力フォームを送信できません。", ephemeral=True)
        await interaction.response.send_modal(MessageInput(future))
        if future.done():
            if future.result():
                content, _interaction = future.result()
                return content
            else:
                return None
        return None

    @staticmethod
    async def get_button(interaction: discord.Interaction) -> str | None:
        future = asyncio.Future()
        content = "添付するボタンを選択してください。"
        view = SelectView(
            menu_dict=modal_button_dict,
            future=future,
            placeholder="ボタンを選択",
            min_values=1,
            max_values=1,
            deferred=True,
        )
        if interaction.response.is_done():
            await interaction.followup.send(content=content, view=view)
        else:
            await interaction.response.send_message(content=content, view=view)
        await future
        if future.done():
            if future.result():
                button, _interaction = future.result()
                return button
            else:
                return None
        else:
            return None


class MessageInput(Modal):
    def __init__(self, future: asyncio.Future, custom_id: str | None = None) -> None:
        self.future = future
        super().__init__(title="メッセージ内容入力", custom_id=custom_id)
        self.add_item(
            InputText(
                label="メッセージ内容",
                style=discord.InputTextStyle.paragraph,
                required=True,
                row=0,
                placeholder="これはメッセージです",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        self.future.set_result((self.children[0].value, interaction))
        await interaction.response.defer(ephemeral=True)


class SelectView(discord.ui.View):
    def __init__(
        self,
        menu_dict: dict[str, str],
        placeholder: str | None,
        min_values: int,
        max_values: int,
        future: asyncio.Future,
        deferred: bool,
    ):
        super().__init__(timeout=None)
        options: list[discord.SelectOption] = []
        for key, value in menu_dict.items():
            opt = discord.SelectOption(label=value, value=key)
            options.append(opt)
        select = _Select(
            future=future,
            deferred=deferred,
            placeholder=placeholder,
            options=options,
            min_values=min_values,
            max_values=max_values,
        )
        self.add_item(select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return False


modal_button_dict = {
    "1": "100万人Yosettiボタン",
}


button_dict: dict[str, discord.ui.View] = {
    "1": Yosetti_View(),
}


class _Select(discord.ui.Select):
    def __init__(
        self,
        *,
        future: asyncio.Future,
        deferred: bool,
        placeholder: str | None = None,
        min_values: int,
        max_values: int,
        options: list[discord.SelectOption],
    ) -> None:
        super().__init__(
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            options=options,
        )
        self.future = future
        self.deferred = deferred

    async def callback(self, interaction: discord.Interaction):
        self.future.set_result((self.values, interaction))
        if not self.deferred:
            pass
        else:
            await interaction.response.defer(ephemeral=True)


def setup(bot):
    return bot.add_cog(ButtonSender(bot))
