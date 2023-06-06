from customtypes import Coordinate
import pygame as pg

from item import Item
from typing import Optional, TYPE_CHECKING
from settings import TILE_SIZE

if TYPE_CHECKING:
    from tilemap import Tilemap
    from player import Player2
    from world import World
    from inventory import ItemStack


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
        super().__init__(img_path, name, max_stack)
        self.rect = rect
        self.break_time = break_time
        self.break_level = break_level

    def collide(self, pos: Coordinate, other_rect: pg.FRect):
        if self.rect == None:
            return False

        return self.rect.move(pos[0], pos[1]).colliderect(other_rect)
    
    def right_click(self, world: "World", game_object: "Player2", item_stack: "ItemStack"):
        tile_pos = tile_pos = world.get_mouse_tile_pos()
        if game_object.pos.distance_to(tile_pos) <= game_object.input_component.reach:
            if not world.collision_dict.get(tuple(tile_pos)):
                if world.tilemap.set_tile(
                    tile_pos, self, replace=False
                ):
                    item_stack.remove(1)



    def __str__(self) -> str:
        return f"<{self.__class__}{self.__dict__}>"


class Water(Tile):
    img_cache = {}
    max_water_level = 4
    def __init__(
        self,
        img_path: str = "",
        name: str = "water",
        max_stack: int = 64,
        rect: pg.FRect | None = None,
        break_time: float = 0.5,
        break_level: int = 0,
    ):
        super().__init__(img_path, name, max_stack, rect, break_time, break_level)
        self._pos = pg.Vector2()
        self.water_level = self.max_water_level
        self.last_dir = pg.Vector2(1, 0)
        self.grounded = False

    @property
    def pos(self):
        return self._pos

    def update(self, tilemap: "Tilemap"):
        new_pos = self._pos + pg.Vector2(0, 1)
        tile = tilemap.get_tile(new_pos)
        if isinstance(tile, Water):
            if tile.water_level >= self.max_water_level:
                self.grounded = True
            else:
                new_level = tile.water_level + self.water_level
                tile.water_level = min(new_level, self.max_water_level + 2)
                self.water_level = new_level - tile.water_level
        elif tile and tile.rect:
            self.grounded = True
        else:
            self.move(tilemap, new_pos)
            self.grounded = False

        if self.grounded:
            for new_pos in sorted(
                [pg.Vector2(1, 0) + self._pos, pg.Vector2(-1, 0) + self._pos],
                key=lambda pos: self.get_water_level(tilemap, pos),
            ):
                tile = tilemap.get_tile(new_pos)
                if isinstance(tile, Water):
                    total = tile.water_level + self.water_level
                    self.water_level = total / 2
                    tile.water_level = total - self.water_level
                    break

                elif not tile or not tile.rect:
                    tilemap.set_tile(new_pos, Water)
                    new_water = tilemap.get_tile(new_pos)
                    prev_level = self.water_level
                    self.water_level = self.water_level / 2
                    new_water.water_level = prev_level - self.water_level
                    break

            # self.last_dir = -self.last_dir
        if self.water_level <= 0:
            tilemap.set_tile(self._pos, None)
            tilemap.tile_entities.remove(self)

    def get_water_level(self, tilemap: "Tilemap", pos: Coordinate):
        tile = tilemap.get_tile(pos)
        if isinstance(tile, Water):
            return tile.water_level
        return 0

    @property
    def img(self):
        key = round(self.water_level)
        if img := self.img_cache.get(key, None):
            pass
        else:
            img = pg.Surface((16, 16), pg.SRCALPHA)
            img.fill((0, 0, 255, 125), (0, 16 - key / self.max_water_level * TILE_SIZE, 16, key / self.max_water_level * TILE_SIZE))
            self.img_cache[key] = img
        return img

    def move(self, tilemap: "Tilemap", new_pos: pg.Vector2):
        tilemap.set_tile(new_pos, self)
        tilemap.set_tile(self._pos, None)
        self._pos = new_pos

    @pos.setter
    def pos(self, pos: Coordinate):
        self._pos = pg.Vector2(pos)


class Tiles:
    DIRT = Tile("textures/1.png", "Dirt", break_time=0.5)
    GRASS = Tile("textures/7.png", "Grass", break_time=0.5)
    STONE = Tile("textures/3.png", "Stone")
    GRASS_PLANT = Tile("textures/8.png", "Grass Plant", rect=None, break_time=0.1)
    WOOD = Tile("textures/5.png", "Wood")
    LEAF = Tile("textures/9.png", "Leaf", break_time=0.2)
    WATER = Water
