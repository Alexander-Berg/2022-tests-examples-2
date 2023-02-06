import pytest

from taxi.core import autoincrement


@pytest.inline_callbacks
def test_increment():
    assert (yield autoincrement.increment('first')) == 1
    assert (yield autoincrement.increment('first')) == 2
    assert (yield autoincrement.increment('first')) == 3
    assert (yield autoincrement.increment('second')) == 1
    assert (yield autoincrement.increment('second')) == 2
    assert (yield autoincrement.increment('first')) == 4
