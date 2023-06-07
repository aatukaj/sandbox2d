import pygame as pg
from settings import TILE_SIZE
from tiles import Tiles as t
from inventory import Inventory
from tools import load_img, Timer, get_img_dimensions
import abc
import math
from typing import TYPE_CHECKING, Any, Optional
from customtypes import Coordinate
import random
from event import post_event
from lights import Light
from particle import Particle
if TYPE_CHECKING:
    from world import World
    from inventory import ItemStack


class GameObject:
    def __init__(self, x: float, y: float, w: float = 0.0, h: float = 0.0):
        self.vel = pg.Vector2(0, 0)
        self.rect = pg.FRect(x, y, w, h)

    def update(self, world: "World"):
        pass

    def draw(self, world: "World"):
        pass

    @property
    def pos(self):
        return pg.Vector2(self.rect.topleft)

    @property
    def center(self):
        return pg.Vector2(self.rect.center)

    @pos.setter
    def pos(self, new_pos: Coordinate):
        self.rect.top = new_pos[0]
        self.rect.left = new_pos[1]

    def get_corner_tile_positions(self):
        x1 = self.rect.left // 1
        y1 = self.rect.top // 1
        x2 = self.rect.right // 1
        y2 = self.rect.bottom // 1

        return {
            (x1, y1),
            (x1, y2),
            (x2, y1),
            (x2, y2),
        }


class Component(abc.ABC):
    @abc.abstractmethod
    def update(self, game_object: Any, world: "World") -> None:
        pass


class SimpleRenderer(Component):
    def __init__(self, image: pg.Surface):
        self.image = image

    def update(self, game_object: GameObject, world: "World") -> None:
        world.draw_image(game_object.pos, self.image)


class PlayerInputComponent(Component):
    def __init__(self):
        self.break_timer = 0
        self.reach = 5
        self.dash_timer = Timer(1)
        self.can_dash = False
        self.prev_tile_pos = None
        self.last_keys = pg.key.get_pressed()
        self.shoot_timer = Timer(0.2)

    def update(self, game_object: "Player2", world: "World") -> None:
        if not self.can_dash and self.dash_timer.tick(world.dt):
            self.can_dash = True
        self.handle_keys(game_object, world)
        self.handle_mouse(game_object, world)
        
    def handle_keys(self, game_object: "Player2", world: "World"):
        keys = pg.key.get_pressed()

        if keys[pg.K_d]:
            game_object.physics_component.apply_force_target(
                pg.Vector2(50, 0), pg.Vector2(5, 0)
            )

        if keys[pg.K_a]:
            game_object.physics_component.apply_force_target(
                pg.Vector2(-50, 0), pg.Vector2(-5, 0)
            )

        if keys[pg.K_e] and self.can_dash:
            self.dash(game_object, world, pg.Vector2(10, 0))

        if keys[pg.K_q] and self.can_dash:
            self.dash(game_object, world, pg.Vector2(-10, 0))

        if keys[pg.K_SPACE] and game_object.physics_component.grounded:
            self.jump(game_object)

            
        if game_object.physics_component.flying:
            speed_y = 0
            if keys[pg.K_s]:
                speed_y += 3
            if keys[pg.K_w]:
                speed_y -= 3
            game_object.vel.y = speed_y
        self.last_keys = keys

    def dash(self, game_object: "Player2", world: "World", vec: pg.Vector2):
        self.can_dash = False
        game_object.physics_component.apply_impulse(vec)
        post_event("player_dash", {"game_object": game_object, "vec": vec})

    def jump(self, game_object):   
        game_object.physics_component.apply_impulse(pg.Vector2(0, -13))
        post_event("player_jump", game_object)

    def right_click(self, world: "World", game_object: "Player2"):
        game_object.equipped_stack.right_click(world, game_object)


    def left_click(self, world: "World", game_object: "Player2"):
        tile_pos = world.get_mouse_tile_pos()
        if self.shoot_timer.tick(world.dt):
            p = Particle(2, game_object.center, (tile_pos - game_object.center).normalize()*20, 10, (0, 0, 255))
            world.pm.add([p])
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

        


class PhysicsComponent(Component):
    def __init__(self):
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

    def debug_draw(self, game_object: GameObject, world: "World"):
        center = (game_object.center - world.camera) * TILE_SIZE
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
            center + game_object.vel * 4,
        )

    def handle_force_target(self, game_object, force, target, dt):
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
        c2 = pg.Vector2(collision.center)
        dif = c1 - c2

        if dif != pg.Vector2(0, 0):
            direction = dif.normalize()
        else:
            direction = pg.Vector2(random.random(), random.random()).normalize()
        self.apply_force(direction.elementwise() * pg.Vector2(80, 20))

    def update(self, game_object: GameObject, world: "World"):
        rect = game_object.rect
        dt = world.dt
        self.gravity = world.gravity

        self.apply_force(self.gravity)
        self.apply_friction(game_object)

        if entity_collisions := world.get_entity_collisions(game_object):
            for collision in entity_collisions:
                self.push_away_from_collision(rect, collision)

        for force, target in self.target_forces:
            self.handle_force_target(game_object, force, target, dt)

        for force in self.forces:
            game_object.vel += force * dt
        for impulse in self.impulses:
            game_object.vel += impulse

        self.last_forces = self.forces
        self.forces = []
        self.impulses = []
        self.target_forces = []

        rect.y += game_object.vel.y * dt
        tile_collisions = world.tilemap.get_collisions(game_object)
        self.last_grounded = self.grounded
        self.grounded = False

        if tile_collisions:
            for collision in tile_collisions:
                if game_object.vel.y > 0:
                    game_object.vel.y = 0
                    self.grounded = True
                    rect.bottom = collision.top
                    if not self.last_grounded and isinstance(game_object, Player2):
                        post_event("player_grounded", game_object)
                if game_object.vel.y < 0:
                    game_object.vel.y = 0
                    rect.top = collision.bottom

        rect.x += game_object.vel.x * dt

        tile_collisions = world.tilemap.get_collisions(game_object)
        if tile_collisions:
            for collision in tile_collisions:
                if game_object.vel.x > 0:
                    game_object.vel.x = 0
                    rect.right = collision.left

                if game_object.vel.x < 0:
                    game_object.vel.x = 0
                    rect.left = collision.right


class Player2(GameObject):
    def __init__(self, x: float, y: float):
        self.image = pg.Surface((TILE_SIZE - 3, TILE_SIZE - 3))
        self.image.fill((255, 255, 255))
        super().__init__(x, y, *get_img_dimensions(self.image))

        self.inventory = Inventory(9 * 5)
        self.equipped_stack: ItemStack
        self.max_health = 100
        self.health = self.max_health
        self.inventory.items[0].set_data(t.DIRT, 999)

        self.input_component = PlayerInputComponent()
        self.physics_component = PhysicsComponent()
        self.render_component = SimpleRenderer(self.image)

    def update(self, world: "World"):
        self.input_component.update(self, world)
        self.physics_component.update(self, world)

    def draw(self, world: "World"):
        self.render_component.update(self, world)
        if world.debug_on:
            self.physics_component.debug_draw(self, world)


class SimpleAIComponent(Component):
    def __init__(self):
        self.update_timer = Timer(0.3, random.random() * 0.3)
        self.speed_x = 0

    def update(self, game_object: GameObject, world: "World"):
        game_object.physics_component.apply_force_target(
            pg.Vector2(self.speed_x * 10, 0), pg.Vector2(self.speed_x, 0)
        )

        if not self.update_timer.tick(world.dt):
            return

        sign = math.copysign(1, world.player.pos.x - game_object.pos.x)
        self.speed_x = 2 * sign
        tile_pos = (game_object.pos + pg.Vector2(sign, 0)) // 1
        if game_object.physics_component.grounded:
            if (
                game_object.pos.distance_squared_to(world.player.pos) <= 1**2
                and random.random() < 0.5
            ):
                game_object.physics_component.apply_impulse(pg.Vector2(0, -8))
            elif random.random() < 0.1:
                game_object.physics_component.apply_impulse(pg.Vector2(0, -8))
            elif world.tilemap.is_tile_collidable(tile_pos):
                rect = game_object.rect
                if tile_pos.x + 1 - rect.left < 0.1 or rect.right - tile_pos.x < 0.1:
                    game_object.physics_component.apply_impulse(pg.Vector2(0, -8))


class Enemy1(GameObject):
    def __init__(self, x, y, world):
        self.image = pg.Surface((TILE_SIZE - 3, TILE_SIZE - 3))
        color = (random.randint(100, 255), 0, 0)
        self.image.fill(color)
        super().__init__(x, y, *get_img_dimensions(self.image))
        self.input_component = SimpleAIComponent()
        self.physics_component = PhysicsComponent()
        self.render_component = SimpleRenderer(self.image)
        self.light = Light(50, self.center, (255, 0, 0))

    def update(self, world: "World"):
        self.input_component.update(self, world)
        self.physics_component.update(self, world)
        self.light.pos = self.center
    def draw(self, world: "World"):
        self.render_component.update(self, world)


# this is lowkey bad, but it works
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
