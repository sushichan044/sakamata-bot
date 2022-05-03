import json
import os
from datetime import datetime, timedelta, timezone

import discord
import requests
from discord.ext import commands
from discord.ui import InputText, Modal
from dotenv import load_dotenv

from Cogs.embed_builder import EmbedBuilder as EB

load_dotenv()

jst = timezone(timedelta(hours=9), "Asia/Tokyo")
admin_role = int(os.environ["ADMIN_ROLE"])
hook_url = os.environ["FEEDBACK_WEBHOOK"]


class Inquiry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="send-inq")
    @commands.has_permissions(administrator=True)
    async def _send_inq_button(self, ctx):
        embed = discord.Embed(
            title="管理者への問い合わせ",
            description="管理者へ直接問い合わせしたい場合は\nボタンを押してください。",
            color=2105893,
        )
        await ctx.send(embed=embed, view=InquiryView())
        return

    @commands.command(name="send-sug")
    @commands.has_permissions(administrator=True)
    async def _send_sug_button(self, ctx):
        embed = discord.Embed(
            title="サーバーへのご意見・ご要望",
            description="サーバーへの要望などを送りたい場合は\n下のフォームをご利用ください！",
            color=2105893,
        )
        await ctx.send(embed=embed, view=SuggestionView())
        return


class InquiryConfView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="続ける/Continue",
        style=discord.ButtonStyle.red,
        custom_id="continue_contact_mods_button",
        row=0,
    )
    async def callback_ok(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.defer(ephemeral=True)
        if not interaction.guild or not interaction.user:
            return
        if interaction.guild.premium_tier >= 2:
            thread_type = discord.ChannelType.private_thread
        else:
            thread_type = discord.ChannelType.public_thread
        if not interaction.channel or not isinstance(
            interaction.channel, discord.TextChannel
        ):
            print("Contact_mods: Invalid channel type")
            return
        tickets = len(interaction.channel.threads)
        target = await interaction.channel.create_thread(
            name=f"ticket-{str(tickets+1).zfill(4)}",
            auto_archive_duration=1440,
            type=thread_type,
        )
        await target.edit(invitable=False)
        await target.add_user(interaction.user)
        await target.send(content=f"<@&{admin_role}>")
        em = EB()._inquiry_contact(target)
        await interaction.followup.send(embed=em, ephemeral=True)
        return


class InquiryView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label="問い合わせ/Contact Moderators",
        style=discord.ButtonStyle.secondary,
        emoji="\N{Thought Balloon}",
        custom_id="start_contact_mods_button",
        row=0,
    )
    async def _contact_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            content="続けるボタンを押すと管理者を呼び出します。\n間違えて押した場合はこのメッセージを消してください。\n\nPress the 'Continue' button to contact Moderators.\nIf you pressed 'Contact' button by mistake, please delete this message.",
            view=InquiryConfView(),
            ephemeral=True,
        )
        return


class SuggestionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="目安箱/Server Suggestion",
        style=discord.ButtonStyle.secondary,
        emoji="\N{Envelope with Downwards Arrow Above}",
        custom_id="start_submit_survey_button",
        row=1,
    )
    async def _survey_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.send_modal(SurveyModal())
        return


class SurveyModal(Modal):
    def __init__(self) -> None:
        super().__init__(title="目安箱/Server Suggestion", custom_id="submit_survey_modal")
        self.add_item(
            InputText(
                label="サーバーへの意見やリクエスト、質問、相談など\nなんでもお聞かせください。",
                style=discord.InputTextStyle.paragraph,
                required=True,
                row=0,
            )
        )
        self.add_item(
            InputText(
                label="Discordアカウント名\n(管理者からの返信を希望する場合はお書きください。)",
                style=discord.InputTextStyle.short,
                required=False,
                row=1,
                placeholder="職員補佐#2976",
            )
        )

    async def callback(self, interaction: discord.Interaction):
        path = os.path.join(os.path.dirname(__file__), "../src/inquiry.json")
        with open(path) as f:
            df: dict = json.load(f)
        # print(df)
        now = datetime.now(jst).strftime("%Y/%m/%d %H:%M:%S")
        df["embeds"][0]["description"] = self.children[0].value
        df["embeds"][0]["footer"]["text"] = now
        if self.children[1].value:
            df["embeds"][0]["fields"] = [
                {"name": "アカウント名", "value": self.children[1].value}
            ]
        # print(df)
        content = json.dumps(df, indent=4)
        headers = {"Content-Type": "application/json"}
        try:
            requests.post(url=hook_url, data=content, headers=headers)
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                "何らかの要因により正常に送信できませんでした。\nこのBotのDMなどで管理者に問い合わせてください。", ephemeral=True
            )
        else:
            print("post completed")
            await interaction.response.send_message(
                "送信が完了しました。\nありがとうございました。", ephemeral=True
            )
        return


def setup(bot):
    return bot.add_cog(Inquiry(bot))
