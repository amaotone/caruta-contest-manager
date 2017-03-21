import math
import os
import sys

import yaml

def load_setting(name="setting.yml"):
    path = os.path.join(os.path.dirname(sys.argv[0]), name)
    with open(path, "r") as f:
        setting = yaml.load(f)
    return setting


def classname_sorted(items):
    return sorted(items, key=lambda x: (x[0][0], int(x[0][1:])))


def match_count(player_count):
    winner_count = 2 ** (math.ceil(math.log(player_count, 2)) - 1)
    return player_count - winner_count
