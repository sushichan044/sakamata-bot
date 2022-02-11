from typing import Any


class History:
    def __init__(self, response: Any) -> None:
        self._response = response
        pass

    @property
    def date(self) -> str:
        return self._response

    @property
    def href(self) -> str:
        return self._response
