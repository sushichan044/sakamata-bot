from discord_webhook import DiscordWebhook, DiscordEmbed

def error_log(message):
    webhook = DiscordWebhook(url='https://discord.com/api/webhooks/923826187254525952/DAsUrkjfMThdxVzBIDfLUZt0AikX_RXhEbzl4c8Q_m_ywk9YLV7Wy9i4_n7OyIb5sjQd',username="エラーログ")
    data=":exclamation: " + message+":exclamation:"
    embed = DiscordEmbed(title='エラー', description=data, color=0xff0000)
    webhook.add_embed(embed)
    webhook.execute()