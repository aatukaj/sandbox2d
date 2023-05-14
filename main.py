import pygame as pg
from settings import *

pg.display.init()
pg.mixer.init()
win = pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED | pg.RESIZABLE)

from world import World
def main():
    clock = pg.Clock()
    world = World()
    while True:
        dt = clock.tick() / 1000

        world.update(dt)
        world.draw(win)
        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                raise SystemExit
            
if __name__ == "__main__":
    main()