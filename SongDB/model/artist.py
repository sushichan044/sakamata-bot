from typing import Any
from SongDB.model.song import Song


class Artist:
    def __init__(self, response: Any) -> None:
        self._response = response
        pass

    @property
    def songs(self) -> list[Song]:
        return self._response
