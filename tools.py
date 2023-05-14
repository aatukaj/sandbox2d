import pygame as pg
from settings import TILE_SIZE

def load_img(path, transparent = False):
    if transparent:
        img = pg.image.load(path).convert_alpha()
    else: 
        img = pg.image.load(path).convert()
    return pg.transform.scale_by(img, TILE_SIZE / 16)



class OffsetGroup(pg.sprite.Group):
    def draw(self, surf: pg.Surface, offset=pg.Vector2(0, 0)):
        for sprite in self.sprites():
            surf.blit(sprite.image, sprite.rect.topleft + offset)