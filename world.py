import random
from tilemap import Tilemap
from player import Player2, TileOverlay, Enemy1
from tools import OffsetGroup
import opensimplex
from settings import *
from tiles import Tiles
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
        for i in range(20):
            self.layer0.append(Enemy1(*(self.player.pos - pg.Vector2(5, 5 + i))))
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
            self.tilemap.set_tile((x, ground_y), Tiles.GRASS.value)

            if last_tree + 1 < x and random.random() > 0.95:
                last_tree = x
                self.generate_tree(
                    pg.Vector2(x, ground_y - 1),
                    bark_length=random.choices([1, 2, 3, 4], weights=(1, 3, 3, 1))[0],
                )
            if random.random() > 0.7:
                self.tilemap.set_tile(
                    (x, ground_y - 1), Tiles.GRASS_PLANT.value, replace=False
                )

            for y in range(ground_y + 1, self.tilemap.height):
                if y < ground_y + 6 + stone_offset:
                    self.tilemap.set_tile((x, y), Tiles.DIRT.value)
                else:
                    self.tilemap.set_tile((x, y), Tiles.STONE.value)

    def generate_tree(self, pos, bark_length=2):
        leaf_t = Tiles.LEAF.value
        bark_t = Tiles.WOOD.value
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

    def draw(self):
        self.surf.fill("#79A6FF")
        self.camera.xy = (
            pg.Vector2(self.player.physics_component.rect.center)
        ) - pg.Vector2(WIDTH, HEIGHT) // (2 * TILE_SIZE)
        self.tilemap.draw(self.surf, -self.camera)
        for i in self.layer0:
            i.draw(self)

    def get_collision_rects(self, rect: pg.FRect):
        return self.tilemap.get_collisions(rect) + self.get_entity_collisions(rect)

    def get_entity_collisions(self, game_obj):
        collisions = []
        for pos in game_obj.physics_component.get_corner_tile_positions():
            for obj in self.collision_dict.get(pos):
                if obj != game_obj and obj.physics_component.rect not in collisions:
                    if game_obj.physics_component.rect.colliderect(
                        obj.physics_component.rect
                    ):
                        collisions.append(obj.physics_component.rect)
        return collisions

    def get_mouse_tile_pos(self):
        mouse_pos = pg.Vector2(pg.mouse.get_pos()) / TILE_SIZE
        return self.tilemap.get_tile_coords((mouse_pos + self.camera) // 1)

    def draw_image(self, pos, image):
        self.surf.blit(image, (pos - self.camera) * TILE_SIZE)

    def update_collision_dict(self):
        collision_dict = {}
        for obj in self.layer0:
            if hasattr(obj, "physics_component"):
                for i in obj.physics_component.get_corner_tile_positions():
                    if i in collision_dict:
                        collision_dict[i].append(obj)
                    else:
                        collision_dict[i] = [obj]
        self.collision_dict = collision_dict

    def update(self, dt):
        self.update_collision_dict()
        self.dt = dt
        for i in self.layer0:
            i.update(self)
        self.draw()
