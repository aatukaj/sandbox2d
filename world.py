import random
from tilemap import Tilemap

from player import Player2, TileOverlay, Enemy1, GameObject
from settings import *

from customtypes import Coordinate
import pygame as pg

from particle import ParticleManager, Particle
from event import subscribe

from lights import Light, LightManager

from tools import hexstr2tuple

from world_gen import WorldGenerator

from components.collider import ColliderSystem
from components.render import RenderSystem
from components.physics import PhysicsSystem
from components.input import InputSystem

class World:
    def __init__(self, surface: pg.Surface):
        self.cs = ColliderSystem()
        self.rs = RenderSystem()
        self.ps = PhysicsSystem()
        self.ins = InputSystem()
        self.pm = ParticleManager()
        self.lm = LightManager()

        self.surf = surface
        self.layer0: list[GameObject] = []
        self.tilemap = Tilemap(5000, 500)
        self.player = Player2(
            self.tilemap.width // 2, self.tilemap.height // 2 - 5, self
        )
        self.gravity = pg.Vector2(0, 15)
        self.layer0.append(self.player)
        
        self.cam_light = Light(75, self.player.pos, (200, 200, 200))
        
        for i in range(1):
            self.layer0.append(Enemy1(*(self.player.pos - pg.Vector2(5, 5 + i)), self))
        self.layer0.append(TileOverlay(0, 0))
        self.camera = pg.Vector2()

        WorldGenerator(self.tilemap).generate_tiles()

        self.debug_on: bool = False
        
        self.projectiles = []

        self.sounds = {}
        self.background = self.generate_background(0.001)
        self.background2 = self.generate_background(0.002)
        self.background3 = self.generate_background(0.003)

        subscribe("player_jump", self.play_sound_fn("jump (1).wav"))
        subscribe("player_dash", self.play_sound_fn("jump.wav"))
        subscribe("player_dash", self.dash_particles)
        subscribe("player_grounded", self.play_sound_fn("hitHurt.wav"))
        subscribe("projectile_explosion", self.play_sound_fn("explosion.wav"))
        subscribe("projectile_explosion", self.explosion_particles)

    def generate_background(self, chance):
        background = pg.Surface(self.surf.get_size(), pg.SRCALPHA)
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if random.random() < chance:
                    pg.draw.rect(background, (255, 255, 255), (x, y, 1, 1))
        return background

    def explosion_particles(self, projectile):
        pos = projectile.pos
        self.pm.add(
            [
                Particle(
                    1 + random.uniform(-0.3, 0.5),
                    pos+ pg.Vector2(random.uniform(0, 0.1), random.uniform(0, 0.1)), #the particle freaks out if i dont add the random ints here
                    pg.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * 3 * random.uniform(0, 1) - pg.Vector2(0, 3),
                    5 + random.randint(-2, 2),
                    [hexstr2tuple("#68386c"), hexstr2tuple("#b55088"), hexstr2tuple("#f6757a")][random.randint(0, 2)],
                    self.gravity / 1.5
                )
                for i in range(40)
            ]
        )

    def dash_particles(self, data):
        game_object = data["game_object"]
        vec = data["vec"]
        vec = (
            pg.Vector2(-game_object.vel.x - vec.x, -game_object.vel.y / 2).normalize()
            * 5
        )
        self.pm.add(
            [
                Particle(
                    0.5 + random.uniform(-0.2, 0.2),
                    game_object.pos
                    + pg.Vector2(random.uniform(-0.1, 0.1), random.uniform(-0.2, 0.2)),
                    (vec + pg.Vector2(0, i / 8 - 2)).normalize() * 10
                    + pg.Vector2(
                        random.uniform(-1, 1), random.uniform(-1, 1)
                    ).normalize()
                    * 2,
                    6,
                    (255, 255, 255),
                )
                for i in range(40)
            ]
        )

    def get_sound(self, name: str):
        if not name in self.sounds:
            self.sounds[name] = pg.mixer.Sound("sounds/" + name)
            self.sounds[name].set_volume(0.5)
        return self.sounds[name]

    def play_sound_fn(self, name: str):
        def fn(*args):
            self.get_sound(name).play()

        return fn

    def draw(self):
        self.camera.xy = self.player.pos - pg.Vector2(WIDTH, HEIGHT) / (2 * TILE_SIZE)
        self.cam_light.pos = self.player.pos
        self.surf.fill("#10121E")

        for pos in [
            pg.Vector2(0, 0),
            pg.Vector2(0, HEIGHT),
            pg.Vector2(WIDTH, 0),
            pg.Vector2(WIDTH, HEIGHT),
        ]:
            self.surf.blit(
                self.background,
                (-self.camera * TILE_SIZE * 0.4).elementwise()
                % pg.Vector2(WIDTH, HEIGHT)
                - pos,
            )
            self.surf.blit(
                self.background2,
                (-self.camera * TILE_SIZE * 0.5).elementwise()
                % pg.Vector2(WIDTH, HEIGHT)
                - pos,
            )
            self.surf.blit(
                self.background3,
                (-self.camera * TILE_SIZE * 0.6).elementwise()
                % pg.Vector2(WIDTH, HEIGHT)
                - pos,
            )

        self.tilemap.draw(self.surf, -self.camera)
        self.rs.update(self)
        self.pm.draw(self)
        self.lm.draw(self)

    def get_mouse_tile_pos(self):
        mouse_pos = pg.Vector2(pg.mouse.get_pos()) / TILE_SIZE
        return (mouse_pos + self.camera) // 1

    def draw_image(self, pos: Coordinate, image: pg.Surface):
        self.surf.blit(image, (pos - self.camera) * TILE_SIZE)

    def update(self, dt: float):
        self.dt = dt
        self.cs.update()
        self.ps.update(self)
        self.ins.update(self)
        self.tilemap.update(self)

        self.pm.update(self)
        for i in self.layer0:
            i.update(self)
        self.projectiles = [
            projectile for projectile in self.projectiles if projectile.update(self)
        ]
        self.draw()
