from .base import System, Component
import pygame as pg
from settings import TILE_SIZE


class RenderSystem(System):
    def __init__(self):
        super().__init__()

    def update(self, world):
        self.components = [i for i in self.components if i.update(world)]
        return super().update()


class SimpleRenderer(Component):
    def __init__(self, owner, system: System, image: pg.Surface) -> None:
        super().__init__(owner, system)
        self.image = image
        self.size = pg.Vector2(self.image.get_size())

    def update(self, world: "World") -> bool:
        world.draw_image(self.owner.pos - self.size / 2 / TILE_SIZE, self.image)
        return super().update()
