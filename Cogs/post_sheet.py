import os

import requests

from .format_date import FormatDate as date


class PostToSheet():
    def __init__(self, member, date: str) -> None:
        self.member = member
        self.date = date

    async def check_status(self):
        if self.member is None:
            return
        d = self.post_sheet()
        s = d.get('status')
        if s == 'ok':
            return None
        else:
            return s['message']

    def post_sheet(self):
        sent_date = date(self.date).format_date()
        data = {'id': f'{self.member.id}', 'name': f'{self.member}',
                'billing_date': f'{sent_date}'}
        url = os.environ['MEMBER_SHEET']
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