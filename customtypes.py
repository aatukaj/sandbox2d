from typing import Union, Tuple, Sequence
from pygame import Vector2


RGBAOutput = Tuple[int, int, int, int]
Coordinate = Union[Tuple[float, float], Sequence[float], Vector2]
ColorValue = Union[int, str, Tuple[int, int, int], RGBAOutput, Sequence[int]]