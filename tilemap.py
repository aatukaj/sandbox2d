import pygame as pg
from settings import *
from tiles import Tile, Water
from typing import Union, Optional, TYPE_CHECKING
from customtypes import Coordinate
from inspect import isclass
from tools import Timer
if TYPE_CHECKING:
    from world import World
    from player import GameObject
class Tilemap:
    def __init__(self, width: int, height: int):
        self.tiles: list[list[Optional["Tile"]]] = [
            [None for _ in range(width)] for _ in range(height)
        ]
        self.tile_entities = []
        self.width = width
        self.height = height
        self.tile_entity_timer = Timer(0.2)

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
        if not replace and self.get_tile(pos):
            return False
        if not self.is_inside(pos):
            return False
        
        if isclass(val) and issubclass(Water, val):
            val = val()
            self.tile_entities.append(val)
            val.pos = pos

        self.tiles[int(pos[1])][int(pos[0])] = val
        return True


    def get_tile(self, pos: Coordinate) -> Union[Tile, None]:
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
    
    def update(self, world: "World"):
        if self.tile_entity_timer.tick(world.dt):
            for ent in self.tile_entities:
                ent.update(self)

    def get_collisions(self, game_object: "GameObject") -> list[pg.FRect]:
        # only works when rect dimensions are <= 1
        points = game_object.get_corner_tile_positions()
        rects: list[pg.FRect] = []

        for point in points:
            tile = self.get_tile(point)
            if tile is not None and tile.rect is not None:
                tile_rect = tile.rect.move(point)
                if game_object.rect.colliderect(tile_rect):
                    rects.append(tile_rect)

        return rects
