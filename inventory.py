import pygame as pg
import pygame.freetype as ft
import tiles as t
from settings import *


class ItemStack:
    def __init__(self, item, item_count):
        self.item = item
        self.item_count = item_count
        self.rect = 0



class Inventory:
    def __init__(self, width, height, font: ft.Font):
        self.width = width
        self.height = height
        self.items = [ItemStack(t.DIRT, 64) for _ in range(width * height)]

        self.cell_margin = 4
        self.cell_padding = 2
        self.cell_total = self.cell_margin + self.cell_padding + TILE_SIZE

        self.rect_padding = 4
        self.font = font
        self.rect = pg.Rect(
            0,
            0,
            self.cell_total * self.width - self.cell_margin + self.rect_padding * 2,
            self.cell_total * self.height - self.cell_margin + self.rect_padding * 2,
        )
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.item_rects = self.generate_rects()
        self.surface = pg.Surface(self.rect.size)


    def generate_rects(self):
        item_rects = []
        for i in range(self.width * self.height):
            x = i % self.width * self.cell_total + self.rect_padding
            y = i // self.width * self.cell_total + self.rect_padding
            item_rects.append(pg.Rect(x, y, TILE_SIZE + self.cell_padding, TILE_SIZE + self.cell_padding))

        return item_rects

    def handle_event(self, event: pg.Event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(*event.pos):

                    #translate the event pos
                    rect = pg.Rect(event.pos, (1, 1)).move(-self.rect.x, -self.rect.y)
                    collision = rect.collidelist(self.item_rects)
                    if collision != -1:
                        self.items[collision].item = None

    def draw(self, surf: pg.Surface):
        self.surface.fill((120, 120, 120))
        for i, rect in enumerate(self.item_rects):
            pg.draw.rect(self.surface, (0, 0, 0), rect)
            item_stack = self.items[i]
            if item_stack.item is not None:

                self.surface.blit(item_stack.item.img, (rect.x+ self.cell_padding//2,  rect.y+ self.cell_padding//2))
                self.font.render_to(self.surface, (rect.left + 1, rect.top + 1), str(item_stack.item_count), (255, 255, 255))
  
        surf.blit(self.surface, self.rect)
