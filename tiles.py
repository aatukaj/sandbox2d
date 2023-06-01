from customtypes import Coordinate
import pygame as pg

from item import Item, ItemType
from typing import Optional

import enum


class Tile(Item):
    def __init__(
        self,
        img_path: str,
        name: str,
        max_stack: int = 64,
        rect: Optional[pg.FRect] = pg.FRect(0, 0, 1, 1),
        break_time: float = 0.5,
        break_level: int = 0,
    ):
        super().__init__(img_path, name, ItemType.TILE, max_stack)
        self.rect = rect
        self.break_time = break_time
        self.break_level = break_level

    def collide(self, pos : Coordinate, other_rect: pg.FRect):
        if self.rect == None:
            return False

        return self.rect.move(pos[0], pos[1]).colliderect(other_rect)

    def __str__(self) -> str:
        return f"<{self.__class__}{self.__dict__}>"


class Tiles(enum.Enum):
    DIRT = Tile("textures/1.png", "Dirt", break_time=0.5)
    GRASS = Tile("textures/2.png", "Grass", break_time=0.5)
    STONE = Tile("textures/3.png", "Stone")
    GRASS_PLANT = Tile("textures/4.png", "Grass Plant", rect=None, break_time=0.1)
    WOOD = Tile("textures/5.png", "Wood")
    LEAF = Tile("textures/6.png", "Leaf", break_time=0.2)
