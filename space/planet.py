from globals import *
from .celestial_body import CelestialBody
from .moon import Moon


class Planet(CelestialBody):
    def __init__(self, universe, host, dist=0, radius=0):
        print("Planet init...")

        if not dist:
            dist = get_random_dist(host, DISTANCE_EARTH, PLANET_DISTANCE_VARIANCE)

        if not radius:
            radius = get_random_radius(RADIUS_EARTH, PLANET_RADIUS_VARIANCE)

        super().__init__(universe, host, dist, radius)

        self.create_moons()

        print(f"{self} @ {self.get_abs_center()} init, host={self.host}")

    def create_moons(self, n=0):
        if not n:
            rand = random.random()
            if rand > 0.95:
                n = 4
            elif rand > 0.9:
                n = 3
            elif rand > 0.75:
                n = 2
            elif rand > 0.5:
                n = 1
            else:
                n = 0

        for i in range(n):
            self.add_moon()

    def add_moon(self):
        dist = get_random_dist(self, self.radius * 2 + DISTANCE_MOON * len(self.guests), 0)
        self.guests.append(Moon(self.universe, self, dist))
