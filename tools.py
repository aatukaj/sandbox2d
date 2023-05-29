import pygame as pg
from settings import TILE_SIZE

def load_img(path, transparent = False):
    img = pg.image.load(path).convert_alpha()

    return pg.transform.scale_by(img, TILE_SIZE / 16)



class OffsetGroup(pg.sprite.Group):
    def draw(self, surf: pg.Surface, offset=pg.Vector2(0, 0)):
        for sprite in self.sprites():
            surf.blit(sprite.image, (sprite.rect.topleft + offset) * TILE_SIZE)


class Timer:
    def __init__(self, duration, initial_time = 0):
        self.time = initial_time
        self.duration = duration
    def tick(self, dt):
        self.time += dt
        if self.time >= self.duration:
            self.time = self.time % self.duration
            return True
        return False