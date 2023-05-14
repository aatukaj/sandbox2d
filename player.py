import pygame as pg
from settings import TILE_SIZE
from tilemap import Tilemap

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

    def update(self, dt, tile_group):
        self.old_rect = self.rect.copy()
        self.handle_input()

        self.handle_collision(tile_group, dt)
        self.vel += self.accel * dt

    @property
    def pos(self):
        return pg.Vector2(self.rect.topleft)

    def handle_input(self):
        keys = pg.key.get_pressed()
        speed = 0
        if keys[pg.K_d]:
            speed += 200
        if keys[pg.K_a]:
            speed -= 200
        if keys[pg.K_SPACE] and self.grounded:
            self.vel.y = -300
        self.vel.x = speed

    def handle_collision(self, tilemap: Tilemap, dt):
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