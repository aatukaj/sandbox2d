from settings import TILE_SIZE
from tools import load_img
import pygame as pg
from functools import cached_property
import enum
class Item:
    def __init__(self, img_path, name, item_type, max_stack=64):
        self.img_path = img_path
        self.name = name
        self.max_stack = max_stack
        self.item_type = item_type



    @cached_property
    def img(self):
        #only load the image when its needed
        #also prevents an error where the image tries to load before pg.set_mode has been called
        return load_img(self.img_path)



class ItemType(enum.Enum):
    TILE = 0