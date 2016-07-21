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

    def add(self, player):
        """Add player to board.

        This match-making algorithm acts upon a Guidelines for Caruta
        Competition proposed by All Japan Caruta Association.

        Args:
            player (pd.Series): Player to be added.

        See Also:
            http://www.karuta.or.jp/kitei/kyougikai.pdf

        """
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

        raise ValueError("Match-making is already completed.")

    @property
    def _single_player(self):
        assert len(self._upper) > len(self._lower)
        return self._upper[len(self._lower)]

    def _change_players(self, player):
        opponent = self._single_player
        for i, a, b in enumerate(zip(self._upper, self._lower)):
            if self._is_valid(player, b) and self._is_valid(opponent, a):
                self._upper[i] = player
                self._lower.append(a)
                return

            if self._is_valid(a, player) and self._is_valid(opponent, b):
                self._lower[i] = player
                self._lower.append(b)
                return

        raise ValueError("There is no changeable player.")

    def _is_valid(self, a, b):
        for key in self.keys:
            if a.ix[key] == b.ix[key]:
                return False
        return True

    def _is_last(self, lst):
        return len(lst) >= self.match_count

    def _on_upper(self):
        return len(self._upper) == len(self._lower)
