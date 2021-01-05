from globals import *
from .player import Player
from .item import Item


class Environment:
    def __init__(self, universe):
        self.universe = universe
        self.celestial_body = None
        self.ground_y = 100
        self.player = None
        self.items = []

    def enter_celestial(self, celestial):
        self.celestial_body = celestial
        self.player = Player(self.universe, self)

    def leave_celestial(self):
        self.celestial_body = None
        self.player = None

    def draw(self):
        self.draw_background()
        self.draw_ground()
        self.draw_items()
        self.player.draw()

    def draw_items(self):
        for item in self.items:
            item.draw()

    def draw_background(self):
        self.universe.screen.fill(BLACK)

    def draw_ground(self):
        ground_on_screen = self.universe.camera.calculate_pos_on_screen((0, 100))[1]
        if ground_on_screen >= SCREEN_H:
            return

        ground_draw_height = SCREEN_H - ground_on_screen
        surf = pg.Surface((SCREEN_W, ground_draw_height))
        surf.fill(self.celestial_body.color)
        self.universe.screen.blit(surf, (0, ground_on_screen))

    def tick(self, dt):
        if self.celestial_body:
            for item in self.items:
                item.tick(dt)
            self.player.tick(dt)

    def add_item(self, abs_pos):
        self.items.append(Item(self.universe, self, abs_pos, self.celestial_body.color))
