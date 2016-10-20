import math
import os
import warnings

import numpy as np
import pandas as pd


class Board(object):
    def __init__(self, match_count, keys=None):
        """Initialize match display board.

        Args:
            match_count (int): Number of matches.
            keys (list[str]): Keys for deciding whether the match is valid.
                Default value is `["club"]`.

        """
        self._upper = list()
        self._lower = list()

        self.match_count = match_count
        self.keys = keys if keys else ["club"]

    def append(self, player):
        """Append player to board.

        This match-making algorithm acts upon a Guidelines for Caruta
        Competition proposed by All Japan Caruta Association.

        Args:
            player (pd.Series): A player to be added.

        See Also:
            http://www.karuta.or.jp/kitei/kyougikai.pdf

        """
        assert len(self._upper) >= len(self._lower)

        if self._on_upper():
            self._upper.append(player)
            return

        if self._is_valid(self._single_player, player):
            self._lower.append(player)
            return

        if not self._is_last(self._upper):
            self._upper.append(player)
            return

        if not self._is_last(self._lower):
            self._change_players(player)
            return

        warnings.warn("Match-making is already completed.")

    def validate(self):
        """Check all organized matches are valid."""
        for a, b in zip(self._upper, self._lower):
            if not self._is_valid(a, b):
                return False
        return True

    def as_dataframe(self):
        return pd.DataFrame(self.all)

    @property
    def all(self):
        return list(sum(zip(self._upper, self._lower), ()))

    @property
    def completed(self):
        if not self.validate():
            return False
        return len(self._upper) == len(self._lower) == self.match_count

    @property
    def _single_player(self):
        assert len(self._upper) > len(self._lower)
        return self._upper[len(self._lower)]

    def _change_players(self, player):
        opponent = self._single_player
        for i, (a, b) in enumerate(zip(self._upper, self._lower)):
            if self._is_valid(player, b) and self._is_valid(opponent, a):
                self._upper[i] = player
                self._lower.append(a)
                return

            if self._is_valid(a, player) and self._is_valid(opponent, b):
                self._lower[i] = player
                self._lower.append(b)
                return

        warnings.warn("No player is changeable.")
        self._lower.append(player)

    def _is_valid(self, a, b):
        for key in self.keys:
            if a.ix[key] == b.ix[key]:
                return False
        return True

    def _is_last(self, lst):
        return len(lst) >= self.match_count

    def _on_upper(self):
        return len(self._upper) == len(self._lower)

    def index(self, player):
        return self.all.index(player)

    def __contains__(self, item):
        return item in self.all

    def __getitem__(self, i):
        return self.all[i]

    def __len__(self):
        return len(self.all)


class Maker(object):
    def __init__(self, file):
        self.dfs = pd.read_excel(file, sheetname=None)
        self.results = None

    def make(self, keys, id_label='ID', seat_label='seat', bye_display='bye'):
        results = list()

        start = 1
        for classname, df in classname_sorted(self.dfs.items()):
            assert start % 2 == 1

            board = self._make_board(df, keys=keys)
            board = self._trim_board(board, start_index=start)

            sheet = self._make_sheet(df, board, on=id_label, label=seat_label,
                                     bye_display=bye_display)

            results.append({
                'classname': classname,
                'board': board,
                'sheet': sheet
            })

            start += board.shape[0]

        self.results = results

    def save(self, outdir='result', board_file='board.xlsx',
             sheet_file='sheet.xlsx'):
        os.makedirs(outdir, exist_ok=True)
        board_writer = pd.ExcelWriter(os.path.join(outdir, board_file),
                                      engine='xlsxwriter')
        sheet_writer = pd.ExcelWriter(os.path.join(outdir, sheet_file),
                                      engine='xlsxwriter')

        for res in self.results:
            res['board'].to_excel(board_writer, res['classname'], index=False)
            res['sheet'].to_excel(sheet_writer, res['classname'], index=False)

        board_writer.save()
        sheet_writer.save()

    @staticmethod
    def _make_sheet(df, board, on, label, bye_display):
        ref = pd.DataFrame({label: board.index, on: board[on]})
        sheet = df.merge(right=ref, on=on, how='left')
        sheet[label] = sheet[label].fillna(bye_display)
        return sheet

    @staticmethod
    def _make_board(df, keys):
        player_count = df.shape[0]
        board = Board(match_count(player_count), keys=keys)

        shuffled = df.reindex(np.random.permutation(df.index))
        for i, row in shuffled.iterrows():
            board.append(row)
            if board.completed:
                break

        return board.as_dataframe()

    @staticmethod
    def _trim_board(df, start_index=1):
        df.reset_index(drop=True, inplace=True)
        df.index += start_index
        return df


def classname_sorted(items):
    return sorted(items, key=lambda x: (x[0][0], int(x[0][1:])))


def match_count(player_count):
    winner_count = 2 ** (math.ceil(math.log(player_count, 2)) - 1)
    return player_count - winner_count
