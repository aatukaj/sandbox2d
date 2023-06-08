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
from event import post_event
from lights import Light
from particle import Particle
if TYPE_CHECKING:
    from world import World
    from inventory import ItemStack
from tools import *
from components.collider import Collider
from components.render import SimpleRenderer
from components.physics import PhysicsComponent

class GameObject:
    def __init__(self, x: float, y: float, w: float = 0.0, h: float = 0.0, tag: Tags = Tags.DEFAULT):
        self.vel = pg.Vector2(0, 0)
        self.pos = pg.Vector2(x, y)
        self.tag = tag
        self.components = {}
    
    def add_component(self, component):
        self.components[type(component)] = component

    def update(self, world: "World"):
        pass


class Projectile(GameObject):
    def __init__(self, x: float, y: float, vel: pg.Vector2, world: "World"):
        super().__init__(x, y, 0.5, 0.5, Tags.PROJECTILE)
        self.add_component(Collider(0.5, 0.5, self, world.cs))
        self.vel = vel
        img = pg.Surface(pg.Vector2(0.5, 0.5) * TILE_SIZE)
        self.color = [hexstr2tuple("#68386c"), hexstr2tuple("#b55088"), hexstr2tuple("#f6757a")][random.randint(0, 2)]
        self.light = Light(img.get_size()[0] * 8, self.pos, self.color)
        img.fill(self.color)
        self.add_component(SimpleRenderer(self, world.rs, img))

    def update(self, world: "World"):
        self.pos.x += self.vel.x * world.dt
        self.pos.y += self.vel.y * world.dt
        self.vel += world.gravity * world.dt
        self.light.pos = self.pos
        cols = world.tilemap.get_collisions(self)
        if cols:
            post_event("projectile_explosion", self)
            world.tilemap.set_tile(self.pos + self.vel, None)
            self.light.kill()
            return 0
        return 1
    def draw(self, world):
        self.render_component.update(self, world)

class Component(abc.ABC):
    @abc.abstractmethod
    def update(self, game_object: Any, world: "World") -> None:
        pass




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
        game_object.components[PhysicsComponent].right_click(world, game_object)


    def left_click(self, world: "World", game_object: "Player2"):
        tile_pos = world.get_mouse_tile_pos()
        if self.shoot_timer.tick(world.dt):
            p = Projectile(0, 0, (tile_pos - game_object.pos).normalize()*20, world)
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


class Player2(GameObject):
    def __init__(self, x: float, y: float, world):
        self.image = pg.Surface((TILE_SIZE - 3, TILE_SIZE - 3))
        self.image.fill((255, 255, 255))
        super().__init__(x, y, tag=Tags.PLAYER)
        self.add_component(Collider(*(pg.Vector2(self.image.get_size()) / TILE_SIZE), self, world.cs))
        self.add_component(SimpleRenderer(self, world.rs, self.image))
        self.add_component(PhysicsComponent(self, world.ps))
        self.inventory = Inventory(9 * 5)
        self.equipped_stack: ItemStack
        self.max_health = 100
        self.health = self.max_health
        self.inventory.items[0].set_data(t.DIRT, 999)

        self.input_component = PlayerInputComponent()
 

    def update(self, world: "World"):
        self.input_component.update(self, world)
        return 1


class SimpleAIComponent(Component):
    def __init__(self):
        self.update_timer = Timer(0.3, random.random() * 0.3)
        self.speed_x = 0

    def update(self, game_object: GameObject, world: "World"):
        game_object.components[PhysicsComponent].apply_force_target(
            pg.Vector2(self.speed_x * 10, 0), pg.Vector2(self.speed_x, 0)
        )

        if not self.update_timer.tick(world.dt):
            return

        sign = math.copysign(1, world.player.pos.x - game_object.pos.x)
        self.speed_x = 2 * sign
        tile_pos = (game_object.pos + pg.Vector2(sign, 0)) // 1
        if game_object.components[PhysicsComponent].grounded:
            if (
                game_object.pos.distance_squared_to(world.player.pos) <= 1**2
                and random.random() < 0.5
            ):
                game_object.components[PhysicsComponent].apply_impulse(pg.Vector2(0, -8))
            elif random.random() < 0.1:
                game_object.components[PhysicsComponent].apply_impulse(pg.Vector2(0, -8))
            elif world.tilemap.is_tile_collidable(tile_pos):
                rect = game_object.components[Collider].rect
                if tile_pos.x + 1 - rect.left < 0.1 or rect.right - tile_pos.x < 0.1:
                    game_object.components[PhysicsComponent].apply_impulse(pg.Vector2(0, -8))


class Enemy1(GameObject):
    def __init__(self, x, y, world):
        self.image = pg.Surface((TILE_SIZE - 3, TILE_SIZE - 3))
        color = hexstr2tuple("#63c74d")
        self.image.fill(color)
        super().__init__(x, y, *get_img_dimensions(self.image), tag=Tags.ENEMY)
        self.add_component(Collider(*get_img_dimensions(self.image), self, world.cs))
        self.input_component = SimpleAIComponent()
        self.add_component(PhysicsComponent(self, world.ps))
        self.add_component(SimpleRenderer(self, world.rs, self.image))
        self.light = Light(50, self.pos, color)

    def update(self, world: "World"):
        self.input_component.update(self, world)
        self.light.pos = self.pos
        return 0


# this is doesnt work rn
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
