import enum
import pygame as pg
import pygame.freetype as ft
import numpy

pg.display.init()


from settings import *

win = pg.display.set_mode((WIDTH, HEIGHT), FLAGS)

from world import World
from inventory import Inventory, ItemStack


class State(enum.Enum):
    INVENTORY = 0
    GAME = 1


def main():
    state = State.GAME
    clock = pg.Clock()
    world = World()
    # font = ft.Font("textures/scientifica/bdf/scientifica-11.bdf")
    
    inventory = world.player.inventory
    hotbar = Inventory(9, 1, font)
    hotbar.selected_index = 0
    hotbar.rect.bottom = HEIGHT - 10
    mouse_item_stack = ItemStack()
    background = win.copy()
    debug_on = True

    def debug_draw():
        player = world.player
        lines = [
            f"fps={clock.get_fps():.2f}, {dt=}",
            f"player.pos=[{player.rect.x:.2f}, {player.rect.y:.2f}]",
            f"player.vel={player.vel.xy}",
            f"player.break_time={player.break_timer:.2f}",
            f"player.selected_tile={player.selected_tile}",
        ]
        bg = pg.Surface((170, 80), pg.SRCALPHA)
        bg.fill((0, 0, 0, 125))
        win.blit(bg, (0, 0))
        y = 1
        for line in lines:
            font.render_to(win, (1, y), line, (255, 255, 255))
            y += 10

    while True:
        dt = clock.tick(144) / 1000
        world.player.equipped_stack = hotbar.items[hotbar.selected_index]
        if state == State.GAME:
            world.update(dt)

            world.draw(win)
            hotbar.draw(win)

        if state == State.INVENTORY:
            win.blit(background, (0, 0))
            inventory.draw(win)
            hotbar.draw(win)
            if mouse_item_stack:
                mpos = pg.Vector2(pg.mouse.get_pos())
                mouse_item_stack.draw(font, *(mpos - pg.Vector2(TILE_SIZE / 2)), win)
        if debug_on:
            debug_draw()
        pg.display.flip()

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
                if event.key == pg.K_TAB:
                    debug_on = not debug_on

                if event.unicode != "" and event.unicode in "123456789":
                    hotbar.selected_index = int(event.unicode) - 1

            if event.type == pg.MOUSEWHEEL:
                hotbar.selected_index = (
                    hotbar.selected_index - numpy.sign(event.y)
                ) % 9
            if state == State.INVENTORY:
                for ui in [inventory, hotbar]:
                    ui.handle_event(event, mouse_item_stack)


if __name__ == "__main__":
    main()
