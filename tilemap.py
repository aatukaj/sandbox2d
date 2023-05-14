import pygame as pg
from settings import *

class Tilemap:
    def __init__(self, width, height):
        self.tiles = [[None for _ in range(width)] for _ in range(height)]
        self.width = width
        self.height = height
        print(self.width, self.height)

    def draw(self, surf: pg.Surface, camera=pg.Vector2(0, 0)):
        #cords for clipping
        y_start = max(0, int(-camera.y / TILE_SIZE))
        x_start = max(0, int(-camera.x / TILE_SIZE))
        y_end = min(self.height - 1, int((-camera.y + HEIGHT) / TILE_SIZE + 1))
        x_end = min(self.width - 1, int((-camera.x + WIDTH) / TILE_SIZE + 1))

        # love list comprehension
        surf.blits(
            (
                (tile.img, (x * TILE_SIZE + camera.x, y * TILE_SIZE + camera.y))
                for y, row in enumerate(self.tiles[y_start:y_end], y_start)
                for x, tile in enumerate(row[x_start:x_end], x_start)
                if (tile is not None)
            )
        )

    def is_inside(self, pos):
        return (0 <= pos[0] < self.width) and (0 <= pos[1] < self.height)
    
    def set_tile(self, pos, val, replace = True):
        if self.is_inside(pos):
            if replace or self.get_tile(pos) is None:
                self.tiles[pos[1]][pos[0]] = val

    def get_tile(self, pos):
        if self.is_inside(pos):
            return self.tiles[pos[1]][pos[0]]

    def set_tiles(self, pos, vals, replace = True):
        for y, row in enumerate(vals, int(pos[1])):
            for x, tile in enumerate(row, int(pos[0])):
                self.set_tile((x, y), tile, replace=replace)
    
    def get_tile_coords(self, pos):
        tile_coords = (int(pos.x / TILE_SIZE), int(pos.y / TILE_SIZE))
        return tile_coords if self.is_inside(tile_coords) else False
 

    def get_collisions(self, rect: pg.Rect):
        # only works when rect dimensions are <= TILE_SIZE
        x1 = rect.left // TILE_SIZE
        y1 = rect.top // TILE_SIZE
        x2 = rect.right // TILE_SIZE
        y2 = rect.bottom // TILE_SIZE

        points = [
            pg.Vector2(x1, y1),
            pg.Vector2(x1, y2),
            pg.Vector2(x2, y1),
            pg.Vector2(x2, y2),
        ]
        rects = []
        for point in points:
            if self.is_inside(point):
                tile = self.tiles[int(point.y)][int(point.x)]
                if tile is not None and tile.rect is not None:
                    rects.append(tile.rect.move(point * TILE_SIZE))

        if rects:
            return [rects[i] for i in rect.collidelistall(rects)]
    
    