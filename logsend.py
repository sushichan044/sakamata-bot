from discord.ext import commands
import discord

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/',intents=intents)

'''
#本番鯖IDなど

guildid = 915910043461890078
logchannel = 917009541433016370
vclogchannel = 917009562383556678
commandchannel = 917788634655109200
dmboxchannel = 921781301101613076

'''
#実験鯖IDなど
guildid = 916965252896260117
logchannel = 916971090042060830
vclogchannel = 916988601902989373
commandchannel = 917788514903539794
dmboxchannel = 918101377958436954


def log_send(message):
    channel = bot.get_channel(logchannel)
    channel.send(message)
