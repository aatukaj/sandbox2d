import pygame as pg
from settings import TILE_SIZE
from tilemap import Tilemap
import tiles as t


class Player(pg.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.image = pg.Surface((TILE_SIZE-3, TILE_SIZE-3))
        self.image.fill((255, 255, 255))
        self.rect = pg.FRect((x, y), pg.Vector2(self.image.get_rect().size) / TILE_SIZE)
        self.rect.topleft = (x, y)

        self.vel = pg.Vector2(0, 0)
        self.accel = pg.Vector2(0, 40)
        self.grounded = False
        self.reach = 5
        self.selected_tile = None
        self.break_timer = 0

        self.equipped_stack = None

        self.flying = False

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
        speed_x = 0
        
        if keys[pg.K_d]:
            speed_x += 5
        if keys[pg.K_a]:
            speed_x -= 5
        
        if keys[pg.K_SPACE] and self.grounded:
            self.vel.y = -19
        self.vel.x = speed_x
        
        if self.flying:
            speed_y = 0
            if keys[pg.K_s]:
                speed_y += 5
            if keys[pg.K_w]:
                speed_y -= 5
            self.vel.y = speed_y

    def handle_collision(self, tilemap: Tilemap, dt: float) -> None:
        self.rect.y += self.vel.y * dt
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
        self.rect.x += self.vel.x * dt
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
        mouse_pos = pg.Vector2(pg.mouse.get_pos()) / TILE_SIZE
        tile_pos = world.tilemap.get_tile_coords((mouse_pos + camera) // 1)

        if tile_pos and (self.pos).distance_to(tile_pos) <= self.reach:
            tile = world.tilemap.get_tile(tile_pos)
            prev_tile_pos = self.selected_tile
            self.selected_tile = tile_pos
            if mouse[0] and tile is not None:
                self.break_timer += dt
                if prev_tile_pos != tile_pos:
                    self.break_timer = 0

                if self.break_timer >= tile.break_time:
                    world.tilemap.set_tile(tile_pos, None)
                    self.break_timer = 0

            else:
                self.break_timer = 0

            if mouse[2]:
                if self.equipped_stack and isinstance(self.equipped_stack.item_data, t.Tile):
                    if not t.DIRT.rect.move(*(tile_pos)).colliderect(
                        self.rect
                    ):
                        if world.tilemap.set_tile(tile_pos, t.DIRT, replace=False):
                            self.equipped_stack.remove(1)
        else:
            self.selected_tile = None
