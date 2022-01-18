import json
import requests

import discord


class PostToSheet():
    def __init__(self, member: discord.Member) -> None:
        self.member = member

    async def check_status(self):
        return_status = self.post_sheet()
        s = return_status['status']
        if s == 'ok':
            return True
        else:
            return return_status['message']

    def post_sheet(self):
        data = {'id': f'{self.member.id}', 'name': f'{self.member}', }
        url = 'https://script.google.com/macros/s/AKfycby0NjXb8ASm75Q4rZpEUsENpWXtIVUZc7ZkhTtojaq6Ppd8jxD6gUzIZ8-O7YwGqoLJgg/exec'
        try:
            r = requests.post(url, data=data)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print('エラー:', e)
        else:
            print(r)
            print(r.text)
            return r.json
        finally:
            print('処理を完了')
