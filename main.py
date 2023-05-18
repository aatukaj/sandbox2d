import ez_profile

import enum
import pygame as pg
import pygame.freetype as ft
pg.init()

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
    hotbar.rect.bottom = HEIGHT-10
    grabbed_item = None
    background = win.copy()
    while True:
        dt = clock.tick() / 1000
        if state == State.GAME:
            world.update(dt)
            world.draw(win)
        elif state == State.INVENTORY:
            win.blit(background, (0, 0))
            inventory.draw(win)
        hotbar.draw(win)
        if grabbed_item:
            mpos = pg.Vector2(pg.mouse.get_pos())
            win.blit(grabbed_item.item.img, (mpos - pg.Vector2(TILE_SIZE/2)))
        pg.display.update()
        

        for event in pg.event.get():
            if event.type == pg.QUIT:
                raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if state== State.INVENTORY:
                        grabbed_item = None
                        state = State.GAME
                    else: 
                        state = State.INVENTORY
                        background = win.copy()

                if event.unicode in "123456789":
                    print(event.unicode)
            if state == State.INVENTORY:
                for ui in [inventory, hotbar]:
                    grabbed_item = ui.handle_event(event, grabbed_item)
                    if grabbed_item:
                        break



if __name__ == "__main__":
    main()
