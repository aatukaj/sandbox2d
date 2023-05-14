from settings import TILE_SIZE
from tools import load_img
import pygame as pg
class Tile:
    def __init__(self, img, rect=pg.FRect(0, 0, TILE_SIZE, TILE_SIZE)):
        self.img = img
        self.rect = rect
    
pg.display.init()
DIRT = Tile(load_img("textures/1.png"))
GRASS = Tile(load_img("textures/2.png"))
STONE = Tile(load_img("textures/3.png"))
GRASS_PLANT = Tile(load_img("textures/4.png", transparent=True), rect=None)
WOOD = Tile(load_img("textures/5.png"))
LEAF = Tile(load_img("textures/6.png", transparent=True))
