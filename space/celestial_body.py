import math

from globals import *
from .trace_point import TracePoint


class CelestialBody:
    def __init__(self, universe, host, dist, radius, angle=None, radial_vel=None, color=None, name=None):
        # if not isinstance(host, CelestialBody) and type(self) != Star:
        #     raise Exception(
        #         f"Invalid host {type(host)} given for {type(self)}")

        if not radius:
            raise Exception(f"Caused a black hole")

        self.universe = universe
        self.host = host
        self.dist = dist
        self.radius = radius

        if angle is None:
            angle = 2 * math.pi * random.random()
        self.angle = angle  # angle relative to host

        if radial_vel is None:
            radial_vel = 2 * math.pi * random.uniform(0.1, 1)
        self.radial_vel = radial_vel

        if color is None:
            color = get_random_color()
        self.color = color

        self.uuid = self.universe.get_new_uuid()
        # todo impl function to validate name
        self.name = name or type(self).__name__ + "#" + str(self.uuid)

        self.age = 0
        self.gravity = 20
        self.guests = []
        self.trace_points = []  # from oldest to newest
        self.trace_point_frequency = min(MAX_TRACE_POINTS, MAX_FPS)  # if tpf >> FPS, memory leak!
        self.time_since_trace_point = 0
        self.universe.celestial_bodies.append(self)

    def __str__(self):
        return self.name

    def tick(self, dt):
        self.age += dt
        self.update_angle(dt)

        for point in self.trace_points:
            point.tick(dt)
            if point.age >= point.max_age:
                self.trace_points.remove(point)

        self.time_since_trace_point += dt
        if self.time_since_trace_point >= (1 / self.trace_point_frequency):  # todo optimize
            self.create_trace_point()
            self.time_since_trace_point = 0

    def draw(self):
        on_screen_x, on_screen_y = self.universe.camera.calculate_pos_on_screen(self.get_abs_center())
        if on_screen_x > SCREEN_W or on_screen_x < 0 or \
                on_screen_y > SCREEN_H or on_screen_y < 0:
            return  # todo fix cutoffs if obj is partially on screen

        self.draw_trace_points()
        self.draw_circle()

    def update_angle(self, dt):
        self.angle += self.radial_vel * dt
        self.angle %= 2 * math.pi

    def create_trace_point(self):
        self.trace_points.append(TracePoint(self.universe, self))
        # print(f"{self} created trace point, total {len(self.trace_points)}")

    def draw_guest_orbits(self):
        for guest in self.guests:
            dist = guest.dist
            pg.draw.circle(self.universe.screen, WHITE, self.get_center_on_screen(), round(dist), 1)

    # todo gfx bug: tp doesnt show when rel x or y is highest/lowest
    def draw_trace_points(self):
        trace_points_reversed = self.trace_points.copy()
        trace_points_reversed.reverse()
        for i, point in enumerate(trace_points_reversed):  # order = newest to oldest
            if i == 0:
                point.draw_to(self.get_abs_center())

            next_index = i + 1
            if next_index == len(trace_points_reversed):
                break

            point.draw_to(trace_points_reversed[next_index].abs_pos)

    def draw_circle(self):
        r = round(self.radius)
        pg.draw.circle(self.universe.screen, self.color, self.get_center_on_screen(), r)

    def draw_label(self):
        label = self.universe.font.render(str(self), True, WHITE, BLACK)
        self.universe.screen.blit(label, self.get_center_on_screen())

    def is_hovered(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        screen_center_x, screen_center_y = self.get_center_on_screen()

        return math.hypot(mouse_x - screen_center_x, mouse_y - screen_center_y) <= self.radius

    def set_name(self, name):
        name = name.strip()
        if not name:
            print("Invalid name")
            return

        self.name = name
        print(f"Set name of {self} to {self.name}")

    def get_rel_center(self):
        return self.dist * math.cos(self.angle), self.dist * math.sin(self.angle)

    def get_abs_center_float(self):
        host_abs_center_x, host_abs_center_y = self.host.get_abs_center_float()
        rel_center_x, rel_center_y = self.get_rel_center()
        return host_abs_center_x + rel_center_x, host_abs_center_y + rel_center_y

    def get_abs_center(self):
        center_float_x, center_float_y = self.get_abs_center_float()
        return round(center_float_x), round(center_float_y)

    def get_center_on_screen(self):
        camera_center = self.universe.camera.center_pos
        abs_center = self.get_abs_center_float()
        center_on_screen = round(abs_center[0] - camera_center[0] + SCREEN_CENTER[0]), \
            round(abs_center[1] - camera_center[1] + SCREEN_CENTER[1])

        return center_on_screen

    def get_guests(self, recursive=False):
        guests = self.guests.copy()
        if recursive:
            for guest in self.guests:
                guests.extend(guest.get_guests(recursive=True))

        return guests
