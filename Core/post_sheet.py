import os
from typing import Any

import requests
from discord import Member


class PostToSheet:
    def __init__(self, member: Member, date: str) -> None:
        self.member = member
        self.date = date

    def check_status(self):
        if self.member is None:
            return
        d = self.post_sheet()
        s = d.get("status")
        if s == "ok":
            return None
        else:
            return s["message"]

    def post_sheet(self) -> Any:
        data = {
            "id": f"{self.member.id}",
            "name": f"{self.member}",
            "billing_date": f"{self.date}",
        }
        url = os.environ["MEMBER_SHEET"]
        try:
            r: requests.Response = requests.post(url, data=data)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("エラー:", e)
        else:
            print(r)
            print(r.text)
            return r.json()
        finally:
            print("処理を完了")
