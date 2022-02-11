import re


yt_long = re.compile(r"^https?://www.youtube.com/watch\?v=[\w]+")
yt_short = re.compile(r"^https?://youtu.be/[\w]+")

long_vid = re.compile(r"https?://www.youtube.com/watch\?v=")
short_vid = re.compile(r"https?://youtu.be/")


def match_url(link: str) -> str | None:
    _long = yt_long.fullmatch(link)
    _short = yt_short.fullmatch(link)
    if _long:
        v_id = long_vid.sub("", _long.group())
        return v_id
    elif _short:
        v_id = short_vid.sub("", _short.group())
        return v_id
    else:
        print("song_db_pattern:Nothing is matched.")
        return None
