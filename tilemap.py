import pygame as pg
from settings import *
from tiles import Tile
from typing import Union, Optional
from customtypes import Coordinate


class Tilemap:
    def __init__(self, width: int, height: int):
        self.tiles: list[list[Optional["Tile"]]] = [
            [None for _ in range(width)] for _ in range(height)
        ]
        self.width = width
        self.height = height

    def draw(self, surf: pg.Surface, camera: pg.Vector2 = pg.Vector2(0, 0)):
        # cords for clipping
        y_start = max(0, int(-camera.y))
        x_start = max(0, int(-camera.x))
        y_end = min(self.height - 1, int((-camera.y + HEIGHT / TILE_SIZE) + 1))
        x_end = min(self.width - 1, int((-camera.x + WIDTH / TILE_SIZE) + 1))

        # love list comprehension
        surf.fblits(
            [
                (tile.img, ((x + camera.x) * TILE_SIZE, (y + camera.y) * TILE_SIZE))
                for y, row in enumerate(self.tiles[y_start:y_end], y_start)
                for x, tile in enumerate(row[x_start:x_end], x_start)
                if (tile is not None)
            ]
        )

    def is_inside(self, pos: Coordinate) -> bool:
        return (0 <= pos[0] < self.width) and (0 <= pos[1] < self.height)

    def is_tile_collidable(self, pos: Coordinate):
        """
        Returns True if the tile at pos has is collidable (has a rect)
        """
        tile = self.get_tile(pos)
        return tile is not None and tile.rect is not None

    def set_tile(
        self, pos: Coordinate, val: Union[Tile, None], replace: bool = True
    ) -> bool:
        if self.is_inside(pos):
            if replace or self.get_tile(pos) is None:
                self.tiles[int(pos[1])][int(pos[0])] = val
                return True
        return False

    def get_tile(self, pos: Coordinate) -> Union[Tile, None]:
        if self.is_inside(pos):
            return self.tiles[int(pos[1])][int(pos[0])]

    def set_tiles(
        self, pos: Coordinate, vals: list[list[Optional[Tile]]], replace: bool = True
    ):
        for y, row in enumerate(vals, int(pos[1])):
            for x, tile in enumerate(row, int(pos[0])):
                self.set_tile((x, y), tile, replace=replace)

    def get_tile_coords(self, pos: Coordinate):
        tile_coords = pos
        return tile_coords if self.is_inside(tile_coords) else False

    def get_collisions(self, rect: pg.FRect) -> list[pg.FRect]:
        # only works when rect dimensions are <= 1
        x1 = rect.left // 1
        y1 = rect.top // 1
        x2 = rect.right // 1
        y2 = rect.bottom // 1

        points = [
            pg.Vector2(x1, y1),
            pg.Vector2(x1, y2),
            pg.Vector2(x2, y1),
            pg.Vector2(x2, y2),
        ]
        rects: list[pg.FRect] = []

        for point in points:
            tile = self.get_tile(point)
            if tile is not None and tile.rect is not None:
                tile_rect = tile.rect.move(point)
                if rect.colliderect(tile_rect):
                    rects.append(tile_rect)

        return rects
