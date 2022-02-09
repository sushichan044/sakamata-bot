import json
import os

import discord
import requests
from discord.ext import commands
from discord.ui import InputText, Modal

hook_url = "https://discord.com/api/webhooks/940939208049192960/syh7bQvU8O_JGmbyvukcdFaXrq3Vv1wBoX8PEgi-ex6wzLI4jFQ-20X68oSQHuKAy0dz"


class Inquiry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="send-sug")
    async def _send_sug_button(self, ctx):
        embed = discord.Embed(
            title="サーバーへのご意見・ご要望",
            description="管理者と話したい場合や\nサーバーへの要望などは下のボタンから\nアクセスできます！",
            color=15767485,
        )
        await ctx.send(embed=embed, view=InquiryView())


class InquiryView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label="管理者と話す/Contact to Moderators",
        style=discord.ButtonStyle.blurple,
        emoji="\N{Thought Balloon}",
        custom_id="start_contact_mods_button",
        row=0,
    )
    async def _contact_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        pass

    @discord.ui.button(
        label="目安箱/Server Suggestion",
        style=discord.ButtonStyle.green,
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
        if self.children[1].value:
            df["embeds"]["fields"] = [
                {"name": "アカウント名", "value": self.children[1].value}
            ]
        content = json.dumps(df, indent=4)
        headers = {"Content-Type": "application/json"}
        try:
            requests.post(url=hook_url, data=content, headers=headers)
        except Exception as e:
            print(e)
        else:
            print("post completed")
        return


def setup(bot):
    return bot.add_cog(Inquiry(bot))
