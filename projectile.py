import pygame as pg
from components.collider import Collider
from components.render import SimpleRenderer
from tools import hexstr2tuple
from event import post_event
from game_object import GameObject
from lights import Light
from settings import TILE_SIZE, Tags
import random


class Projectile(GameObject):
    def __init__(self, x: float, y: float, vel: pg.Vector2, world: "World"):
        super().__init__(x, y, 0.5, 0.5, Tags.PROJECTILE)
        self.add_component(Collider(0.5, 0.5, self, world.cs, tags=[Tags.ENEMY]))
        self.vel = vel
        img = pg.Surface(pg.Vector2(0.5, 0.5) * TILE_SIZE)
        self.color = [
            hexstr2tuple("#68386c"),
            hexstr2tuple("#b55088"),
            hexstr2tuple("#f6757a"),
        ][random.randint(0, 2)]
        self.light = Light(img.get_size()[0] * 8, self.pos, self.color)
        img.fill(self.color)
        self.add_component(SimpleRenderer(self, world.rs, img))

    def update(self, world: "World"):
        dt = world.dt
        self.pos += self.vel * dt
        self.vel += world.gravity * world.dt
        self.light.pos = self.pos
        cols = world.tilemap.get_collisions(self)
        if cols:
            post_event("projectile_explosion", self)
            self.light.kill()
            self.kill()
            return 0
        return 1
