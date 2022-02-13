import re


yt_long = re.compile(r"^[\S]*youtube.com/watch\?v=[\S]+")
yt_short = re.compile(r"^[\S]*youtu.be/[\S]+")

long_vid = re.compile(r"^[\S]+?v=")
short_vid = re.compile(r"^[\S]*youtu.be/")


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
        return None
