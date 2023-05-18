import pygame as pg
from settings import TILE_SIZE
from tilemap import Tilemap
import tiles as t


class Player(pg.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.image = pg.Surface((TILE_SIZE - 2, TILE_SIZE - 2))
        self.image.fill((255, 255, 255))
        self.rect = pg.FRect(self.image.get_rect())
        self.rect.topleft = (x, y)
        self.vel = pg.Vector2(0, 0)
        self.accel = pg.Vector2(0, 1000)
        self.grounded = False
        self.reach = 5
        self.selected_tile = None
        self.break_timer = 0

        self.equipped_item = None

    def update(self, dt: float, tile_group: Tilemap) -> None:
        self.old_rect = self.rect.copy()
        self.handle_input()

        self.handle_collision(tile_group, dt)
        self.vel += self.accel * dt

    @property
    def pos(self) -> pg.Vector2:
        return pg.Vector2(self.rect.topleft)

    @property
    def center(self) -> pg.Vector2:
        return pg.Vector2(self.rect.center)

    def handle_input(self):
        keys = pg.key.get_pressed()
        speed = 0
        if keys[pg.K_d]:
            speed += 80
        if keys[pg.K_a]:
            speed -= 80
        if keys[pg.K_SPACE] and self.grounded:
            self.vel.y = -300
        self.vel.x = speed

    def handle_collision(self, tilemap: Tilemap, dt:float) -> None:
        self.rect.top += self.vel.y * dt
        collisions = tilemap.get_collisions(self.rect)

        if collisions:
            for collision in collisions:
                if (
                    self.rect.bottom >= collision.top
                    and self.old_rect.bottom <= collision.top
                ):
                    self.vel.y = 0
                    self.grounded = True
                    self.rect.bottom = collision.top

                elif (
                    self.rect.top <= collision.bottom
                    and self.old_rect.top >= collision.bottom
                ):
                    self.vel.y = 0
                    self.rect.top = collision.bottom
        else:
            self.grounded = False
        self.rect.left += self.vel.x * dt
        collisions = tilemap.get_collisions(self.rect)
        if collisions:
            for collision in collisions:
                if (
                    self.rect.right >= collision.left
                    and self.old_rect.right <= collision.left
                ):
                    self.vel.x = 0
                    self.rect.right = collision.left

                elif (
                    self.rect.left <= collision.right
                    and self.old_rect.left >= collision.right
                ):
                    self.vel.x = 0
                    self.rect.left = collision.right

    def handle_mouse(self, camera, world, dt):
        mouse = pg.mouse.get_pressed()
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        tile_pos = world.tilemap.get_tile_coords(mouse_pos + camera)

        if tile_pos and (self.pos / TILE_SIZE).distance_to(tile_pos) <= self.reach:
            tile = world.tilemap.get_tile(tile_pos)
            prev_tile_pos = self.selected_tile
            self.selected_tile = tile_pos
            if mouse[0]:
                if tile is not None:
                    self.break_timer += dt
                    if prev_tile_pos != tile_pos:
                        self.break_timer = 0
                    if self.break_timer >= tile.break_time:
                        world.tilemap.set_tile(tile_pos, None)
                        self.break_timer = 0
                else:
                    self.break_timer = 0
            else:
                self.break_timer = 0

            if mouse[2]:
                if not t.DIRT.rect.move(*(tile_pos*TILE_SIZE)).colliderect(self.rect):
                    world.tilemap.set_tile(tile_pos, t.DIRT, replace = False)
        else:
            self.selected_tile = None
