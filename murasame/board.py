import warnings

import pandas as pd


class Board(object):
    def __init__(self, match_count, keys=None):
        """Initialize match display board.

        Args:
            match_count (int): Number of matches.
            keys (list[str]): Keys for deciding whether the match is valid.
                Default value is `["club"]`.

        """
        self._upper = []
        self._lower = []

        self.match_count = match_count
        self.keys = keys if keys else ["club"]

    def append(self, player):
        """Append player to board.

        This match-making algorithm acts upon a Guidelines for Caruta
        Competition proposed by All Japan Caruta Association.

        Args:
            player (pd.Series): Player to be added.

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

    def as_dataframe(self, reset_index=False, drop_id=False, start_index=0,
                     trim=False):
        if trim:
            reset_index = True
            drop_id = True
            start_index = 1

        res = pd.DataFrame(self.all)
        if reset_index:
            res.reset_index(drop=drop_id, inplace=True)
            res.index += start_index

        return res

    def to_excel(self, path="board.xlsx"):
        res = self.as_dataframe(trim=True)
        res.to_excel(path)

    @property
    def all(self):
        return list(sum(zip(self._upper, self._lower), ()))

    @property
    def completed(self):
        """Check match-making is completed."""
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
