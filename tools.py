import pygame as pg
from settings import TILE_SIZE


def load_img(path: str, transparent: bool = False) -> pg.Surface:
    img = pg.image.load(path).convert_alpha()
    return pg.transform.scale_by(img, TILE_SIZE / 16)


def get_img_dimensions(image: pg.Surface):
    return pg.Vector2(image.get_rect().size) / TILE_SIZE


class Timer:
    def __init__(self, duration: float, initial_time: float = 0.0):
        self.time = initial_time
        self.duration = duration

    def tick(self, dt: float) -> bool:
        self.time = self.time % self.duration
        self.time += dt
        if self.time >= self.duration:
            return True
        return False


def hexstr2tuple(s: str) -> tuple[int, int, int]:
    num = int(s.strip("#"), 16)
    return (num >> 16 & 0xff, (num >> 8) & 0xff, num & 0xff)


