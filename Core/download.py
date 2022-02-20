import requests


def download(title: str, url: str):
    try:
        r = requests.get(url, stream=True)
        # openの中で保存先のパス（ファイル名を指定）
        with open("/tmp/" + title, mode="wb") as f:
            for chunk in r:
                f.write(chunk)
    except requests.exceptions.RequestException as err:
        print(err)
