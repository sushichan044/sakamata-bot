from typing import Any


class History:
    def __init__(self, response: Any) -> None:
        """An object that represents a history of the song.

        Args:
            response (Any): A response from spreadsheet.
        """
        self._response = response
        pass

    @property
    def date(self) -> str:
        """
        A date that the song is sang.
        Returns:
            str: [description]
        """
        return self._response

    @property
    def href(self) -> str:
        """[summary]
        A link that the song had begun singing.

        Returns:
            str: [description]youtube link like youtu.be/xxxx
        """
        return self._response
