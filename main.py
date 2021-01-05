import os
import math
import pygame as pg
import random


# settings
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
ASSETS_FOLDER = "assets"


# pygame init
# todo pg display flags https://stackoverflow.com/questions/29135147/what-do-hwsurface-and-doublebuf-do
pg.display.set_caption("Space Sim")
SCREEN: pg.Surface = pg.display.set_mode((SCREEN_W, SCREEN_H))
SCREEN_CENTER = round(SCREEN_W / 2), round(SCREEN_H / 2)
pg.font.init()
FONT = pg.font.SysFont("Comic Sans MS", 20)
COLOR_WHITE = 255, 255, 255
COLOR_YELLOW = 255, 255, 0
COLOR_BLACK = 0, 0, 0
COLOR_GRAY = 127, 127, 127
COLOR_GREEN = 0, 255, 0
COLOR_AQUA = 0, 255, 255
COLOR_BACKGROUND = 6, 6, 20
IMGS_BACKGROUND_STAR = [pg.image.load(os.path.join(ASSETS_FOLDER, f"bg_star_{i}.png"))
                        for i in range(7)]
IMG_PLAYER = pg.image.load(os.path.join(ASSETS_FOLDER, "astronaut.png"))
print("Pygame init")


# space constants
MASS_EARTH = 1 or 5.972e24
RADIUS_EARTH = 20 or 6.371e3
MASS_SUN = 1 or 1.989e30
RADIUS_SUN = 20 or 6.963e5
DISTANCE_EARTH = 100  # 1.495e8
DISTANCE_MOON = 20  # 8.844e5
RADIUS_MOON = 5  # 1.737e3
# todo randomize orbital distances between planets
DISTANCE_STEPS = DISTANCE_EARTH * 0.5
STAR_DISTANCE = 2000
STAR_COLOR = 255, 255, 0
MOON_COLOR = COLOR_GRAY


class CelestialBody:
    next_uuid = 1

    def __init__(self, host, dist, radius, angle=0, radial_vel=None,
                 color=None, name=None):
        self.uuid = CelestialBody.get_new_uuid()

        if not isinstance(host, CelestialBody) and type(self) != Star:
            raise Exception(
                f"Invalid host {type(host)} given for {type(self)}")

        if not radius:
            raise Exception(f"Caused a black hole")

        self.host = host
        self.dist = dist
        self.radius = radius

        if angle is None:
            angle = 2 * math.pi * random.random()
        self.angle = angle  # angle relative to host

        if radial_vel is None:
            radial_vel = 2 * math.pi * random.uniform(0.1, 1)
        self.radial_vel = radial_vel  # units per second

        if color is None:
            color = CelestialBody.get_random_color()
        self.color = color

        # todo impl function to validate name
        self.name = name or type(self).__name__ + "#" + str(self.uuid)

        self.age = 0
        self.gravity = 20
        self.guests = []
        self.trace_points = []  # from oldest to newest
        # if frequency >> FPS, memory leak
        self.trace_point_frequency = min(60, FPS)
        self.time_since_trace_point = 0
        Universe.celestial_bodies.append(self)

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
        if self.time_since_trace_point >= (1 / self.trace_point_frequency):
            self.create_trace_point()
            self.time_since_trace_point = 0

    def draw(self):
        self.draw_trace_points()
        self.draw_circle()

    def update_angle(self, dt):
        self.angle += self.radial_vel * dt
        self.angle %= 2 * math.pi

    def create_trace_point(self):
        self.trace_points.append(TracePoint(self))
        # print(f"{self} created trace point, total {len(self.trace_points)}")

    def draw_guest_orbits(self):
        for guest in self.guests:
            dist = guest.dist
            pg.draw.circle(SCREEN, COLOR_WHITE,
                           self.get_center_on_screen(), round(dist), 1)

    # todo gfx bug: doesnt show when rel x or y is highest/lowest
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
        pg.draw.circle(SCREEN, self.color, self.get_center_on_screen(), r)

    def draw_label(self):
        label = FONT.render(str(self), True, COLOR_WHITE, COLOR_BLACK)
        SCREEN.blit(label, self.get_center_on_screen())

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
        camera_center = Camera.center_pos
        abs_center = self.get_abs_center_float()
        screen_center = round(abs_center[0] - camera_center[0] + SCREEN_CENTER[0]), \
            round(abs_center[1] - camera_center[1] + SCREEN_CENTER[1])

        return screen_center

    def get_guests(self, recursive=False):
        guests = self.guests.copy()
        if recursive:
            for guest in self.guests:
                guests.extend(guest.get_guests(recursive=True))

        return guests

    @staticmethod
    def get_random_dist(host, base, variance):
        return random.uniform(base * (len(host.guests) - variance + 1),
                              base * (len(host.guests) + variance + 1))

    @staticmethod
    def get_random_radius(base, variance):
        return random.uniform(base * (1 - variance), base * (1 + variance))

    @staticmethod
    def get_random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    @staticmethod
    def get_new_uuid():
        old = CelestialBody.next_uuid
        CelestialBody.next_uuid += 1
        return old


class Moon(CelestialBody):
    def __init__(self, host, dist):
        print("Moon init...")
        super().__init__(host, dist, RADIUS_MOON, radial_vel=2 * math.pi * random.uniform(0.5, 4),
                         color=MOON_COLOR)

        print(f"{self} @ {self.get_abs_center()} init, host={self.host}")


class Planet(CelestialBody):
    DISTANCE_VARIANCE = 0.2
    RADIUS_VARIANCE = 0.95

    def __init__(self, host, dist=0, radius=0):
        print("Planet init...")

        if not dist:
            dist = CelestialBody.get_random_dist(
                host, DISTANCE_EARTH, self.DISTANCE_VARIANCE)

        if not radius:
            radius = CelestialBody.get_random_radius(
                RADIUS_EARTH, self.RADIUS_VARIANCE)

        super().__init__(host, dist, radius)

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
        dist = CelestialBody.get_random_dist(
            self, self.radius * 2 + DISTANCE_MOON * len(self.guests), 0)
        self.guests.append(Moon(self, dist))


class Star(CelestialBody):
    RADIUS_VARIANCE = 0.5

    def __init__(self, abs_center, radius=0, n_planets=0):
        print("Star init...")

        if not radius:
            radius = CelestialBody.get_random_radius(
                RADIUS_SUN, self.RADIUS_VARIANCE)

        self.abs_center = abs_center
        super().__init__(None, None, radius, color=STAR_COLOR)

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
        self.guests.append(Planet(self, dist, radius))


class Universe:
    celestial_bodies = []
    time_factor = 0.1
    time_factor_step = 0.01
    time_factor_max = 5
    time_factor_min = time_factor_step
    paused = False
    age_adjusted = 0
    age = 0
    n_ticks = 0

    @staticmethod
    def reset():
        print("Resetting universe")
        Universe.celestial_bodies.clear()
        Universe.add_star()

    @staticmethod
    def add_star(n_planets=3):
        star = Star(abs_center=(len(Universe.get_stars()) *
                                STAR_DISTANCE, 0), n_planets=n_planets)
        return star

    @staticmethod
    def get_stars():
        return [celestial_body for celestial_body in Universe.celestial_bodies
                if type(celestial_body) == Star]

    @staticmethod
    def tick(dt):
        dt_adjusted = dt * Universe.time_factor
        Universe.n_ticks += 1
        Universe.age += dt
        Universe.age_adjusted += dt_adjusted

        for celestial in Universe.celestial_bodies:
            celestial.tick(dt_adjusted)

        Environment.tick(dt_adjusted)

    @staticmethod
    def draw():
        for star in Universe.get_stars():
            star.draw()
            for guest in star.get_guests(recursive=True):
                guest.draw()

    @staticmethod
    def set_time_factor(new_time):
        try:
            new_time = float(new_time)
        except ValueError as ex:
            print(f"{ex}: {new_time}")
            return

        Universe.time_factor = new_time

    @staticmethod
    def from_template():
        print("todo")  # todo implement loading from template (json or w/e)

    @staticmethod
    def get_hovered_object():
        for celestial in Universe.celestial_bodies:
            if celestial.is_hovered():
                return celestial  # todo possible to hover over 2+ celestial bodies


class TracePoint:
    max_age = 1
    line_width = 1

    def __init__(self, host):
        self.host = host
        self.abs_pos = host.get_abs_center()
        self.color = host.color
        self.age = 0

    def tick(self, dt):
        self.age += dt

    def draw_to(self, to_abs):
        from_abs = self.abs_pos
        surf_top_left_abs = min(from_abs[0], to_abs[0]), min(
            from_abs[1], to_abs[1])
        surf_width, surf_height = abs(
            from_abs[0] - to_abs[0]) + 1, abs(from_abs[1] - to_abs[1]) + 1
        start_from_top_left = from_abs[0] - \
            surf_top_left_abs[0], from_abs[1] - surf_top_left_abs[1]
        end_from_top_left = to_abs[0] - \
            surf_top_left_abs[0], to_abs[1] - surf_top_left_abs[1]

        r, g, b = self.color
        color_with_alpha = r, g, b, round(
            math.floor((1 - (self.age / self.max_age)) * 255))

        surf = pg.Surface((surf_width, surf_height), pg.SRCALPHA)
        pg.draw.line(surf, color_with_alpha,
                     start_from_top_left, end_from_top_left, TracePoint.line_width)
        SCREEN.blit(surf, Camera.calculate_pos_on_screen(surf_top_left_abs))


class BackgroundStar:
    def __init__(self):
        self.frame = random.randint(0, 6)
        self.default_ticks = random.randint(5, 15)
        self.n_ticks = random.randint(0, self.default_ticks)
        self.screen_pos = 0, 0  # todo disgusting
        self.set_random_position()
        self.alpha = random.randint(0, 255)

    def tick(self):
        if self.n_ticks == 0:
            self.increment_frame()
            self.n_ticks = self.default_ticks
        self.n_ticks -= 1

    def increment_frame(self):
        self.frame += 1
        if self.frame == 7:
            self.frame = 0
            self.set_random_position()

    def set_random_position(self):
        self.screen_pos = random.randint(
            0, SCREEN_W - 64), random.randint(0, SCREEN_H - 64)

    def draw(self):
        img: pg.Surface = IMGS_BACKGROUND_STAR[self.frame].copy()
        # https://stackoverflow.com/a/16177852
        img.fill((255, 255, 255, self.alpha), None, pg.BLEND_RGBA_MULT)
        SCREEN.blit(img, self.screen_pos)


class Console:
    leading_text = "Type Here: "
    input_text = ""
    active = False
    text_color = COLOR_WHITE
    position = (40, 200)

    @staticmethod
    def process():
        text = Console.input_text.strip().lower()
        text_split = text.split()
        print(f"Processing input \"{text}\"")

        if len(text_split) == 0:
            return

        if text_split[0] == "time":
            Universe.set_time_factor(text_split[1])
            return

        for celestial in Universe.celestial_bodies:
            if str(celestial.uuid).lower() == text or \
                    str(celestial).lower() == text:
                carrier_type = type(celestial)
                print(carrier_type)
                Camera.set_locked_celestial(celestial)
                return

        if len(text_split) == 1:
            return

        if text_split[0] == "name":
            locked_celestial = Camera.locked_celestial
            if not locked_celestial:
                print("No locked celestial")
                return

            locked_celestial.set_name(" ".join(text_split[1:]))

    @staticmethod
    def add_text(s):
        Console.input_text += s

    @staticmethod
    def clear_text():
        Console.input_text = ""

    @staticmethod
    def remove_last_character():
        Console.input_text = Console.input_text[:-1]

    @staticmethod
    def toggle():
        if Console.active:
            Console.process()
            Console.clear_text()

        Console.active = not Console.active

    @staticmethod
    def draw():
        if not Console.active:
            return

        surf = FONT.render(Console.leading_text +
                           Console.input_text, True, Console.text_color)
        SCREEN.blit(surf, Console.position)


class EnvironmentEntity:
    def __init__(self, abs_pos, color):
        self.color = color
        self.abs_pos = abs_pos
        self.y_vel = 0
        self.on_ground = False
        self.w, self.h = 20, 20
        self.surf = pg.Surface((self.w, self.h))
        self.surf.fill(self.color)
        self.rect: pg.Rect = self.surf.get_rect()

    def draw(self):
        abs_pos_offsetted = self.abs_pos[0] - \
            self.w / 2, self.abs_pos[1] - self.h / 2
        SCREEN.blit(self.surf, Camera.calculate_pos_on_screen(
            abs_pos_offsetted))

    def tick(self, dt):
        self.y_vel += Environment.planet.gravity
        self.abs_pos = self.abs_pos[0], self.abs_pos[1] + self.y_vel * dt
        if self.abs_pos[1] + self.h / 2 >= Environment.ground_y:
            self.on_ground = True
            self.abs_pos = self.abs_pos[0], Environment.ground_y - self.h / 2
            self.y_vel = 0

        else:
            self.on_ground = False

        self.check_collisions()

    def check_collisions(self):  # todo broken asf
        for item in Environment.items:
            if self.abs_pos[0] <= item.abs_pos[0] + 10:
                self.abs_pos = item.abs_pos[0] + 30, self.abs_pos[1]
            elif self.abs_pos[0] + 10 >= item.abs_pos[0]:
                self.abs_pos = item.abs_pos[0] - 20, self.abs_pos[1]


class Item(EnvironmentEntity):
    def __init__(self, abs_pos, color):
        super().__init__(abs_pos, color)


class Player(EnvironmentEntity):
    def __init__(self):
        super().__init__((0, 0), COLOR_AQUA)
        self.jump_vel = 400
        self.movement_speed = 10
        self.img = IMG_PLAYER

    def tick(self, dt):
        self.y_vel += Environment.planet.gravity
        self.abs_pos = self.abs_pos[0], self.abs_pos[1] + self.y_vel * dt
        if self.abs_pos[1] + self.h / 2 >= Environment.ground_y:
            self.on_ground = True
            self.abs_pos = self.abs_pos[0], Environment.ground_y - self.h / 2
            self.y_vel = 0

        else:
            self.on_ground = False

    def draw(self):
        abs_pos_offsetted = self.abs_pos[0] - \
            self.w / 2, self.abs_pos[1] - self.h / 2
        SCREEN.blit(self.img, Camera.calculate_pos_on_screen(
            abs_pos_offsetted))

    def move(self, add_x):
        if not add_x:
            return

        old = self.abs_pos
        self.abs_pos = old[0] + int(add_x) * self.movement_speed, old[1]

    def jump(self):
        if self.on_ground:
            self.y_vel = -self.jump_vel

    def drop_item(self):
        Environment.add_item(self.abs_pos)


class Environment:
    planet: CelestialBody = None
    ground_y = 100
    player = None
    items = []

    @staticmethod
    def enter_planet(planet):
        Environment.planet = planet
        Environment.player = Player()

    @staticmethod
    def leave_planet():
        Environment.planet = None
        Environment.player = None

    @staticmethod
    def draw():
        Environment.draw_background()
        Environment.draw_ground()
        Environment.draw_items()
        Environment.player.draw()

    @staticmethod
    def draw_items():
        for item in Environment.items:
            item.draw()

    @staticmethod
    def draw_background():
        SCREEN.fill(COLOR_BLACK)

    @staticmethod
    def draw_ground():
        ground_on_screen = Camera.calculate_pos_on_screen((0, 100))[1]
        if ground_on_screen >= SCREEN_H:
            return

        ground_draw_height = SCREEN_H - ground_on_screen
        surf = pg.Surface((SCREEN_W, ground_draw_height))
        surf.fill(Environment.planet.color)
        SCREEN.blit(surf, (0, ground_on_screen))

    @staticmethod
    def tick(dt):
        if Environment.planet:
            for item in Environment.items:
                item.tick(dt)
            Environment.player.tick(dt)

    @staticmethod
    def add_item(abs_pos):
        Environment.items.append(Item(abs_pos, Environment.planet.color))


class Camera:
    zoom_factor = 1
    zoom_factor_max = 8
    zoom_factor_min = 0.5
    center_pos = 0, 0
    movement_step = 20  # todo should account for deltatime
    locked_celestial = None

    @staticmethod
    def set_center(new_center):
        Camera.center_pos = new_center

    @staticmethod
    def move_center(add_x, add_y):
        if not (add_x or add_y):
            return

        Camera.clear_locked_celestial()
        old = Camera.center_pos
        Camera.set_center((old[0] + int(add_x) * Camera.movement_step,
                           old[1] + int(add_y) * Camera.movement_step))

    @staticmethod
    def set_locked_celestial(celestial_body):
        Camera.locked_celestial = celestial_body

    @staticmethod
    def clear_locked_celestial():
        Camera.locked_celestial = None

    @staticmethod
    def snap_to_locked_celestial():
        if Camera.locked_celestial is not None:
            Camera.set_center(Camera.locked_celestial.get_abs_center())

    @staticmethod
    def snap_to_player():
        if Environment.planet:
            Camera.set_center(Environment.player.abs_pos)

    @staticmethod
    def calculate_pos_on_screen(abs_pos):
        camera_center = Camera.center_pos
        screen_pos = round(abs_pos[0] - camera_center[0] + SCREEN_CENTER[0]), \
            round(abs_pos[1] - camera_center[1] + SCREEN_CENTER[1])

        return screen_pos


class Render:
    last_dt = 1
    show_debug = True
    always_show_celestial_body_label = False
    show_orbits = False
    background_stars = []
    trace_point_duration = 1
    n_background_stars = 10

    @staticmethod
    def draw_background():
        SCREEN.fill(COLOR_BACKGROUND)
        for background_star in Render.background_stars:
            background_star.tick()  # todo move to seperate thread
            background_star.draw()

    @staticmethod
    def draw_debug():
        if not Render.show_debug:
            return

        n_trace_points = 0
        for celestial in Universe.celestial_bodies:
            n_trace_points += len(celestial.trace_points)

        fps = round(1 / Render.last_dt)

        lines = [
            f"FPS: {fps} ({round(Render.last_dt, 3)}s/t)",
            f"Time factor: {round(Universe.time_factor, 2)}x",
            f"Age: {round(Universe.age_adjusted, 1)}s (real: {round(Universe.age, 1)}s, {Universe.n_ticks} ticks)",
            f"Cam x,y: {Camera.center_pos}",
            f"Zoom: {Camera.zoom_factor}x",
            f"Stars: {len(Universe.get_stars())}",
            f"Cel bodies: {len(Universe.celestial_bodies)}",
            f"Trace points: {n_trace_points}"
        ]

        if Environment.planet:
            planet = Environment.planet
            lines.extend([
                "",
                f"Planet: {planet}",
                f"x,y: {Environment.player.abs_pos}",
                f"y_vel: {Environment.player.y_vel}",
                f"on_ground: {Environment.player.on_ground}",
                f"Items: {len(Environment.items)}"
            ])

        elif Camera.locked_celestial:
            locked_celestial = Camera.locked_celestial
            guests = [str(guest) for guest in locked_celestial.guests]
            if guests:
                guests_formatted = ", ".join(guests)
            else:
                guests_formatted = "-"

            host = locked_celestial.host
            if host:
                dist = round(locked_celestial.dist, 1)
                orbit = str(
                    round(2 * math.pi / locked_celestial.radial_vel, 1)) + "s"
                radial_vel = round(math.degrees(locked_celestial.radial_vel))
            else:
                dist = orbit = radial_vel = "-"

            lines.extend([
                "",
                str(locked_celestial),
                f"Host: {host or '-'}",
                f"Guests: {guests_formatted}",
                f"Orbit period: {orbit}",
                f"x,y: {locked_celestial.get_abs_center()}",
                f"dist: {dist}",
                f"radius: {round(locked_celestial.radius, 1)}",
                f"radial_vel: {radial_vel}°/s",
                f"angle: {round(math.degrees(locked_celestial.angle))}°"
            ])

        SCREEN.blits([(FONT.render(lines[i], True, COLOR_WHITE),
                       (0, i * 20)) for i in range(len(lines))])

    @staticmethod
    def draw_hover_label():
        hovered_celestial = Universe.get_hovered_object()
        if hovered_celestial:
            label = str(hovered_celestial)

            SCREEN.blit(FONT.render(label, True, COLOR_WHITE,
                                    COLOR_BLACK), pg.mouse.get_pos())

    @staticmethod
    def draw_screen():
        if Environment.planet:
            Environment.draw()
        else:
            Render.draw_background()
            Render.draw_locked_celestial_body_lines()
            Universe.draw()  # todo don't draw things off that are off screen (performance)
            Render.draw_orbits()
            Render.draw_hover_label()

        Render.draw_debug()
        Console.draw()
        Render.draw_paused_screen()

        pg.display.update()

    @staticmethod
    def draw_orbits():
        if Render.show_orbits:
            for celestial in Universe.celestial_bodies:
                celestial.draw_guest_orbits()

    @staticmethod
    def draw_locked_celestial_body_lines():
        locked_celestial = Camera.locked_celestial

        if not locked_celestial:
            return

        for guest in locked_celestial.guests:
            pg.draw.line(SCREEN, COLOR_GREEN, SCREEN_CENTER,
                         guest.get_center_on_screen())

        host = locked_celestial.host
        if host:
            pg.draw.line(SCREEN, COLOR_AQUA, SCREEN_CENTER,
                         host.get_center_on_screen())

    @staticmethod
    def reset_background_stars():
        for i in range(Render.n_background_stars):
            Render.background_stars.append(BackgroundStar())

    @staticmethod
    def draw_paused_screen():
        if not Universe.paused:
            return

        surf = FONT.render("PAUSED", True, COLOR_WHITE, COLOR_BLACK)
        rect: pg.Rect = surf.get_rect()
        SCREEN.blit(
            surf, (SCREEN_CENTER[0] - rect.center[0], SCREEN_CENTER[1] - rect.center[1]))


def handle_events_and_input():
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            raise InterruptedError

        elif ev.type == pg.KEYDOWN:  # ACTIVE KEY PRESSES
            if ev.key == pg.K_RETURN:
                Console.toggle()
            elif Console.active:
                if ev.key == pg.K_BACKSPACE:
                    Console.remove_last_character()

                else:
                    Console.add_text(ev.unicode)

                continue

            locked_celestial = Camera.locked_celestial
            if ev.key == pg.K_e:
                if not Environment.planet and locked_celestial:
                    Environment.enter_planet(locked_celestial)
                else:
                    Environment.leave_planet()
            elif ev.key == pg.K_f and Environment.planet:
                Environment.player.drop_item()
            elif ev.key == pg.K_F1:
                Render.show_debug = not Render.show_debug
            elif ev.key == pg.K_o:
                Render.show_orbits = not Render.show_orbits
            elif ev.key == pg.K_q:
                raise InterruptedError
            elif ev.key == pg.K_r:
                Universe.reset()
                Camera.clear_locked_celestial()
            elif ev.key == pg.K_SPACE:
                Universe.paused = not Universe.paused

        elif ev.type == pg.MOUSEBUTTONDOWN:
            if ev.button == 1:
                celestial = Universe.get_hovered_object()
                if celestial is not None:
                    Camera.set_locked_celestial(celestial)

            elif ev.button == 4 and Camera.zoom_factor <= Camera.zoom_factor_max:
                Camera.zoom_factor *= 2
            elif ev.button == 5 and Camera.zoom_factor >= Camera.zoom_factor_min:
                Camera.zoom_factor *= 0.5

    pressed_keys = pg.key.get_pressed()
    if not Console.active:  # PASSIVE KEY PRESSES
        if pressed_keys[pg.K_EQUALS] and Universe.time_factor <= Universe.time_factor_max:
            Universe.time_factor += Universe.time_factor_step
        if pressed_keys[pg.K_MINUS] and Universe.time_factor >= Universe.time_factor_min:
            Universe.time_factor -= Universe.time_factor_step

        if Environment.planet and not Universe.paused:
            Environment.player.move((pressed_keys[pg.K_RIGHT] or pressed_keys[pg.K_d]) -
                                    (pressed_keys[pg.K_LEFT] or pressed_keys[pg.K_a]))
            if pressed_keys[pg.K_w]:
                Environment.player.jump()

        else:
            Camera.move_center((pressed_keys[pg.K_RIGHT] or pressed_keys[pg.K_d]) -
                               (pressed_keys[pg.K_LEFT]
                                or pressed_keys[pg.K_a]),
                               (pressed_keys[pg.K_DOWN] or pressed_keys[pg.K_s]) -
                               (pressed_keys[pg.K_UP] or pressed_keys[pg.K_w]))


def main():
    Universe.reset()
    Render.reset_background_stars()
    clock = pg.time.Clock()

    while True:
        dt = clock.tick(FPS) / 1000.0
        if not Universe.paused:
            Render.last_dt = dt
            Universe.tick(dt)

        if Environment.planet:
            Camera.snap_to_player()
        else:
            Camera.snap_to_locked_celestial()

        Render.draw_screen()

        try:
            handle_events_and_input()
        except InterruptedError:
            print("Exiting")
            break


if __name__ == "__main__":
    main()
