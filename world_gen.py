import pygame as pg
import opensimplex
import time
import random
from tiles import Tiles
from customtypes import *

class WorldGenerator():
    def __init__(self, tilemap):
        self.tilemap = tilemap
        
    def generate_tiles(self):
        start_time = time.time()
        seed = random.randint(0, 1 << 64)
        opensimplex.seed(seed)
        random.seed(seed)
        base_ground_y = self.tilemap.height // 2
        last_tree = -1
        for x in range(self.tilemap.width):
            ground_y = int(opensimplex.noise2(x / 15, 0) * 8) + base_ground_y
            stone_offset = int(opensimplex.noise2(x / 20, 2) * 5)
            self.tilemap.set_tile((x, ground_y), Tiles.GRASS)

            if last_tree + 1 < x and random.random() > 0.95:
                last_tree = x
                self.generate_tree(
                    pg.Vector2(x, ground_y - 1),
                    bark_length=random.choices([1, 2, 3, 4], weights=(1, 3, 3, 1))[0],
                )
            if random.random() > 0.7:
                self.tilemap.set_tile(
                    (x, ground_y - 1), Tiles.GRASS_PLANT, replace=False
                )
            # for water_y in range(base_ground_y, ground_y - 2, 1):
            # self.tilemap.set_tile((x, water_y), Tiles.WATER, False)

            for y in range(ground_y + 1, self.tilemap.height):
                if y < ground_y + 4 + stone_offset:
                    self.tilemap.set_tile((x, y), Tiles.DIRT)
                else:
                    self.tilemap.set_tile((x, y), Tiles.STONE)

            if x % (self.tilemap.width // 100) == 0:
                print(f"{round(x / self.tilemap.width * 100)}%")
                pg.display.flip()
        print(f"100%\nworldgen done, time:{time.time()-start_time:.2f}s")

    def generate_tree(self, pos: Coordinate, bark_length: int = 2) -> None:
        leaf_t = Tiles.LEAF
        bark_t = Tiles.WOOD
        leafs = [
            [None, leaf_t, leaf_t, leaf_t, None],
            [leaf_t, leaf_t, leaf_t, leaf_t, leaf_t],
            [leaf_t, leaf_t, leaf_t, leaf_t, leaf_t],
        ]
        bark = [[None, None, bark_t, None, None]] * bark_length
        tree = leafs + bark

        self.tilemap.set_tiles(
            (pos - pg.Vector2(2, bark_length + 2)), tree, replace=False
        )

