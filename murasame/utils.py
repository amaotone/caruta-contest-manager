import math

import numpy as np
import pandas as pd

from .board import Board


def winner_count(player_count):
    return 2 ** (math.ceil(math.log(player_count, 2)) - 1)


def match_count(player_count):
    return player_count - winner_count(player_count)


def make_board(data, keys):
    player_count = data.shape[0]
    board = Board(match_count(player_count), keys=keys)

    shuffled = data.reindex(np.random.permutation(data.index))
    for i, row in shuffled.iterrows():
        if board.completed:
            break
        board.append(row)

    return board


def append_seat_number(data, board, label="seat", fill="bye"):
    seat_list = board.as_dataframe(reset_index=True, start_index=1)
    ref = pd.DataFrame({label: seat_list.index}, index=seat_list["index"])

    res = data.merge(right=ref, left_index=True, right_index=True, how="left")
    res[label] = res[label].fillna(fill)

    return res
