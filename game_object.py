import pygame as pg
from settings import Tags


class GameObject:
    def __init__(self, x: float, y: float, w: float = 0.0, h: float = 0.0, tag: Tags = Tags.DEFAULT):
        self.vel = pg.Vector2(0, 0)
        self.pos = pg.Vector2(x, y)
        self.tag = tag
        self.components = {}
    
    def add_component(self, component):
        self.components[type(component)] = component


    def update(self, world: "World"):
        pass

    def kill(self):
        for i in self.components.values():
            i.kill()