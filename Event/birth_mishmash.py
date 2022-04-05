import urllib.parse
from typing import Union

import discord
from discord.ext import commands


class MishMash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="send-mishmash")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def send_mishmash_view(
        self,
        ctx: commands.Context,
        target: discord.TextChannel,
        *,
        text: str,
    ):
        view = MishMash_View()
        await target.send(content=text, view=view)


class MishMash_View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="日本語",
        custom_id="mishmash_form_button_jp",
        style=discord.ButtonStyle.blurple,
    )
    async def mishmash_button_jp(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if interaction.user is None:
            return
        user_id, user_name = self.parser(user=interaction.user)
        form_url = f"https://docs.google.com/forms/d/e/1FAIpQLSfCEgUa3I_i4kkJ1eJ5BBEoqpv_GGB9WzH6ybOrQv2ZjUESig/viewform?usp=pp_url&entry.703835030={user_id}&entry.475358729={user_name}"
        view = MishMash_Form_View(link=form_url)
        await interaction.response.send_message(
            content="下のボタンからGoogleフォームへ移動して\n寄せ書きの入力を行ってください。\n\nフィームへのリンクはユーザーごとに違うため、自分のリンクを使用してください。",
            view=view,
            ephemeral=True,
        )

    @discord.ui.button(
        label="English",
        custom_id="mishmash_form_button_en",
        style=discord.ButtonStyle.success,
    )
    async def mishmash_button_en(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if interaction.user is None:
            return
        user_id, user_name = self.parser(user=interaction.user)
        form_url = f"https://docs.google.com/forms/d/e/1FAIpQLSe9O3tqOE4rjRZ2gVJ3kM5nfOdAJs2DY2W8Hv6qxzvvIwUxeg/viewform?usp=pp_url&entry.703835030={user_id}&entry.475358729={user_name}"
        view = MishMash_Form_View(link=form_url)
        await interaction.response.send_message(
            content="Please use the button below to go to the Google form to fill out the yosegaki.\n\nPlease use your own url to the form,\n\nas the url to the form is different for each user.",
            view=view,
            ephemeral=True,
        )

    def parser(self, user: Union[discord.User, discord.Member]) -> tuple[int, str]:
        user_name = user.name
        user_disc = user.discriminator
        user_identity = f"{user_name}#{user_disc}"
        parsed_name = urllib.parse.quote(string=user_identity)
        user_id = user.id
        return user_id, parsed_name


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
