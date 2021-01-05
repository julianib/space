from globals import *
from camera import Camera
from console import Console
from environment.environment import Environment
from render.render import Render
from space.star import Star


class Universe:
    def __init__(self, screen):
        print("Universe init...")
        self.age = 0
        self.age_real_time = 0
        self.celestial_bodies = []
        self.n_ticks = 0
        self.paused = False
        self.time_factor = DEFAULT_TIME_FACTOR
        self.next_uuid = 1

        self.camera = Camera(self)
        self.console = Console(self)
        self.environment = Environment(self)
        self.font = pg.font.SysFont("Comic Sans MS", 20)
        self.render = Render(self)
        self.screen = screen

        self.reset()
        print("Universe init")

    def reset(self):
        print("Resetting universe")
        self.celestial_bodies.clear()
        self.add_star()

    def add_star(self, n_planets=3):
        star = Star(self, abs_center=(len(self.get_stars()) * STAR_DISTANCE, 0),
                    n_planets=n_planets)
        return star

    def get_stars(self):
        return [celestial for celestial in self.celestial_bodies
                if type(celestial) == Star]

    def tick(self, dt):
        dt_adjusted = dt * self.time_factor
        self.n_ticks += 1
        self.age_real_time += dt
        self.age += dt_adjusted

        for celestial in self.celestial_bodies:
            celestial.tick(dt_adjusted)

        self.environment.tick(dt_adjusted)

    def draw(self):  # todo check: cel.draw() for cel in self.cel_bodies ???
        for star in self.get_stars():
            star.draw()
            for guest in star.get_guests(recursive=True):
                guest.draw()

    def set_time_factor(self, new_time):
        try:
            new_time = float(new_time)
        except ValueError as ex:
            print(f"{ex}: {new_time}")
            return

        self.time_factor = new_time

    def create_from_template(self):
        print(self, "todo")  # todo implement loading from template (json or w/e)

    def get_hovered_object(self):
        for celestial in self.celestial_bodies:
            if celestial.is_hovered():
                return celestial  # todo its possible to hover over 2+ celestial bodies, implement

    def get_new_uuid(self):
        old = self.next_uuid
        self.next_uuid += 1
        return old
