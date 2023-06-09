from typing import Any
from .base import Component, System
import pygame as pg
from typing import Dict, Tuple
from settings import Tags
class ColliderSystem(System):
    def __init__(self):
        super().__init__()
        self.collision_dict = {}

    def update_collision_dict(self):
        collision_dict: Dict[Tuple[float, float], list["Collider"]] = {}
        for obj in self.components:
            for i in obj.get_corner_tile_positions():
                if i in collision_dict:
                    collision_dict[i].append(obj)
                else:
                    collision_dict[i] = [obj]
        self.collision_dict = collision_dict
    
    def update(self):
        self.components = [i for i in self.components if i.update()]
        self.update_collision_dict()
        

    def get_entity_collisions(self, collider: "Collider") -> list["Collider"]:
        collisions: list["Collider"] = []
        for pos in collider.get_corner_tile_positions():
            colls = self.collision_dict.get(pos)
            if not colls: continue
            for col in colls:
                if col != collider:
                    if (col.tags == [] or collider.owner.tag in col.tags) and collider.rect.colliderect(col.rect) and col not in collisions:
                        collisions.append(col)
        return collisions
    

class Collider(Component):
    def __init__(self, w, h, owner, collider_system : ColliderSystem, tags : list[Tags] = []) -> None:
        super().__init__(owner, collider_system)
        self.rect = pg.FRect(0, 0, w, h)
        self.tags = tags
        print(self.tags)
        self.rect.center = self.owner.pos
        collider_system.components.append(self)

    def update(self) -> bool:
        self.rect.center = self.owner.pos
        return super().update()

    def get_corner_tile_positions(self):
        x1 = self.rect.left // 1
        y1 = self.rect.top // 1
        x2 = self.rect.right // 1
        y2 = self.rect.bottom // 1

        return {
            (x1, y1),
            (x1, y2),
            (x2, y1),
            (x2, y2),
        }
