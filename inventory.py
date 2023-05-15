import pygame as pg
import tiles as t
from settings import *


class ItemCell:
    def __init__(self):
        self.item
        self.item_count = 0
        self.rect = 0

class Inventory:
    def __init__(self, width, height):
        self.width = width
        self.height = height 
        self.items = [[(t.DIRT, t.GRASS)[(x+y)%2] for x in range(width)] for y in range(height)]
        self.width = width
        self.height = height
    
    def draw(self, surf):
        cell_margin = 4
        cell_padding = 2
        total = cell_margin + cell_padding + TILE_SIZE

        screen_width = (total)*self.width-cell_margin
        offset_x = WIDTH//2 - screen_width//2

        screen_height = (total)*self.height-cell_margin
        offset_y = (HEIGHT*(2/4)) - screen_height//2

        padding = 3

        pg.draw.rect(surf, (120, 120, 120), (offset_x-padding, offset_y-padding, screen_width+padding*2, screen_height+padding*2))
        for y, row in enumerate(self.items):
            for x, item in enumerate(row):
                pg.draw.rect(surf, (255, 255, 255), (x*(total) + offset_x, y*(total)  + offset_y, TILE_SIZE+cell_padding, TILE_SIZE+cell_padding))
                surf.blit(item.img, (x*(total)+cell_padding/2 + offset_x, y*(total)+cell_padding/2 + offset_y))