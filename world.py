import random
from tilemap import Tilemap
from player import Player2, TileOverlay
from tools import OffsetGroup
import opensimplex
from settings import *
import tiles as t
from tools import load_img


import pygame as pg




class World:
    def __init__(self, surface):
        self.surf = surface
        self.layer0 = []
        self.tilemap = Tilemap(2000, 1000)
        self.player = Player2(
            self.tilemap.width // 2,
            self.tilemap.height // 2 - 5,
        )
        self.layer0.append(self.player)
        self.layer0.append(TileOverlay(0, 0))
        self.camera = pg.Vector2()
        self.generate_tiles()

    def generate_tiles(self):
        seed = random.randint(0, 1 << 64)
        opensimplex.seed(seed)
        random.seed(seed)
        base_ground_y = self.tilemap.height // 2
        last_tree = -1
        for x in range(self.tilemap.width):
            ground_y = int(opensimplex.noise2(x / 15, 0) * 8) + base_ground_y
            stone_offset = int(opensimplex.noise2(x / 20, 2) * 5)
            self.tilemap.set_tile((x, ground_y), t.GRASS)

            if last_tree + 1 < x and random.random() > 0.95:
                last_tree = x
                self.generate_tree(
                    pg.Vector2(x, ground_y - 1),
                    bark_length=random.choices([1, 2, 3, 4], weights=(1, 3, 3, 1))[0],
                )
            if random.random() > 0.7:
                self.tilemap.set_tile((x, ground_y - 1), t.GRASS_PLANT, replace=False)

            for y in range(ground_y + 1, self.tilemap.height):
                if y < ground_y + 6 + stone_offset:
                    self.tilemap.set_tile((x, y), t.DIRT)
                else:
                    self.tilemap.set_tile((x, y), t.STONE)

    def generate_tree(self, pos, bark_length=2):
        leafs = [
            [None, t.LEAF, t.LEAF, t.LEAF, None],
            [t.LEAF, t.LEAF, t.LEAF, t.LEAF, t.LEAF],
            [t.LEAF, t.LEAF, t.LEAF, t.LEAF, t.LEAF],
        ]
        bark = [[None, None, t.WOOD, None, None]] * bark_length
        tree = leafs + bark

        self.tilemap.set_tiles(
            (pos - pg.Vector2(2, bark_length + 2)), tree, replace=False
        )

    def draw(self):
        self.surf.fill("#79A6FF")
        self.camera.xy = (pg.Vector2(self.player.rect.center)) - pg.Vector2(
            WIDTH, HEIGHT
        ) // (2 * TILE_SIZE)
        self.tilemap.draw(self.surf, -self.camera)



    def update(self, dt):
        self.draw()
        self.dt = dt
        for i in self.layer0:
            i.update(self)


