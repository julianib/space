import math

from globals import *
from .celestial_body import CelestialBody


class Moon(CelestialBody):
    def __init__(self, universe, host, dist):
        print("Moon init...")
        super().__init__(universe, host, dist, RADIUS_MOON, radial_vel=2 * math.pi * random.uniform(0.5, 4),
                         color=MOON_COLOR)

        print(f"{self} @ {self.get_abs_center()} init, host={self.host}")
