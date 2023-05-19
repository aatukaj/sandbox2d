import random
from tilemap import Tilemap
from player import Player
from tools import OffsetGroup
import opensimplex
from settings import *
import tiles as t
from tools import load_img


import pygame as pg

breaking_sprites = [
    load_img(f"textures/breaking/{i}.png", transparent=True) for i in range(1, 5)
]
select_sprite = load_img("textures/select.png", transparent=True)


class World:
    def __init__(self):
        self.entities = OffsetGroup()
        self.tilemap = Tilemap(2000, 1000)
        self.player = Player(
            self.tilemap.width // 2,
            self.tilemap.height // 2 - 10,
            self.entities,
        )
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

    def draw(self, surf: pg.Surface):
        surf.fill("#79A6FF")
        self.camera.xy = (pg.Vector2(self.player.rect.center)) - pg.Vector2(
            WIDTH, HEIGHT
        ) // (2 * TILE_SIZE)

        self.tilemap.draw(surf, -self.camera)
        if self.player.selected_tile:
            pos = self.player.selected_tile - self.camera
            surf.blit(select_sprite, (pos * TILE_SIZE, (TILE_SIZE, TILE_SIZE)))
            if self.player.break_timer > 0:
                surf.blit(
                    breaking_sprites[
                        int(
                            self.player.break_timer
                            / self.tilemap.get_tile(
                                self.player.selected_tile
                            ).break_time
                            * 4
                        )
                    ],
                    pos * TILE_SIZE,
                )

        self.entities.draw(surf, -self.camera)

    def update(self, dt):
        self.entities.update(dt, self.tilemap)
        self.handle_mouse(dt)

    def handle_mouse(self, dt):
        # move this logic into player
        self.player.handle_mouse(self.camera, self, dt)
