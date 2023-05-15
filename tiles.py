from settings import TILE_SIZE
from tools import load_img
import pygame as pg
from functools import cached_property
class Tile:
    def __init__(self, img_path, transparent = False, rect=pg.FRect(0, 0, TILE_SIZE, TILE_SIZE), break_time = 0.5, break_level = 0):
        self.img_path = img_path
        self.transparent = transparent
        self.rect = rect
        self.break_time = break_time
        self.break_level = break_level

    
    @cached_property
    def img(self):
        #only load the image when its needed
        #also prevents an error where the image tries to load before pg.set_mode has been called
        return load_img(self.img_path, self.transparent)
        

DIRT = Tile("textures/1.png", break_time = 0.5)
GRASS = Tile("textures/2.png", break_time = 0.5)
STONE = Tile("textures/3.png")
GRASS_PLANT = Tile("textures/4.png", transparent=True, rect=None, break_time = 0.25)
WOOD = Tile("textures/5.png")
LEAF = Tile("textures/6.png", transparent=True)

