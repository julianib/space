import math

from globals import *
from background_star import BackgroundStar


class Render:
    def __init__(self, universe):
        self.universe = universe
        self.last_dt = 1
        self.background_stars = []
        self.reset_background_stars()

    def draw_background(self):
        self.universe.screen.fill(BACKGROUND_COLOR)
        for background_star in self.background_stars:
            background_star.tick()  # todo move to seperate thread
            background_star.draw()

    def draw_debug(self):
        if not SHOW_DEBUG:
            return

        n_trace_points = 0
        for celestial in self.universe.celestial_bodies:
            n_trace_points += len(celestial.trace_points)

        fps = round(1 / self.last_dt)

        lines = [
            f"FPS: {fps} ({round(self.last_dt, 3)}s/t)",

            f"Time factor: {round(self.universe.time_factor, 2)}x",
            f"Age: {round(self.universe.age, 1)}s "
            f"(real: {round(self.universe.age_real_time, 1)}s, "

            f"{self.universe.n_ticks} ticks)",
            f"Cam x,y: {self.universe.camera.center_pos}",
            f"Zoom: {self.universe.camera.zoom_factor}x",
            f"Stars: {len(self.universe.get_stars())}",
            f"Cel bodies: {len(self.universe.celestial_bodies)}",
            f"Trace points: {n_trace_points}"
        ]

        if self.universe.environment.celestial_body:
            celestial = self.universe.environment.celestial_body
            lines.extend([
                "",
                f"Cel body: {celestial}",
                f"x,y: {self.universe.environment.player.abs_pos}",
                f"y_vel: {self.universe.environment.player.y_vel}",
                f"on_ground: {self.universe.environment.player.on_ground}",
                f"Items: {len(self.universe.environment.items)}"
            ])

        elif self.universe.camera.locked_celestial:
            locked_celestial = self.universe.camera.locked_celestial
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

        self.universe.screen.blits([(self.universe.font.render(lines[i], True, WHITE),
                                     (0, i * 20)) for i in range(len(lines))])

    def draw_hover_label(self):
        hovered_celestial = self.universe.get_hovered_object()
        if hovered_celestial:
            label = str(hovered_celestial)

            self.universe.screen.blit(self.universe.font.render(label, True, WHITE, BLACK), pg.mouse.get_pos())

    def draw_screen(self):
        if self.universe.environment.celestial_body:
            self.universe.environment.draw()

        else:
            self.draw_background()
            self.draw_locked_celestial_body_lines()
            self.universe.draw()  # todo don't draw things off that are off screen (performance)
            self.draw_orbits()
            self.draw_hover_label()

        self.draw_debug()
        self.universe.console.draw()
        self.draw_paused_screen()

        pg.display.update()

    def draw_orbits(self):
        if SHOW_GUEST_ORBITS:
            for celestial in self.universe.celestial_bodies:
                celestial.draw_guest_orbits()

    def draw_locked_celestial_body_lines(self):
        locked_celestial = self.universe.camera.locked_celestial

        if not locked_celestial:
            return

        for guest in locked_celestial.guests:
            pg.draw.line(self.universe.screen, GREEN, SCREEN_CENTER,
                         guest.get_center_on_screen())

        host = locked_celestial.host
        if host:
            pg.draw.line(self.universe.screen, AQUA, SCREEN_CENTER,
                         host.get_center_on_screen())

    def reset_background_stars(self):
        for i in range(N_BACKGROUND_STARS):
            self.background_stars.append(BackgroundStar(self.universe))

    def draw_paused_screen(self):
        if not self.universe.paused:
            return

        surf = self.universe.font.render("PAUSED", True, WHITE, BLACK)
        rect: pg.Rect = surf.get_rect()
        self.universe.screen.blit(
            surf, (SCREEN_CENTER[0] - rect.center[0], SCREEN_CENTER[1] - rect.center[1]))
