from globals import *


class Camera:
    def __init__(self, universe):
        self.universe = universe
        self.zoom_factor = 1
        self.center_pos = 0, 0
        self.locked_celestial = None

    def set_center(self, new_center):
        self.center_pos = new_center

    def move_center(self, add_x, add_y):
        if not (add_x or add_y):
            return

        self.clear_locked_celestial()
        old = self.center_pos
        self.set_center((old[0] + int(add_x) * CAMERA_MOVEMENT_STEP,
                         old[1] + int(add_y) * CAMERA_MOVEMENT_STEP))

    def set_locked_celestial(self, celestial_body):
        self.locked_celestial = celestial_body

    def clear_locked_celestial(self):
        self.locked_celestial = None

    def snap_to_locked_celestial(self):
        if self.locked_celestial is not None:
            self.set_center(self.locked_celestial.get_abs_center())

    def snap_to_player(self):
        if self.universe.environment.celestial_body:
            self.set_center(self.universe.environment.player.abs_pos)

    def calculate_pos_on_screen(self, abs_pos):
        camera_center = self.center_pos
        pos_on_screen = round(abs_pos[0] - camera_center[0] + SCREEN_CENTER[0]), \
            round(abs_pos[1] - camera_center[1] + SCREEN_CENTER[1])

        return pos_on_screen
