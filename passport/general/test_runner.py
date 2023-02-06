from passport.backend.tools.metrics.runner import grouper


def test_grouper_small_data():
    small_data = ['a'] * 10
    assert list(grouper(small_data, 100)) == [['a'] * 10]


def test_grouper_big_data():
    big_data = ['a'] * 10
    assert list(grouper(big_data, 5)) == [['a'] * 5, ['a'] * 5]
