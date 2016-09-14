import pandas as pd
import pytest

from murasame.board import Board

nan = float("nan")


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
