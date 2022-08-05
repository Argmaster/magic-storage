from __future__ import annotations

from abc import ABC, abstractmethod

__all__ = ["DeleterBase"]


class DeleterBase(ABC):
    def delete(self, __uid: str, /, *, missing_ok: bool = False) -> None:
        """Delete object with specified uid.

        Attempt to delete non-existing object KeyError will be raised unless missing_ok=True.

        Parameters
        ----------
        __uid : str
            object unique identifier.
        missing_ok : bool, optional
            ignores missing key errors, by default False
        """
        try:
            self._delete(__uid, missing_ok=missing_ok)
        except Exception as e:
            raise KeyError(f"Couldn't delete {__uid}.") from e

    @abstractmethod
    def _delete(self, __uid: str, /, *, missing_ok: bool = False) -> None:
        ...
