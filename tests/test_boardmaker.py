import pandas as pd
import pytest

from maker import Board
from maker import match_count

nan = float("nan")


@pytest.mark.parametrize(('player', 'match'), [
    (128, 64),
    (127, 63),
    (100, 36),
    (65, 1),
    (64, 32),
    (3, 1),
    (2, 1),
])
def test_match_count(player, match):
    assert match_count(player) == match


def pytest_funcarg__board(request):
    return Board(match_count=2, keys=["club", "region"])


@pytest.mark.parametrize(("a", "b", "expected"), [
    (pd.Series({"club": "a", "region": nan}),
     pd.Series({"club": "a", "region": "west"}),
     False),
    (pd.Series({"club": "a", "region": nan}),
     pd.Series({"club": "b", "region": nan}),
     True),
    (pd.Series({"club": "a", "region": nan}),
     pd.Series({"club": "b", "region": "west"}),
     True),
    (pd.Series({"club": "a", "region": "west"}),
     pd.Series({"club": "b", "region": "west"}),
     False),
])
def test_valid_match(a, b, expected):
    board = Board(match_count=2, keys=["club", "region"])
    assert board._is_valid(a, b) is expected


@pytest.mark.parametrize(("data"), [
    [pd.Series({"club": "a"}),
     pd.Series({"club": "a"}),
     pd.Series({"club": "a"})]
])
def test_same_club_in_a_row(data):
    board = Board(match_count=10)
    for d in data:
        board.append(d)
    assert len(board._upper) == 3


@pytest.mark.parametrize(("data"), [
    [pd.Series({"club": "a", "name": "a"}),
     pd.Series({"club": "a", "name": "b"}),
     pd.Series({"club": "a", "name": "c"}),
     pd.Series({"club": "a", "name": "d"})]
])
def test_unavoidable_same_club(data):
    board = Board(match_count=2)
    for d in data:
        board.append(d)
