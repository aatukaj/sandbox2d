import pygame as pg
import pygame.freetype as ft
import tiles as t
from settings import *


class ItemStack:
    def __init__(self, item_data=None, stack_size=-1):
        self.item_data = item_data
        self.stack_size = stack_size

    def clear(self):
        self.item_data = None
        self.stack_size = -1

    def is_empty(self):
        return self.item_data is None and self.stack_size == -1

    def combine(self, other):
        if self.is_empty():
            self.set_data(other.item_data, other.stack_size)
            other.clear()

        elif other.item_data == self.item_data:
            new_stack_size = self.stack_size + other.stack_size
            if new_stack_size > self.item_data.max_stack:
                other.remove(self.item_data.max_stack - self.stack_size)
                self.stack_size = self.item_data.max_stack
            else:
                self.stack_size += other.stack_size
                other.clear()

    def remove(self, amount):
        self.stack_size -= amount
        if self.stack_size <= 0:
            self.clear()

    def set_data(self, item_data, stack_size):
        self.item_data = item_data
        self.stack_size = stack_size

    def draw(self, font, x, y, surf):
        if self.item_data is None:
            return
        surf.blit(self.item_data.img, (x, y))
        if self.stack_size > 1:
            font.render_to(surf, (x, y), str(self.stack_size), (255, 255, 255))


class Inventory:
    def __init__(self, width, height, font: ft.Font):
        self.width = width
        self.height = height
        self.items = [ItemStack() for _ in range(width * height)]
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

    def add(self, item_data, stack_size):
        add_item_stack = ItemStack(item_data, stack_size)
        for item_stack in self.items:
            item_stack.combine(add_item_stack)
            if add_item_stack.is_empty():
                break


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

    def handle_event(self, event: pg.Event, mouse_item_stack):
        if (
            event.type != pg.MOUSEBUTTONDOWN
            or event.button != 1
            or not self.rect.collidepoint(*event.pos)
        ):
            return

        # translate the event pos
        rect = pg.Rect(event.pos, (1, 1)).move(-self.rect.x, -self.rect.y)
        collision = rect.collidelist(self.item_rects)

        # collision is -1 when there aren't any collisions
        if collision == -1:
            return

        itemstack = self.items[collision]

        if mouse_item_stack.is_empty():
            mouse_item_stack.combine(itemstack)

        else:
            itemstack.combine(mouse_item_stack)

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


class InventoryUI:
    def __init__(self, item_stacks):
        self.item_stacks = item_stacks