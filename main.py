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



    while True:
        dt = clock.tick() / 1000
        if state == State.GAME:
            world.update(dt)
            world.draw(win)
        elif state == State.INVENTORY:
            inventory.draw(win)
        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    state = State.INVENTORY if state == State.GAME else State.GAME
            if state == State.INVENTORY:
                inventory.handle_event(event)


if __name__ == "__main__":
    main()
