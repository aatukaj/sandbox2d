import pygame as pg
import pygame.freetype as ft
ft.init()

TILE_SIZE = 16
HEIGHT = 360
WIDTH = HEIGHT//9 * 14

FLAGS = pg.SCALED | pg.RESIZABLE
#FLAGS = pg.SCALED | pg.RESIZABLE | pg.FULLSCREEN
font = ft.Font("textures/scientifica/ttf/scientifica.ttf", 11)