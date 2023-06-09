from components.base import System
from tools import Timer
import pygame as pg
from .base import System, Component
from .physics import PhysicsComponent
from .collider import Collider
from event import post_event
from projectile import Projectile
import random
import math


class InputSystem(System):
    def __init__(self):
        super().__init__()

    def update(self, world):
        self.components = [i for i in self.components if i.update(world)]
        return super().update()


class PlayerInputComponent(Component):
    def __init__(self, owner, system: System) -> None:
        super().__init__(owner, system)

        self.break_timer = 0
        self.reach = 5
        self.dash_timer = Timer(1)
        self.can_dash = False
        self.prev_tile_pos = None
        self.last_keys = pg.key.get_pressed()
        self.shoot_timer = Timer(0.2)

    def update(self, world: "World") -> None:
        if not self.can_dash and self.dash_timer.tick(world.dt):
            self.can_dash = True
        self.handle_keys(self.owner, world)
        self.handle_mouse(self.owner, world)
        return super().update()

    def handle_keys(self, game_object: "Player2", world: "World"):
        keys = pg.key.get_pressed()

        if keys[pg.K_d]:
            game_object.components[PhysicsComponent].apply_force_target(
                pg.Vector2(50, 0), pg.Vector2(5, 0)
            )

        if keys[pg.K_a]:
            game_object.components[PhysicsComponent].apply_force_target(
                pg.Vector2(-50, 0), pg.Vector2(-5, 0)
            )

        if keys[pg.K_e] and self.can_dash:
            self.dash(game_object, world, pg.Vector2(10, 0))

        if keys[pg.K_q] and self.can_dash:
            self.dash(game_object, world, pg.Vector2(-10, 0))

        if keys[pg.K_SPACE] and game_object.components[PhysicsComponent].grounded:
            self.jump(game_object)

    def dash(self, game_object: "Player2", world: "World", vec: pg.Vector2):
        self.can_dash = False
        game_object.components[PhysicsComponent].apply_impulse(vec)
        post_event("player_dash", {"game_object": game_object, "vec": vec})

    def jump(self, game_object):
        game_object.components[PhysicsComponent].apply_impulse(pg.Vector2(0, -13))
        post_event("player_jump", game_object)

    def right_click(self, world: "World", game_object: "Player2"):
        game_object.equipped_stack.right_click(world, self)

    def left_click(self, world: "World", game_object: "Player2"):
        tile_pos = world.get_mouse_tile_pos()
        if self.shoot_timer.tick(world.dt):
            p = Projectile(0, 0, (tile_pos - game_object.pos).normalize() * 20, world)
            p.pos = game_object.pos
            world.projectiles.append(p)
        if game_object.pos.distance_to(tile_pos) > self.reach:
            return
        tile = world.tilemap.get_tile(tile_pos)

        if tile is None:
            self.break_timer = 0
            return

        self.break_timer += world.dt
        if self.prev_tile_pos != tile_pos:
            self.break_timer = 0

        if self.break_timer >= tile.break_time:
            game_object.inventory.add(world.tilemap.get_tile(tile_pos), 1)
            world.tilemap.set_tile(tile_pos, None)

            self.break_timer = 0

        self.prev_tile_pos = tile_pos

    def handle_mouse(self, game_object: "Player2", world: "World"):
        mouse = pg.mouse.get_pressed()
        if mouse[0]:
            self.left_click(world, game_object)
        else:
            self.break_timer = 0
        if mouse[2]:
            self.right_click(world, game_object)


class SimpleAIComponent(Component):
    def __init__(self, owner, system: System) -> None:
        super().__init__(owner, system)
        self.update_timer = Timer(0.3, random.random() * 0.3)
        self.speed_x = 0

    def update(self, world: "World"):
        game_object = self.owner
        game_object.components[PhysicsComponent].apply_force_target(
            pg.Vector2(self.speed_x * 10, 0), pg.Vector2(self.speed_x, 0)
        )

        if not self.update_timer.tick(world.dt):
            return super().update()

        sign = math.copysign(1, world.player.pos.x - game_object.pos.x)
        self.speed_x = 2 * sign
        tile_pos = (game_object.pos + pg.Vector2(sign, 0)) // 1
        if game_object.components[PhysicsComponent].grounded:
            if (
                game_object.pos.distance_squared_to(world.player.pos) <= 1**2
                and random.random() < 0.5
            ):
                game_object.components[PhysicsComponent].apply_impulse(
                    pg.Vector2(0, -8)
                )
            elif random.random() < 0.1:
                game_object.components[PhysicsComponent].apply_impulse(
                    pg.Vector2(0, -8)
                )
            elif world.tilemap.is_tile_collidable(tile_pos):
                rect = game_object.components[Collider].rect
                if tile_pos.x + 1 - rect.left < 0.1 or rect.right - tile_pos.x < 0.1:
                    game_object.components[PhysicsComponent].apply_impulse(
                        pg.Vector2(0, -8)
                    )
        return super().update()
