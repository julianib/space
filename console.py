from globals import *


class Console:
    def __init__(self, universe):
        self.universe = universe
        self.leading_text = "Type Here: "
        self.input_text = ""
        self.active = False
        self.text_color = WHITE
        self.position = (40, 200)

    def process(self):
        text = self.input_text.strip()
        text_lower = text.lower()
        text_lower_split = text_lower.split()
        print(f"Processing input \"{text}\"")

        if len(text_lower_split) == 0:
            return

        if text_lower_split[0] == "time":
            self.universe.set_time_factor(text_lower_split[1])
            return

        for celestial in self.universe.celestial_bodies:
            if str(celestial.uuid).lower() == text_lower or \
                    str(celestial).lower() == text_lower:
                celestial_type = type(celestial)
                print(celestial_type)
                self.universe.camera.set_locked_celestial(celestial)
                return

        if len(text_lower_split) == 1:
            return

        if text_lower_split[0] == "name":
            locked_celestial = self.universe.camera.locked_celestial
            if not locked_celestial:
                print("No locked celestial")
                return

            locked_celestial.set_name(" ".join(text.split()[1:]))

    def add_text(self, text):
        self.input_text += text

    def clear_text(self):
        self.input_text = ""

    def remove_last_character(self):
        self.input_text = self.input_text[:-1]

    def toggle(self):
        if self.active:
            self.process()
            self.clear_text()

        self.active = not self.active

    def draw(self):
        if not self.active:
            return

        surf = self.universe.font.render(self.leading_text + self.input_text,
                                         True, self.text_color)
        self.universe.screen.blit(surf, self.position)
