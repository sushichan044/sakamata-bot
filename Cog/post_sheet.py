import discord
import requests


class PostToSheet():
    def __init__(self, member: discord.Member, date: str) -> None:
        self.member = member
        self.date = date

    async def check_status(self):
        d = self.post_sheet()
        s = d.get('status')
        if s == 'ok':
            return None
        else:
            return s['message']

    def post_sheet(self):
        sent_date = self.format_date()
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
            return r.json()
        finally:
            print('処理を完了')

    def format_date(self):
        sent_date = self.date[:3] + '/' + self.date[4:5] + '/' + self.date[6:7]
        return sent_date