import os
from datetime import datetime, timedelta, timezone

import discord
from discord import Option
from discord.commands import permissions, slash_command
from discord.ext import commands
from discord.ui import InputText, Modal

mod_role = int(os.environ["MOD_ROLE"])
admin_role = int(os.environ["ADMIN_ROLE"])
guild_id = int(os.environ["GUILD_ID"])
jst = timezone(timedelta(hours=9), "Asia/Tokyo")
utc = timezone.utc


class StreamRegister(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[guild_id], default_permission=False, name="stream")
    @permissions.has_role(mod_role)
    async def _newcreateevent(
        self,
        ctx,
        event_name: Option(str, "配信の名前(例:マリカ,歌枠,など)"),
        stream_url: Option(str, "配信のURL"),
        start_time: Option(str, "配信開始時間(202205182100または2100(当日))"),
        duration: Option(float, "予想される配信の長さ(単位:時間)(例:1.5)"),
    ):
        """配信を簡単にイベントに登録できます。"""
        guild = ctx.guild
        if len(start_time) == 4:
            todate = datetime.now(timezone.utc).astimezone(jst)
            start_time_object = datetime.strptime(start_time, "%H%M")
            true_start_jst = start_time_object.replace(
                year=todate.year, month=todate.month, day=todate.day, tzinfo=jst
            )
        elif len(start_time) == 12:
            true_start = datetime.strptime(start_time, "%Y%m%d%H%M")
            true_start_jst = true_start.replace(tzinfo=jst)
        else:
            await ctx.respond(
                content="正しい時間を入力してください。\n有効な時間は\n```202205182100(2022年5月18日21:00)もしくは\n2100(入力した日の21:00)です。```",
                mention_author=False,
            )
            return
        true_duration = timedelta(hours=duration)
        true_end = true_start_jst + true_duration
        await guild.create_scheduled_event(
            name=f"{event_name}",
            description="",
            start_time=true_start_jst.astimezone(utc),
            end_time=true_end,
            location=stream_url,
        )
        await ctx.respond("配信を登録しました。")
        return

    @slash_command(guild_ids=[guild_id], name="testmodal")
    async def _test_modal(self, ctx):
        modal = StreamModal()
        await ctx.interaction.response.send_modal(modal)
        return


class StreamModal(Modal):
    def __init__(self) -> None:
        super().__init__(title="配信登録用フォーム")
        self.add_item(
            InputText(label="配信のトピック", placeholder="歌枠、雑談、など", row=0, required=True)
        )
        self.add_item(
            InputText(
                label="配信のURL(掲載できない場合は空欄)",
                placeholder="https://youtu.be/LyakqutKBpM",
                row=1,
                required=False,
            )
        )
        self.add_item(
            InputText(
                label="配信開始時刻",
                placeholder="2100(当日) or 2022.05.18.2100(日付指定)",
                row=2,
                required=True,
                min_length=4,
                max_length=15,
            )
        )
        self.add_item(
            InputText(
                label="予想配信時間(単位:時間)", placeholder="1.5(1時間30分)", row=3, required=True
            )
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        event_name = self.children[0].value
        if not self.children[1].value:
            event_url = ""
        else:
            event_url = self.children[1].value
        start_time = self.children[2].value
        if len(start_time) not in [4, 15]:
            # print(start_time)
            await interaction.response.send_message(
                content="正しい時間を入力してください。\n有効な時間は\n```2022.05.18.2100(2022年5月18日21:00)もしくは\n2100(入力した日の21:00)です。```",
                ephemeral=True,
            )
            return
        else:
            time = self._make_time(start_time)
        dur = timedelta(hours=float(self.children[3].value))
        end_time = time + dur
        await guild.create_scheduled_event(
            name=event_name,
            description="",
            start_time=time.astimezone(utc),
            end_time=end_time,
            location=event_url,
        )
        await interaction.response.send_message("配信を登録しました。")
        return

    def _make_time(self, time: str) -> datetime:
        if len(time) == 4:
            todate = datetime.now(timezone.utc).astimezone(jst)
            time_object = datetime.strptime(time, "%H%M")
            true_start_jst = time_object.replace(
                year=todate.year, month=todate.month, day=todate.day, tzinfo=jst
            )
            return true_start_jst
        else:
            true_start = datetime.strptime(time, "%Y.%m.%d%H%M")
            true_start_jst = true_start.replace(tzinfo=jst)
            return true_start_jst


def setup(bot):
    return bot.add_cog(StreamRegister(bot))
