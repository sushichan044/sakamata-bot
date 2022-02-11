from typing import Any

from SongDB.model.history import History


class Song:
    def __init__(self, response: Any) -> None:
        self._response = response
        pass

    @property
    def title(self) -> str:
        return self._response

    @property
    def artist(self) -> str:
        return self._response

    @property
    def history(self) -> list[History]:
        return self._response
