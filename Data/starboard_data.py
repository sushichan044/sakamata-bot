from typing import Literal


def _return_exception(env: Literal['main', 'alpha']) -> tuple[list[int], list[int]]:
    ignore_category = {
        916898415349223484: 'main',
        927568480985821185: 'main',
        925236277262045225: 'main',
        917599766353969173: 'main',
        916899483391000577: 'main',
        926866496137879592: 'main',
        917009372129919006: 'main',
        915910929240191006: 'main',
        917568001300123678: 'main',
        916859441821929472: 'main',
        926268191037087755: 'alpha',
    }

    ignore_channel = {
        929345604805611520: 'main',
        923789832482873404: 'main',
        927555978092748800: 'main',
        936758638561857537: 'alpha'
    }
    category = [cat for cat, e in ignore_category.items() if e == env]
    channel = [ch for ch, e in ignore_channel.items() if e == env]
    return category, channel
