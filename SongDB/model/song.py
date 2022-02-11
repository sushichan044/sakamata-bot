from typing import Any, Union

from SongDB.model.history import History


class Song:
    def __init__(self, response: Any) -> None:
        """An object that represents a song.

        Args:
            response (Any): A response from spreadsheet.
        """
        self._response = response
        pass

    @property
    def title(self) -> str:
        """A title of the song.

        Returns:
            str: the song's title
        """
        return self._response

    @property
    def artist(self) -> str:
        """An artist of the song.
        may contains the song's composer.

        Returns:
            str: the song's artist's name or composer's name
        """
        return self._response

    @property
    def history(self) -> Union[History, list[History]]:
        """A history of the song.
        it contains when the song was sang and that links to youtube.

        Returns:
            Union[History, list[History]]: Contains the date and the link tou youtube.
        """
        return self._response

    @property
    def latest_date(self) -> str:
        """A date that the song was sung most recently.

        Returns:
            str: A date
        """
        return self._response
