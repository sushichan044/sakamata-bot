from typing import Optional
import urllib.parse

import discord
from discord.ext import commands


class MishMash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="send-mishmash")
    @commands.has_permissions(administrator=True)
    async def send_mishmash_view(
        self,
        ctx: commands.Context,
        target: Optional[discord.TextChannel] = None,
        *,
        text: str,
    ):
        view = MishMash_View()
        if target is None:
            await ctx.send(content=text, view=view)
        else:
            await target.send(content=text, view=view)


class MishMash_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="日本語を使う方はこちら",
        custom_id="mishmash_form_button",
        style=discord.ButtonStyle.blurple,
    )
    async def mishmash_button(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if interaction.user is None:
            return
        user_name = interaction.user.name
        parsed_name = urllib.parse.quote(string=user_name)
        user_id = interaction.user.id
        form_url = f"https://docs.google.com/forms/d/e/1FAIpQLSfCEgUa3I_i4kkJ1eJ5BBEoqpv_GGB9WzH6ybOrQv2ZjUESig/viewform?usp=pp_url&entry.703835030={user_id}&entry.1949127614={parsed_name}"
        view = MishMash_Form_View(link=form_url)
        await interaction.response.send_message(
            content="下のボタンからGoogleフォームへ移動して\n寄せ書きの入力を行ってください。\n\nフィームへのリンクはユーザーごとに違うため、自分のリンクを使用してください。",
            view=view,
            ephemeral=True,
        )


class MishMash_Form_View(discord.ui.View):
    def __init__(self, link: str):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="Googleフォームへ移動", style=discord.ButtonStyle.url, url=link
            )
        )


def setup(bot):
    return bot.add_cog(MishMash(bot))
