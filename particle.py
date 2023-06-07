import pygame as pg
from typing import TYPE_CHECKING, Dict
from customtypes import ColorValue
from settings import TILE_SIZE
from lights import Light

if TYPE_CHECKING:
    from world import World


class ParticleManager:
    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def update(self, world):
        self.particles = [
            particle for particle in self.particles if particle.update(world)
        ]

    def add(self, particles):
        self.particles.extend(particles)

    def draw(self, world: "World"):
        world.surf.fblits(
            [(p.draw(), (p.pos - world.camera) * TILE_SIZE) for p in self.particles]
        )


class Particle:
    img_cache: Dict[tuple[int, ColorValue], pg.Surface] = {}

    def __init__(
        self,
        life_time: float,
        pos: pg.Vector2,
        vel: pg.Vector2,
        size: int,
        color: tuple,
        accel: pg.Vector2 = pg.Vector2(0, 0)
    ):
        self.pos = pos
        self.vel = vel
        self.time = 0
        self.life_time = life_time
        self.size = size
        self.start_size = size
        self.color = color
        self.accel = accel
        self.light = Light(self.size * 6, self.pos, self.color)

    def update(self, world: "World"):
        self.pos += self.vel * world.dt
        self.light.pos = self.pos
        self.vel += self.accel * world.dt

        self.time += world.dt
        if self.time >= self.life_time:
            self.light.kill()
            return 0
        frac = 1 - self.time/ self.life_time
        self.size = round(self.start_size * frac)
        self.light.radius = self.size * 6
        return 1

    def draw(self):
        key = (self.size, self.color)
        if img := self.img_cache.get(key, None):
            pass
        else:
            img = pg.Surface((self.size, self.size))
            img.fill(self.color)
            self.img_cache[key] = img
        return img



