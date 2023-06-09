from components.base import System
from .base import System, Component
import pygame as pg
from settings import TILE_SIZE, Tags
import math
import random
from .collider import Collider
from event import post_event


class PhysicsSystem(System):
    def __init__(self):
        super().__init__()

    def update(self, world):
        self.components = [i for i in self.components if i.update(world)]
        return super().update()


class PhysicsComponent(Component):
    def __init__(self, owner, system: System) -> None:
        super().__init__(owner, system)

        self.grounded = False
        self.flying = False
        self.gravity = pg.Vector2(0, 20)
        self.forces: list[pg.Vector2] = []
        self.target_forces: list[tuple(pg.Vector2, pg.Vector2)] = []
        self.impulses: list[pg.Vector2] = []
        self.last_forces: list[pg.Vector2] = []

    def apply_force(self, vec: pg.Vector2):
        self.forces.append(vec)

    def apply_force_target(self, vec: pg.Vector2, target: pg.Vector2):
        self.target_forces.append((vec, target))

    def apply_impulse(self, vec: pg.Vector2):
        self.impulses.append(vec)

    def debug_draw(self, world: "World"):
        center = (self.owner.pos - world.camera) * TILE_SIZE
        for vec in self.last_forces:
            if vec.length_squared() == 0.0:
                continue
            direction = vec.normalize()
            pg.draw.line(
                world.surf,
                (
                    abs(direction.x * 255),
                    abs(direction.y * 255),
                    0,
                ),
                center,
                center + vec * 4,
            )
        pg.draw.line(
            world.surf,
            (
                0,
                0,
                255,
            ),
            center,
            center + self.owner.vel * 4,
        )

    def handle_force_target(self, game_object, force, target, dt) -> bool:
        if game_object.vel.x == target.x:
            return
        new_vel = game_object.vel + force * dt

        if force.x > 0:
            if game_object.vel.x < target.x and new_vel.x > target.x:
                dif = target.x - game_object.vel.x

                self.apply_force(pg.Vector2(dif / dt, 0))

            elif new_vel.x < target.x:
                self.apply_force(force)
        if force.x < 0:
            if game_object.vel.x > target.x and new_vel.x < target.x:
                dif = target.x - game_object.vel.x
                self.apply_force(pg.Vector2(dif / dt, 0))
            elif new_vel.x > target.x:
                self.apply_force(force)

    def apply_friction(self, game_object):
        fric = 1
        if self.grounded:
            fric = 20

        self.apply_force_target(
            pg.Vector2(-(math.copysign(fric, game_object.vel.x)), 0), pg.Vector2(0, 0)
        )

    def push_away_from_collision(self, rect, collision):
        c1 = pg.Vector2(rect.center)
        c2 = pg.Vector2(collision.rect.center)
        dif = c1 - c2

        if dif != pg.Vector2(0, 0):
            direction = dif.normalize()
        else:
            direction = pg.Vector2(random.random(), random.random()).normalize()
        self.apply_force(direction.elementwise() * pg.Vector2(80, 20))

    def update(self, world: "World"):
        rect = self.owner.components[Collider].rect
        dt = world.dt
        self.gravity = world.gravity

        self.apply_force(self.gravity)
        self.apply_friction(self.owner)

        if entity_collisions := world.cs.get_entity_collisions(
            self.owner.components[Collider]
        ):
            for collision in entity_collisions:
                self.push_away_from_collision(rect, collision)

        for force, target in self.target_forces:
            self.handle_force_target(self.owner, force, target, dt)

        for force in self.forces:
            self.owner.vel += force * dt
        for impulse in self.impulses:
            self.owner.vel += impulse

        self.last_forces = self.forces
        self.forces = []
        self.impulses = []
        self.target_forces = []

        rect.y += self.owner.vel.y * dt
        tile_collisions = world.tilemap.get_collisions(self.owner)
        self.last_grounded = self.grounded
        self.grounded = False

        if tile_collisions:
            for collision in tile_collisions:
                if self.owner.vel.y > 0:
                    self.owner.vel.y = 0
                    self.grounded = True
                    rect.bottom = collision.top
                    if not self.last_grounded and self.owner.tag == Tags.PLAYER:
                        post_event("player_grounded", self.owner)
                if self.owner.vel.y < 0:
                    self.owner.vel.y = 0
                    rect.top = collision.bottom

        rect.x += self.owner.vel.x * dt

        tile_collisions = world.tilemap.get_collisions(self.owner)
        if tile_collisions:
            for collision in tile_collisions:
                if self.owner.vel.x > 0:
                    self.owner.vel.x = 0
                    rect.right = collision.left

                if self.owner.vel.x < 0:
                    self.owner.vel.x = 0
                    rect.left = collision.right

        self.owner.pos = pg.Vector2(rect.center)
        return super().update()
