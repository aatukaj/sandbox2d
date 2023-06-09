import pygame as pg
from settings import TILE_SIZE, Tags
from tiles import Tiles as t
from inventory import Inventory
from tools import load_img, Timer, get_img_dimensions
import abc
import math
from typing import TYPE_CHECKING, Any, Optional
from customtypes import Coordinate
import random

from lights import Light

if TYPE_CHECKING:
    from world import World
    from inventory import ItemStack
from tools import *
from components.collider import Collider
from components.render import SimpleRenderer
from components.physics import PhysicsComponent
from components.input import PlayerInputComponent, SimpleAIComponent
from game_object import GameObject


class Component(abc.ABC):
    @abc.abstractmethod
    def update(self, game_object: Any, world: "World") -> None:
        pass


class Player2(GameObject):
    def __init__(self, x: float, y: float, world):
        self.image = pg.Surface((TILE_SIZE - 3, TILE_SIZE - 3))
        self.image.fill((255, 255, 255))
        super().__init__(x, y, tag=Tags.PLAYER)
        self.add_component(
            Collider(
                *(pg.Vector2(self.image.get_size()) / TILE_SIZE),
                self,
                world.cs,
                tags=[Tags.ENEMY],
            )
        )
        self.add_component(SimpleRenderer(self, world.rs, self.image))
        self.add_component(PhysicsComponent(self, world.ps))
        self.inventory = Inventory(9 * 5)
        self.equipped_stack: ItemStack
        self.max_health = 100
        self.health = self.max_health
        self.inventory.items[0].set_data(t.DIRT, 999)

        self.add_component(PlayerInputComponent(self, world.ins))

    def update(self, world: "World"):
        return 1


class Enemy1(GameObject):
    def __init__(self, x, y, world):
        self.image = pg.Surface((TILE_SIZE - 3, TILE_SIZE - 3))
        color = hexstr2tuple("#63c74d")
        self.image.fill(color)
        super().__init__(x, y, *get_img_dimensions(self.image), tag=Tags.ENEMY)
        self.add_component(Collider(*get_img_dimensions(self.image), self, world.cs))
        self.add_component(SimpleAIComponent(self, world.ins))
        self.add_component(PhysicsComponent(self, world.ps))
        self.add_component(SimpleRenderer(self, world.rs, self.image))

        self.light = Light(50, self.pos, color)

    def update(self, world: "World"):
        self.light.pos = self.pos
        return 0


# this doesnt work rn
class TileOverlay(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.breaking_sprites = [
            load_img(f"textures/breaking/{i}.png") for i in range(1, 5)
        ]
        self.select_sprite = load_img("textures/select.png")

    def update(self, world: "World"):
        pass

    def draw(self, world: "World"):
        if (
            world.get_mouse_tile_pos().distance_to(world.player.pos)
            <= world.player.input_component.reach
        ):
            pos = world.get_mouse_tile_pos()
            world.draw_image(pos, self.select_sprite)
            if world.player.input_component.break_timer > 0:
                timer = world.player.input_component.break_timer
                if tile := world.tilemap.get_tile(pos):
                    cur_sprite = self.breaking_sprites[
                        min(int(timer / tile.break_time * 4), 3)
                    ]
                    world.draw_image(pos, cur_sprite)
