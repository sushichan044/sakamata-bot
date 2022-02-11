from typing import Any
import requests


class SongDBHttpClient:
    BASE_URL = ""

    def __init__(self) -> None:
        pass

    async def request(self, *, endpoint: str, **kwargs: Any) -> Any:
        url = self.BASE_URL + endpoint
        result: requests.Response = requests.post(url)
        return result

    async def _search_by_song(self, *, song_name: str) -> Any:
        return await self.request(endpoint=f"?title={song_name}")

    async def _search_by_artist(self, *, artist_name: str) -> Any:
        return await self.request(endpoint=f"?artist={artist_name}")

    async def _search_by_stream(self, *, stream_id: str) -> Any:
        return await self.request(endpoint=f"?stream={stream_id}")

    async def _search_no_recent_song(self) -> Any:
        return await self.request(endpoint="?recent")
