import pygame as pg
from settings import TILE_SIZE
from tiles import Tiles as t
from item import ItemType
from inventory import Inventory
from tools import load_img, Timer
import abc
import math
from typing import TYPE_CHECKING
import random
if TYPE_CHECKING:
    from world import World


class GameObject:
    def __init__(self, x, y):
        self.vel = pg.Vector2(0, 0)
        self.pos = pg.Vector2(x, y)

    def update(self, world: "World"):
        pass
    
    
class Component(abc.ABC):
    @abc.abstractmethod
    def update(game_object: GameObject, world: "World") -> None:
        pass

class SimpleRenderer(Component):
    def __init__(self, image):
        self.image = image

    def update(self, game_object: GameObject, world: "World") -> None:
        world.draw_image(game_object.pos, self.image)

class PlayerInputComponent(Component):
    def __init__(self):
        self.break_timer = 0
        self.reach = 5

    def update(self, game_object: GameObject, world: "World"):
        self.handle_keys(game_object)
        self.handle_mouse(game_object, world)

    def handle_keys(self, game_object: GameObject):
        keys = pg.key.get_pressed()


        if keys[pg.K_d]:
            game_object.vel.x = max(5, game_object.vel.x)
        if keys[pg.K_a]:
            game_object.vel.x = min(-5, game_object.vel.x)

        if keys[pg.K_SPACE] and game_object.physics_component.grounded:
            game_object.vel.y = -13


        if game_object.physics_component.flying:
            speed_y = 0
            if keys[pg.K_s]:
                speed_y += 3
            if keys[pg.K_w]:
                speed_y -= 3
            game_object.vel.y = speed_y

    def right_click(self, world, tile_pos, game_object):
        if game_object.equipped_stack.is_empty:
            return
        if game_object.equipped_stack.item_data.item_type == ItemType.TILE:
            if not game_object.equipped_stack.item_data.collide(
                tile_pos, game_object.physics_component.rect
            ):
                if world.tilemap.set_tile(
                    tile_pos, game_object.equipped_stack.item_data, replace=False
                ):
                    game_object.equipped_stack.remove(1)

    def handle_mouse(self, game_object: GameObject, world: "World"):
        mouse = pg.mouse.get_pressed()
        tile_pos = world.get_mouse_tile_pos()

        if game_object.pos.distance_to(tile_pos) <= self.reach:
            tile = world.tilemap.get_tile(tile_pos)
            if mouse[0] and tile is not None:
                self.break_timer += world.dt
                if self.prev_tile_pos != tile_pos:
                    self.break_timer = 0

                if self.break_timer >= tile.break_time:
                    game_object.inventory.add(world.tilemap.get_tile(tile_pos), 1)
                    world.tilemap.set_tile(tile_pos, None)

                    self.break_timer = 0

            else:
                self.break_timer = 0

            if mouse[2]:
                self.right_click(world, tile_pos, game_object)
        else:
            self.selected_tile = None

        self.prev_tile_pos = tile_pos


class PhysicsComponent(Component):
    def __init__(self, rect: pg.FRect):
        self.grounded = False
        self.flying = False
        self.gravity = pg.Vector2(0, 20)
        self.rect = rect


    def get_corner_tile_positions(self):
        x1 = self.rect.left // 1
        y1 = self.rect.top// 1
        x2 = self.rect.right// 1
        y2 = self.rect.bottom// 1

        return {
            (x1, y1),
            (x1, y2),
            (x2, y1),
            (x2, y2),
        }

    def update(self, game_object: GameObject, world: "World"):
        dt = world.dt
        self.rect.topleft = game_object.pos.xy
        rect = self.rect
        
        if entity_collisions := world.get_entity_collisions(game_object):
            for collision in entity_collisions:
                dist = pg.Vector2(rect.center).distance_to(collision.center)
                

                if dist < 0.9 and dist != 0:
                    direction = (pg.Vector2(rect.center) - pg.Vector2(collision.center)).normalize()
                    game_object.vel.x = direction.x * 1
                #game_object.vel.y = direction.x * 0.1
        
        game_object.vel += self.gravity * dt
        rect.y += game_object.vel.y * dt
        tile_collisions = world.tilemap.get_collisions(rect)
        self.grounded = False

        if tile_collisions:
            for collision in tile_collisions:
                if game_object.vel.y > 0:
                    game_object.vel.y = 0
                    self.grounded = True
                    rect.bottom = collision.top

                if game_object.vel.y < 0:
                    game_object.vel.y = 0
                    rect.top = collision.bottom
            
        rect.x += game_object.vel.x * dt
        tile_collisions = world.tilemap.get_collisions(rect)
        if tile_collisions:
            for collision in tile_collisions:
                if game_object.vel.x > 0:
                    game_object.vel.x = 0
                    rect.right = collision.left

                if game_object.vel.x < 0:
                    game_object.vel.x = 0
                    rect.left = collision.right

        


        if self.grounded:
            game_object.vel.x-= 20*game_object.vel.x*dt
        game_object.pos.xy = rect.topleft
        

class Player2(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.image = pg.Surface((TILE_SIZE - 3, TILE_SIZE - 3))
        self.image.fill((255, 255, 255))

        self.inventory = Inventory(9 * 5)

        for i, tile in enumerate(t):
            self.inventory.items[i].set_data(tile.value, 999)

        self.input_component = PlayerInputComponent()
        self.physics_component = PhysicsComponent(
            pg.FRect((x, y), pg.Vector2(self.image.get_rect().size) / TILE_SIZE)
        )
        self.render_component = SimpleRenderer(self.image)

    def update(self, world: "World"):
        self.input_component.update(self, world)
        self.physics_component.update(self, world)
        
    def draw(self, world: "World"):
        self.render_component.update(self, world)



class SimpleAIComponent(Component):
    def __init__(self):
        self.update_timer = Timer(0.3, random.random() * 0.3)
        self.speed_x = 0

    def update(self, game_object: GameObject, world: "World"):
        if self.speed_x > 0:
            game_object.vel.x = max(self.speed_x, game_object.vel.x)
        if self.speed_x < 0:
            game_object.vel.x = min(self.speed_x, game_object.vel.x)
        if not self.update_timer.tick(world.dt):
            return

        sign = math.copysign(1,  world.player.pos.x - game_object.pos.x)
        self.speed_x = 2 * sign
        tile_pos = (game_object.pos + pg.Vector2(sign, 0)) // 1
        if game_object.physics_component.grounded:
            if world.tilemap.is_tile_collidable(tile_pos):
                rect = game_object.physics_component.rect
                if tile_pos.x +1 - rect.left < 0.1 or rect.right - tile_pos.x < 0.1:
                    game_object.vel.y = -10

            elif game_object.pos.distance_squared_to(world.player.pos) <= 1**2:
                game_object.vel.y = -10
            if random.random() < 0.1:
                game_object.vel.y = -10

class Enemy1(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pg.Surface((TILE_SIZE - 3, TILE_SIZE - 3))
        self.image.fill((255*random.random(), 0, 0))

        self.input_component = SimpleAIComponent()
        self.physics_component = PhysicsComponent(
            pg.FRect((x, y), pg.Vector2(self.image.get_rect().size) / TILE_SIZE)
        )
        self.render_component = SimpleRenderer(self.image)

    def update(self, world: "World"):
        self.input_component.update(self, world)
        self.physics_component.update(self, world)
        
    def draw(self, world: "World"):
        self.render_component.update(self, world)




#this is lowkey bad, but it works
class TileOverlay(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.breaking_sprites = [
            load_img(f"textures/breaking/{i}.png")
            for i in range(1, 5)
        ]
        self.select_sprite = load_img("textures/select.png")

    def update(self, world: "World"):
        pass

    def draw(self, world: "World"):
        if world.get_mouse_tile_pos().distance_to(world.player.pos) <= world.player.input_component.reach:
            pos = world.get_mouse_tile_pos()
            world.draw_image(pos, self.select_sprite)
            if world.player.input_component.break_timer > 0:
                timer = world.player.input_component.break_timer
                if tile := world.tilemap.get_tile(pos):
                    cur_sprite = self.breaking_sprites[
                            int(timer / tile.break_time * 4)
                        ]
                    world.draw_image(pos, cur_sprite)
