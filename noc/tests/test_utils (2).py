from noc.pahom import utils


def test_chunked():
    assert list(utils.chunked(2, [1, 2, 3, 4])) == [(1, 2), (3, 4)]
    assert list(utils.chunked(2, [1, 2, 3])) == [(1, 2), (3, )]
    assert list(utils.chunked(3, [1, 2, 3, 4])) == [(1, 2, 3), (4, )]
    assert list(utils.chunked(3, [1, 2, 3, 4, 5])) == [(1, 2, 3), (4, 5, )]
