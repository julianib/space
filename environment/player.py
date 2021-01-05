from globals import *
from .entity import Entity


class Player(Entity):
    def __init__(self, universe, environment):
        super().__init__(universe, environment, (0, 0), AQUA)
        self.jump_vel = 400
        self.movement_speed = 10
        self.img = IMG_PLAYER

    def tick(self, dt):
        self.y_vel += self.environment.celestial_body.gravity
        self.abs_pos = self.abs_pos[0], self.abs_pos[1] + self.y_vel * dt
        if self.abs_pos[1] + self.h / 2 >= self.environment.ground_y:
            self.on_ground = True
            self.abs_pos = self.abs_pos[0], self.environment.ground_y - self.h / 2
            self.y_vel = 0

        else:
            self.on_ground = False

    def draw(self):
        abs_pos_offsetted = self.abs_pos[0] - \
            self.w / 2, self.abs_pos[1] - self.h / 2
        self.universe.screen.blit(self.img,
                                  self.universe.camera.calculate_pos_on_screen(
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
        self.environment.add_item(self.abs_pos)
