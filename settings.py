import pygame as pg
import pygame.freetype as ft
ft.init()

TILE_SIZE = 16
WIDTH = 480
HEIGHT = 270
FLAGS = pg.SCALED | pg.RESIZABLE

font = ft.Font("textures/scientifica/ttf/scientifica.ttf", 11)