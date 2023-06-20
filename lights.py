import pygame as pg
from settings import TILE_SIZE, WIDTH, HEIGHT
from event import subscribe, post_event
from typing import Optional

class Light:
    img_cache = {}
    def __init__(self, radius: int, pos: pg.Vector2, color: tuple[int, int, int], parent : Optional["GameObject"] = None):
        self.radius = radius
        self.pos = pos
        self.color = color
        post_event("light_added", self)
        self.alive = True
        self.parent = parent

    def kill(self):
        post_event("light_killed", self)

    def update(self, world):
        if self.parent:
            self.pos = self.parent.pos

    @property
    def img(self):
        key = (self.radius, self.color)
        if img := self.img_cache.get(key, None):
            pass
        else:
            lights = [255]
            img = pg.Surface((self.radius*2, self.radius*2))
            for i in range(1, 255):
                val = lights[i - 1] - i * 0.1
                if val < 0:
                    break
                lights.append(val)

            n = len(lights)
            for i in range(n):
                val = (255 - lights[i]) / 255
                pg.draw.circle(img, (val * self.color[0], val * self.color[1], val * self.color[2]), (self.radius, self.radius), (n - i) / n * self.radius)
            self.img_cache[key] = img
        return img

class LightManager:
    def __init__(self) -> None:
        self.lights: list[Light] = []
        self.light_surf = pg.Surface((WIDTH, HEIGHT))
        subscribe("light_added", self.add)
        subscribe("light_killed", self.remove)

    def add(self, light: Light):
        self.lights.append(light)

    def remove(self, light: Light):
        self.lights.remove(light)    

    def draw(self, world: "World", debug: bool = False):
        self.light_surf.fill((5, 5, 5))
        draw_list = []

        for l in self.lights:
            l.update(world)
            draw_list.append((l.img, (l.pos - world.camera) * TILE_SIZE - pg.Vector2(l.radius)))


        self.light_surf.fblits(
            draw_list, pg.BLEND_MAX
        )
        if debug:
            world.surf.blit(self.light_surf, (0, 0))
        else:
            world.surf.blit(self.light_surf, (0, 0), special_flags=pg.BLEND_MULT)
