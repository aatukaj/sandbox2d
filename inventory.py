import pygame as pg
import pygame.freetype as ft
import tiles as t
from settings import *


class ItemStack:
    def __init__(self, item, item_count):
        self.item = item
        self.item_count = item_count
        self.rect = 0

    def draw(self, font, x, y, surf):
        surf.blit(self.item.img, (x, y))
        if self.item_count > 1:
            font.render_to(surf, (x, y), str(self.item_count), (255, 255, 255))


class Inventory:
    def __init__(self, width, height, font: ft.Font):
        self.width = width
        self.height = height
        self.items = [ItemStack(t.DIRT, i + 1) for i in range(width * height)]
        self.selected_index = None

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
            item_rects.append(
                pg.Rect(
                    x, y, TILE_SIZE + self.cell_padding, TILE_SIZE + self.cell_padding
                )
            )

        return item_rects

    def handle_event(self, event: pg.Event, grabbed_item):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(*event.pos):
                    # translate the event pos
                    rect = pg.Rect(event.pos, (1, 1)).move(-self.rect.x, -self.rect.y)
                    collision = rect.collidelist(self.item_rects)

                    # collision is -1 when there aren't any collisions
                    if collision != -1:
                        itemstack = self.items[collision]
                        if grabbed_item is None:
                            self.items[collision] = None
                            return itemstack
                        else:
                            if itemstack is None:
                                self.items[collision] = grabbed_item
                            else:
                                itemstack.item_count += grabbed_item.item_count
                            return None
        return grabbed_item

    def draw(self, surf: pg.Surface):
        self.surface.fill("#181425")
        pg.draw.rect(self.surface, "#262b44", ((0, 0), self.rect.size), width=1)
        for i, rect in enumerate(self.item_rects):
            pg.draw.rect(self.surface, "#262b44", rect)
            if self.selected_index == i:
                pg.draw.rect(self.surface, "#feae34", rect, width=1)
            item_stack = self.items[i]
            if item_stack is not None:
                item_stack.draw(
                    self.font,
                    rect.x + self.cell_padding // 2,
                    rect.y + self.cell_padding // 2,
                    self.surface,
                )

        surf.blit(self.surface, self.rect)
