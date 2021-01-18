from globals import *


def handle_events_and_input(universe):
    camera = universe.camera
    console = universe.console
    environment = universe.environment
    render = universe.render

    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            raise InterruptedError

        elif ev.type == pg.KEYDOWN:  # ACTIVE KEY PRESSES
            if ev.key == pg.K_RETURN:
                console.toggle()
            elif console.active:
                if ev.key == pg.K_BACKSPACE:
                    console.remove_last_character()

                else:
                    console.add_text(ev.unicode)

                continue

            locked_celestial = camera.locked_celestial
            if ev.key == pg.K_e:
                if not environment.celestial_body and locked_celestial:
                    environment.enter_celestial(locked_celestial)
                else:
                    environment.leave_celestial()
            elif ev.key == pg.K_f and environment.celestial_body:
                environment.player.drop_item()
            elif ev.key == pg.K_F1:
                render.show_debug = not render.show_debug
            elif ev.key == pg.K_o:
                render.show_orbits = not render.show_orbits
            elif ev.key == pg.K_q:
                raise InterruptedError
            elif ev.key == pg.K_r:
                universe.reset()
                universe.camera.clear_locked_celestial()
            elif ev.key == pg.K_SPACE:
                universe.paused = not universe.paused

        elif ev.type == pg.MOUSEBUTTONDOWN:
            if ev.button == 1:
                celestial = universe.get_hovered_object()
                if celestial:
                    camera.set_locked_celestial(celestial)

            elif ev.button == 4 and camera.zoom_factor <= CAMERA_ZOOM_FACTOR_MAX:
                camera.zoom_factor *= 2
            elif ev.button == 5 and camera.zoom_factor >= CAMERA_ZOOM_FACTOR_MIN:
                camera.zoom_factor *= 0.5

    pressed_keys = pg.key.get_pressed()
    if not console.active:  # PASSIVE KEY PRESSES
        if pressed_keys[pg.K_EQUALS] and universe.time_factor <= TIME_FACTOR_MAX:
            universe.time_factor += TIME_FACTOR_STEP
        if pressed_keys[pg.K_MINUS] and universe.time_factor >= TIME_FACTOR_MIN:
            universe.time_factor -= TIME_FACTOR_STEP

        if environment.celestial_body and not universe.paused:
            environment.player.move((pressed_keys[pg.K_RIGHT] or pressed_keys[pg.K_d]) -
                                    (pressed_keys[pg.K_LEFT] or pressed_keys[pg.K_a]))
            if pressed_keys[pg.K_w]:
                environment.player.jump()

        else:
            camera.move_center((pressed_keys[pg.K_RIGHT] or pressed_keys[pg.K_d]) -
                               (pressed_keys[pg.K_LEFT]
                                or pressed_keys[pg.K_a]),
                               (pressed_keys[pg.K_DOWN] or pressed_keys[pg.K_s]) -
                               (pressed_keys[pg.K_UP] or pressed_keys[pg.K_w]))
