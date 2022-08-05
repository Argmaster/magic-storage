from __future__ import annotations

from abc import ABC, abstractmethod

__all__ = ["DeleterBase"]


class DeleterBase(ABC):
    def delete(self, __uid: str, /, *, suppress_errors: bool = False) -> None:
        """Delete object with specified uid.

        Attempt to delete non-existing object may raise exception which can be
        automatically suppressed with suppress_errors=True.

        Parameters
        ----------
        __uid : str
            object unique identifier.
        suppress_errors : bool, optional
            toggles automatic error suppression, by default False
        """
        try:
            self._delete(__uid)
        except Exception:
            if not suppress_errors:
                raise

    @abstractmethod
    def _delete(self, __uid: str, /) -> None:
        ...
