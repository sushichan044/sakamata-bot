import discord
from discord.ext import commands, tasks

from . import cfg


class Alarm(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.login_alert.start()

    def cog_unload(self) -> None:
        self.login_alert.cancel()

    @tasks.loop(seconds=60)
    async def login_alert(self):
        now = discord.utils.utcnow().astimezone(cfg.jst).strftime("%H:%M")
        if now == "07:00":
            guild = self.bot.get_guild(cfg.guild_id)
            channel = guild.get_channel_or_thread(cfg.genshin_channel)
            role = guild.get_role(cfg.genshin_role)
            await channel.send(
                content=f"{role.mention}\nログインボーナスの\n受け取りをお忘れなく！\nhttps://webstatic-sea.mihoyo.com/ys/event/signin-sea/index.html?act_id=e202102251931481&lang=ja-"
            )
            return
        else:
            pass


def setup(bot):
    return bot.add_cog(Alarm(bot))
