from globals import *
from .player import Player
from .item import Item


class Environment:
    def __init__(self, universe):
        self.universe = universe
        self.celestial_body = None
        self.ground_y = 100
        self.player = None
        self.entities = []

    def enter_celestial(self, celestial):
        self.celestial_body = celestial
        self.player = Player(self.universe, self)

    def leave_celestial(self):
        self.celestial_body = None
        self.player = None

    def draw(self):
        self.draw_sky()
        self.draw_ground()
        self.draw_entities()

    def draw_sky(self):
        print(self, "implement")  # todo implement

    def draw_entities(self):
        for entity in self.entities:
            entity.draw()

    def draw_ground(self):
        ground_on_screen = self.universe.camera.calculate_pos_on_screen((0, 100))[1]
        if ground_on_screen >= SCREEN_HEIGHT:
            return

        ground_draw_height = SCREEN_HEIGHT - ground_on_screen
        surf = pg.Surface((SCREEN_WIDTH, ground_draw_height))
        surf.fill(self.celestial_body.color)
        self.universe.screen.blit(surf, (0, ground_on_screen))

    def tick(self, dt):
        if self.celestial_body:
            for item in self.entities:
                item.tick(dt)
            self.player.tick(dt)

    def add_item(self, abs_pos):
        self.entities.append(Item(self.universe, self, abs_pos, self.celestial_body.color))
