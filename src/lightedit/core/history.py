"""Command history, including memory-efficient changed-region pixel commands."""

from dataclasses import dataclass
from typing import Protocol

import numpy as np


class Command(Protocol):
    def undo(self) -> None: ...
    def redo(self) -> None: ...


@dataclass
class RegionCommand:
    target: np.ndarray
    bounds: tuple[int, int, int, int]
    before: np.ndarray
    after: np.ndarray
    label: str = "Stroke"

    @classmethod
    def capture(
        cls,
        target: np.ndarray,
        bounds: tuple[int, int, int, int],
        before: np.ndarray,
        label: str = "Stroke",
    ) -> "RegionCommand":
        x, y, w, h = bounds
        return cls(target, bounds, before.copy(), target[y : y + h, x : x + w].copy(), label)

    def _apply(self, data: np.ndarray) -> None:
        x, y, w, h = self.bounds
        self.target[y : y + h, x : x + w] = data

    def undo(self) -> None:
        self._apply(self.before)

    def redo(self) -> None:
        self._apply(self.after)


class History:
    def __init__(self, limit: int = 100) -> None:
        self.limit = limit
        self._undo: list[Command] = []
        self._redo: list[Command] = []

    def push(self, command: Command) -> None:
        self._undo.append(command)
        self._undo = self._undo[-self.limit :]
        self._redo.clear()

    def undo(self) -> bool:
        if not self._undo:
            return False
        command = self._undo.pop()
        command.undo()
        self._redo.append(command)
        return True

    def redo(self) -> bool:
        if not self._redo:
            return False
        command = self._redo.pop()
        command.redo()
        self._undo.append(command)
        return True
