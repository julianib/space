import math

from globals import *


class TracePoint:
    max_age = 1
    line_width = 1

    def __init__(self, universe, host):
        self.universe = universe
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
        self.universe.screen.blit(surf, self.universe.camera.calculate_pos_on_screen(
            surf_top_left_abs))
