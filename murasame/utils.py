import math

import numpy as np
import pandas as pd

from .board import Board


def winner_count(player_count):
    return 2 ** (math.ceil(math.log(player_count, 2)) - 1)


def match_count(player_count):
    return player_count - winner_count(player_count)


def make_board(df, keys):
    player_count = len(df)
    board = Board(match_count(player_count), keys=keys)

    shuffled = df.reindex(np.random.permutation(df.index))
    for i, row in shuffled.iterrows():
        if board.completed:
            break
        board.append(row)

    return board


def trim_board(df, start_index=0, drop_id=False, id_label="index"):
    df.reset_index(drop=drop_id, inplace=True)
    df.columns.values[0] = id_label
    df.index += start_index
    return df


def append_seat_number(df, board, id_label="index", label="seat", fill="bye",
                       start_index=1):
    ref = pd.DataFrame({label: board.index}, index=board[id_label])
    res = df.merge(right=ref, left_index=True, right_index=True, how="left")
    res[label] = res[label].fillna(fill)
    return res
