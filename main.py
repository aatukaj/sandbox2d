import enum
import pygame as pg

pg.mixer.init()
pg.display.init()

from settings import *

win = pg.display.set_mode((WIDTH, HEIGHT), FLAGS)
print(win)
from world import World
from inventory import ItemStack, InventoryUI, UIBar
from components.input import PlayerInputComponent


class State(enum.Enum):
    INVENTORY = 0
    GAME = 1


def main():
    state = State.GAME
    clock = pg.Clock()
    world = World(win)

    inventory = InventoryUI(world.player.inventory.items[: 9 * 4], 9, 4)
    hotbar = InventoryUI(world.player.inventory.items[-9:], 9, 1)
    uibar = UIBar(
        world.player.components[PlayerInputComponent].dash_timer.duration,
        0,
        pg.FRect(10, 0, 100, 20),
    )
    uibar.rect.bottom = HEIGHT - 10
    hotbar.selected_index = 0
    hotbar.rect.bottom = HEIGHT - 10
    mouse_item_stack = ItemStack()
    background = win.copy()

    debug_on = False

    def debug_draw():
        player = world.player

        lines = []
        try:
            lines.append(f"fps={clock.get_fps():.0f}, {dt=}")
            lines.append(f"player.pos=[{player.rect.x:.2f}, {player.rect.y:.2f}]")
            lines.append(f"player.vel=[{player.vel.x:.2f}, {player.vel.y:.2f}]")
            lines.append(f"player.break_time={player.input_component.break_timer:.2f}")
            lines.append(f"mouse_tile={world.get_mouse_tile_pos()}")
            lines.append(f"paritcles={len(world.pm.particles)}")
            lines.append(f"lights={len(world.lm.lights)}")

        except Exception as ex:
            lines.append(str(ex))
        bg = pg.Surface((170, 80), pg.SRCALPHA)
        bg.fill((0, 0, 0, 125))
        win.blit(bg, (0, 0))
        y = 1

        for line in lines:
            font.render_to(win, (1, y), line, (255, 255, 255))
            y += 10

    while True:
        dt = clock.tick() / 1000
        # throttle dt
        dt = min(dt, 0.2)

        world.player.equipped_stack = hotbar.items[hotbar.selected_index]
        if state == State.GAME:
            world.update(dt)
            hotbar.draw(win)
            uibar.draw(win)
            uibar.value = world.player.components[PlayerInputComponent].dash_timer.time

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
                    world.debug_on = debug_on

                if event.unicode != "" and event.unicode in "123456789":
                    hotbar.selected_index = int(event.unicode) - 1

            if event.type == pg.MOUSEWHEEL:
                hotbar.selected_index = (hotbar.selected_index - event.y) % 9
            if state == State.INVENTORY:
                for ui in [inventory, hotbar, uibar]:
                    ui.handle_event(event, mouse_item_stack)


if __name__ == "__main__":
    main()
