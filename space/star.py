from globals import *

from .celestial_body import CelestialBody
from .planet import Planet


class Star(CelestialBody):
    def __init__(self, universe, abs_center, radius=0, n_planets=0):
        print("Star init...")

        if not radius:
            radius = get_random_radius(
                RADIUS_SUN, STAR_RADIUS_VARIANCE)

        self.abs_center = abs_center
        super().__init__(universe, None, None, radius, color=STAR_COLOR)

        self.generate_planets(n_planets)

        print(f"{self} @ {self.get_abs_center()} init, n_planets={n_planets}")

    def tick(self, dt):
        pass

    def draw(self):
        self.draw_circle()

    def get_abs_center_float(self):
        return self.abs_center

    def generate_planets(self, n):
        for i in range(n):
            self.add_planet()

    def add_planet(self, dist=0, radius=0):
        self.guests.append(Planet(self.universe, self, dist, radius))
