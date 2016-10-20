import os
import warnings

import numpy as np
import pandas as pd

from .utils import classname_sorted, match_count


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
        self.results = dict()

    def make_board(self, keys):
        def make(df, keys):
            player_count = df.shape[0]
            board = Board(match_count(player_count), keys=keys)

            shuffled = df.reindex(np.random.permutation(df.index))
            for i, row in shuffled.iterrows():
                board.append(row)
                if board.completed:
                    break
            return board.as_dataframe()

        def trim(df, start_index=1):
            df.reset_index(drop=True, inplace=True)
            df.index += start_index
            return df

        start = 1
        for classname, df in classname_sorted(self.dfs.items()):
            assert start % 2 == 1

            board = make(df, keys=keys)
            board = trim(board, start_index=start)

            self.results[classname] = dict()
            self.results[classname]['board'] = board
            start += board.shape[0]

    def make_sheet(self, id_label, seat_label, fill):
        def make(df, board, id_label, seat_label, fill):
            ref = pd.DataFrame({id_label: board[id_label], seat_label:
                board.index})
            sheet = df.merge(right=ref, on=id_label, how='left')
            sheet[seat_label] = sheet[seat_label].fillna(fill)
            return sheet

        assert len(self.results) != 0
        for classname, df in classname_sorted(self.dfs.items()):
            board = self.results[classname]['board']
            sheet = make(df, board, id_label, seat_label, fill)
            self.results[classname]['sheet'] = sheet

    def save_board(self, path):
        w = self.writer(path)
        for classname, res in self.results.items():
            res['board'].to_excel(w, classname, index=False)

        w.save()

    def save_sheet(self, path, sort_by=None):
        w = self.writer(path)
        for classname, res in self.results.items():
            sheet = res['sheet'].copy()
            if sort_by is not None:
                sheet.sort_values(by=sort_by, inplace=True)
            sheet.to_excel(w, classname, index=False)

        w.save()

    @staticmethod
    def writer(path):
        root, _ = os.path.split(path)
        os.makedirs(root, exist_ok=True)
        return pd.ExcelWriter(path, engine='xlsxwriter')
