import requests


def download(title: str, url: str):
    try:
        r = requests.get(url)
        # openの中で保存先のパス（ファイル名を指定）
        with open("/tmp/" + title, mode="wb") as f:
            f.write(r.content)
    except requests.exceptions.RequestException as err:
        print(err)
