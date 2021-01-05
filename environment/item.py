from .entity import Entity


class Item(Entity):
    def __init__(self, universe, environment, abs_pos, color):
        super().__init__(universe, environment, abs_pos, color)
