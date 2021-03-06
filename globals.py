import random
import os
import math
import numpy as np
import pygame as pg


# settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
MAX_FPS = 120
ASSETS_FOLDER = "assets"
TRACE_POINT_MAX_AGE = 1
MAX_TRACE_POINTS = 100  # per celestial object
N_BACKGROUND_STARS = 10

DEFAULT_TIME_FACTOR = 0.1
TIME_FACTOR_STEP = 0.01
TIME_FACTOR_MAX = 5
TIME_FACTOR_MIN = 0.01

CAMERA_ZOOM_FACTOR_MAX = 8
CAMERA_ZOOM_FACTOR_MIN = 0.5
CAMERA_MOVEMENT_STEP = 20  # todo should account for deltatime

SHOW_DEBUG = True
SHOW_CELESTIAL_BODY_LABEL = False
SHOW_GUEST_ORBITS = False


# assets
IMGS_BACKGROUND_STAR = [pg.image.load(os.path.join(ASSETS_FOLDER, f"bg_star_{i}.png"))
                        for i in range(7)]
IMG_PLAYER = pg.image.load(os.path.join(ASSETS_FOLDER, "astronaut.png"))


# colors
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
MAGENTA = 255, 0, 255
CYAN = 0, 255, 255

BLACK = 0, 0, 0
GRAY = 127, 127, 127
WHITE = 255, 255, 255

DARK_RED = 63, 0, 0
DARK_GREEN = 0, 63, 0
DARK_BLUE = 0, 0, 63
DARK_YELLOW = 63, 63, 0
DARK_MAGENTA = 63, 0, 63
DARK_CYAN = 0, 63, 63
DARK_GRAY = 63, 63, 63

BACKGROUND_COLOR = 6, 6, 20


# space constants
MASS_EARTH = 1 or 5.972e24
RADIUS_EARTH = 20 or 6.371e3
MASS_SUN = 1 or 1.989e30
RADIUS_SUN = 20 or 6.963e5
DISTANCE_EARTH = 100 or 1.495e8
DISTANCE_MOON = 20 or 8.844e5
RADIUS_MOON = 5 or 1.737e3
DISTANCE_STEPS = DISTANCE_EARTH * 0.5  # todo randomize orbital distances
STAR_DISTANCE = 2000
STAR_COLOR = YELLOW
MOON_COLOR = GRAY
PLANET_DISTANCE_VARIANCE = 0.2
PLANET_RADIUS_VARIANCE = 0.95
STAR_RADIUS_VARIANCE = 0.5


# quality of life constants
SCREEN_WIDTH_HALF, SCREEN_HEIGHT_HALF = round(SCREEN_WIDTH / 2), round(SCREEN_HEIGHT / 2)
SCREEN_CENTER = SCREEN_WIDTH_HALF, SCREEN_HEIGHT_HALF


# general functions
def get_random_dist(host, base, variance):
    return random.uniform(base * (len(host.guests) - variance + 1),
                          base * (len(host.guests) + variance + 1))


def get_random_radius(base, variance):
    return random.uniform(base * (1 - variance), base * (1 + variance))


def get_random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


# numpy shortcuts
def v2(x, y):
    return np.array([x, y])


v2_zero = v2(0.0, 0.0)
