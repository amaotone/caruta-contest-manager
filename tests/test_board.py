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
def test_valid_match(board, a, b, expected):
    assert board._is_valid(a, b) is expected
