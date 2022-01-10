import redis
import os


def connect():
    return redis.from_url(
        url=os.environ.get('REDIS_URL'),  # 環境変数にあるURLを渡す
        charset='utf-8',
        decode_responses=True,  # 日本語の文字化け対策のため必須
    )
