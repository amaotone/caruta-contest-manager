import math

import yaml


def load_setting(file="setting.yml"):
    with open(file, "r") as f:
        setting = yaml.load(f)
    return setting


def classname_sorted(items):
    return sorted(items, key=lambda x: (x[0][0], int(x[0][1:])))


def match_count(player_count):
    winner_count = 2 ** (math.ceil(math.log(player_count, 2)) - 1)
    return player_count - winner_count