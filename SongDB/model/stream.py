from typing import Any, Union
from SongDB.model.song import Song


class Stream:
    def __init__(self, response: Any) -> None:
        """An object that has a list of the songs related to a specific stream.

        Args:
            response (Any): A response from spreadsheet.
        """
        self._response = response
        pass

    @property
    def songs(self) -> Union[Song, list[Song]]:
        """A list of the songs related to a specific stream.

        Returns:
            list[Song]: A list of object that representing a song.
        """
        return self._response
