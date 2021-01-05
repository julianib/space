from globals import *


class Entity:
    def __init__(self, universe, environment, abs_pos, color):
        self.universe = universe
        self.environment = environment
        self.abs_pos = abs_pos
        self.color = color

        self.y_vel = 0
        self.on_ground = False
        self.w, self.h = 20, 20
        self.surf = pg.Surface((self.w, self.h))
        self.surf.fill(self.color)
        self.rect: pg.Rect = self.surf.get_rect()

    def draw(self):
        abs_pos_offsetted = self.abs_pos[0] - self.w / 2, \
                            self.abs_pos[1] - self.h / 2
        self.universe.screen.blit(self.surf,
                                  self.universe.camera.calculate_pos_on_screen(
                                      abs_pos_offsetted))

    def tick(self, dt):
        self.y_vel += self.environment.celestial_body.gravity
        self.abs_pos = self.abs_pos[0], self.abs_pos[1] + self.y_vel * dt
        if self.abs_pos[1] + self.h / 2 >= self.environment.ground_y:
            self.on_ground = True
            self.abs_pos = self.abs_pos[0], self.environment.ground_y - self.h / 2
            self.y_vel = 0

        else:
            self.on_ground = False

        self.check_collisions()

    def check_collisions(self):  # todo broken asf
        for item in self.environment.items:
            if self.abs_pos[0] <= item.abs_pos[0] + 10:
                self.abs_pos = item.abs_pos[0] + 30, self.abs_pos[1]
            elif self.abs_pos[0] + 10 >= item.abs_pos[0]:
                self.abs_pos = item.abs_pos[0] - 20, self.abs_pos[1]
