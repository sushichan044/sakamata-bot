import os
from datetime import timezone, timedelta

utc = timezone.utc
jst = timezone(timedelta(hours=9), "Asia/Tokyo")

guild_id = int(os.environ["GUILD_ID"])
genshin_channel = int(os.environ["GENSHIN_CHANNEL"])
genshin_role = int(os.environ["GENSHIN_ROLE"])

official_map = "https://webstatic-sea.mihoyo.com/app/ys-map-sea/index.html"
official_statistics = (
    "https://webstatic-sea.mihoyo.com/app/community-game-records-sea/index.html"
)
unofficial_map = "https://genshin-impact-map.appsample.com/#/"
unofficial_map_2 = "https://yuanshen.site/index_jp.html?locale=ja"
redeem_code = "https://genshin.hoyoverse.com/ja/gift"
login_bonus = "https://webstatic-sea.mihoyo.com/ys/event/signin-sea/index.html?act_id=e202102251931481&lang=ja-"
