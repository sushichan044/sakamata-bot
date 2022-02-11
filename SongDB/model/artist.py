from typing import Any, Union
from SongDB.model.song import Song


class Artist:
    def __init__(self, response: Any) -> None:
        """A Object that has a list of the song related to a specific artist.

        Args:
            response (Any): A response from spreadsheet.
        """
        self._response = response
        pass

    @property
    def songs(self) -> Union[Song, list[Song]]:
        """A list of the song related to a specific artist.

        Returns:
            list[Song]: A list contains each song's title and so on.
        """
        return self._response
