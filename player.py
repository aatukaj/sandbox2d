import pygame as pg
from settings import TILE_SIZE, font
from tilemap import Tilemap
from tiles import Tiles as t
from item import ItemType
from inventory import Inventory
from tools import load_img
import abc

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world import World


class GameObject:
    def __init__(self, x, y):
        self.vel = pg.Vector2(0, 0)
        self.rect = pg.FRect(x, y, 1, 1)

    @property
    def pos(self) -> pg.Vector2:
        return pg.Vector2(self.rect.topleft)

    @property
    def center(self) -> pg.Vector2:
        return pg.Vector2(self.rect.center)


class PhysicsComponent:
    def __init__(self):
        self.grounded = False
        self.flying = False
        self.gravity = pg.Vector2(0, 20)

    def update(self, game_object: GameObject, world: "World", dt: float):
        tilemap = world.tilemap
        rect = game_object.rect
        old_rect = rect.copy()
        game_object.vel += self.gravity * dt
        rect.y += game_object.vel.y * dt

        collisions = tilemap.get_collisions(rect)

        if collisions:
            for collision in collisions:
                if rect.bottom >= collision.top and old_rect.bottom <= collision.top:
                    game_object.vel.y = 0
                    self.grounded = True
                    rect.bottom = collision.top

                elif rect.top <= collision.bottom and old_rect.top >= collision.bottom:
                    game_object.vel.y = 0
                    rect.top = collision.bottom
        else:
            self.grounded = False
        rect.x += game_object.vel.x * dt
        collisions = tilemap.get_collisions(rect)
        if collisions:
            for collision in collisions:
                if rect.right >= collision.left and old_rect.right <= collision.left:
                    game_object.vel.x = 0
                    rect.right = collision.left

                elif rect.left <= collision.right and old_rect.left >= collision.right:
                    game_object.vel.x = 0
                    rect.left = collision.right


class SimpleRenderer:
    def __init__(self, image):
        self.image = image

    def update(self, game_object: GameObject, world: "World") -> None:
        world.surf.blit(
            self.image, (game_object.pos - world.camera) * TILE_SIZE
        )


class InputComponent(abc.ABC):
    @abc.abstractmethod
    def update(game_object: GameObject, world: "World") -> None:
        pass


class PlayerInputComponent(InputComponent):
    def __init__(self):
        self.break_timer = 0
        self.reach = 5
        self.selected_tile = None

    def update(self, game_object: GameObject, world: "World"):
        self.handle_keys(game_object)
        self.handle_mouse(game_object, world)

    def handle_keys(self, game_object: GameObject):
        keys = pg.key.get_pressed()
        speed_x = 0

        if keys[pg.K_d]:
            speed_x += 5
        if keys[pg.K_a]:
            speed_x -= 5

        if keys[pg.K_SPACE] and game_object.physics_component.grounded:
            game_object.vel.y = -13
        game_object.vel.x = speed_x

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
                tile_pos, game_object.rect
            ):
                if world.tilemap.set_tile(
                    tile_pos, game_object.equipped_stack.item_data, replace=False
                ):
                    game_object.equipped_stack.remove(1)

    def handle_mouse(self, game_object: GameObject, world: "World"):
        mouse = pg.mouse.get_pressed()
        mouse_pos = pg.Vector2(pg.mouse.get_pos()) / TILE_SIZE
        tile_pos = world.tilemap.get_tile_coords((mouse_pos + world.camera) // 1)
        if tile_pos and (game_object.pos).distance_to(tile_pos) <= self.reach:
            tile = world.tilemap.get_tile(tile_pos)
            prev_tile_pos = self.selected_tile
            self.selected_tile = tile_pos
            if mouse[0] and tile is not None:
                self.break_timer += world.dt
                if prev_tile_pos != tile_pos:
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


class Player2(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.vel = pg.Vector2(0, 0)

        self.image = pg.Surface((TILE_SIZE - 3, TILE_SIZE - 3))
        self.image.fill((255, 255, 255))
        self.rect = pg.FRect((x, y), pg.Vector2(self.image.get_rect().size) / TILE_SIZE)
        self.rect.topleft = (x, y)

        self.inventory = Inventory(9 * 5)


        for i, tile in enumerate(t):
            self.inventory.items[i].set_data(tile.value, 999)

        self.input_component = PlayerInputComponent()
        self.physics_component = PhysicsComponent()
        self.render_component = SimpleRenderer(self.image)

    def update(self, world: "World"):
        self.input_component.update(self, world)
        self.physics_component.update(self, world, world.dt)
        self.render_component.update(self, world)


class TileOverlay(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.breaking_sprites = [
            load_img(f"textures/breaking/{i}.png", transparent=True)
            for i in range(1, 5)
        ]
        self.select_sprite = load_img("textures/select.png", transparent=True)

    def update(self, world: "World"):
        if tile := world.player.input_component.selected_tile:
            pos = (tile - world.camera) * TILE_SIZE
            world.surf.blit(self.select_sprite, (pos))
            if world.player.input_component.break_timer > 0:
                timer = world.player.input_component.break_timer
                world.surf.blit(
                    self.breaking_sprites[
                        int(timer / world.tilemap.get_tile(tile).break_time * 4)
                    ],
                    pos,
                )
