from globals import *


class BackgroundStar:
    def __init__(self, universe):
        self.universe = universe

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
        self.universe.screen.blit(img, self.screen_pos)
