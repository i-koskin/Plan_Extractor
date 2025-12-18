from dataclasses import dataclass
from typing import List, Tuple, Optional

Point = Tuple[int, int]


@dataclass
class Wall:
    id: str
    points: List[Point]


@dataclass
class Door:
    id: str
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2


@dataclass
class Window:
    id: str
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2


@dataclass
class Plan:
    source: str
    walls: List[Wall]
    doors: List[Door]
    windows: List[Window]
