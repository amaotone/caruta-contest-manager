import pandas as pd

from murasame.utils import make_board, append_seat_number

data = pd.read_excel("members.xlsx", index_col=0)
board = make_board(data, keys=["学校", "地域"])
sheet = append_seat_number(data, board, label="座席", fill="不戦")

board.to_excel("board.xlsx")
sheet.to_excel("list.xlsx")
