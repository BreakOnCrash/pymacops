from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Size:
    width: float
    height: float


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def origin(self) -> Point:
        return Point(self.x, self.y)

    @property
    def size(self) -> Size:
        return Size(self.width, self.height)

    def contains(self, point: Point) -> bool:
        return (
            self.x <= point.x < self.x + self.width
            and self.y <= point.y < self.y + self.height
        )

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.width, self.height)


@dataclass(frozen=True)
class WindowInfo:
    window_id: int
    title: str
    owner_name: str
    owner_pid: int
    bounds: Rect


@dataclass(frozen=True)
class TextBlock:
    text: str
    bounds: Optional[Rect] = None
