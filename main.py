from globals import *
from universe import Universe
from event_handler import handle_events_and_input

# pygame init
# todo pg display flags https://stackoverflow.com/questions/29135147/what-do-hwsurface-and-doublebuf-do
pg.display.set_caption("Space Sim")
pg.font.init()
print("Pygame init")


def main():
    clock = pg.time.Clock()
    screen: pg.Surface = pg.display.set_mode((SCREEN_W, SCREEN_H))
    universe = Universe(screen)

    while True:
        dt = clock.tick(MAX_FPS) / 1000.0
        if not universe.paused:
            universe.render.last_dt = dt
            universe.tick(dt)

        if universe.environment.celestial_body:
            universe.camera.snap_to_player()
        else:
            universe.camera.snap_to_locked_celestial()

        universe.render.draw_screen()

        try:
            handle_events_and_input(universe)
        except InterruptedError:
            print("Exiting")
            break


if __name__ == "__main__":
    main()
