import ez_profile

import enum
import pygame as pg
import pygame.freetype as ft
import numpy


pg.display.init()
ft.init()

from settings import *

win = pg.display.set_mode((WIDTH, HEIGHT), FLAGS)

from world import World
from inventory import Inventory


class State(enum.Enum):
    INVENTORY = 0
    GAME = 1


def main():
    state = State.GAME
    clock = pg.Clock()
    world = World()
    font = ft.Font("textures/scientifica/bdf/scientifica-11.bdf")
    inventory = Inventory(9, 4, font)
    hotbar = Inventory(9, 1, font)
    hotbar.selected_index = 0
    hotbar.rect.bottom = HEIGHT - 10
    grabbed_item = None
    background = win.copy()
    while True:
        dt = clock.tick() / 1000
        world.player.equipped_stack = hotbar.items[hotbar.selected_index]
        if state == State.GAME:
            world.update(dt)

            world.draw(win)
            hotbar.draw(win)

        if state == State.INVENTORY:
            win.blit(background, (0, 0))
            inventory.draw(win)
            hotbar.draw(win)
            if grabbed_item:
                mpos = pg.Vector2(pg.mouse.get_pos())
                grabbed_item.draw(font, *(mpos - pg.Vector2(TILE_SIZE / 2)), win)

        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if state == State.INVENTORY:
                        state = State.GAME
                    else:
                        state = State.INVENTORY
                        background = win.copy()

                if event.unicode != "" and event.unicode in "123456789":

                    hotbar.selected_index = int(event.unicode) - 1

            if event.type == pg.MOUSEWHEEL:
                hotbar.selected_index = (
                    hotbar.selected_index - numpy.sign(event.y)
                ) % 9
            if state == State.INVENTORY:
                for ui in [inventory, hotbar]:
                    grabbed_item = ui.handle_event(event, grabbed_item)
                    


if __name__ == "__main__":
    main()
