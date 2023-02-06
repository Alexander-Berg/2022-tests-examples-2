import pytest

from orderhistory.utils import simplify_track


@pytest.mark.parametrize(
    'start, end, point, distance',
    [
        ([0, 0], [1, 0], [0, 1], 1),
        ([0, 0], [1, 0], [0, -2], 4),
        ([0, 0], [1, 0], [-1, 0], 1),
        ([0, 0], [1, 0], [2, 0], 1),
        ([0, 0], [1, 1], [0, 1], 0.5),
    ],
)
def test_distance(start, end, point, distance):
    # pylint: disable=protected-access
    assert simplify_track._distance(start, end, point) == pytest.approx(
        distance, 1e-9,
    )


_SIMPLE_LINE = [[0, 0], [2, 2], [4, 0], [5, 1], [6, 0]]
_TRICKY_LINE = [[0, 0], [-2, 1], [1, 2], [2, 0]]
_DUPLICATE_POINTS_LINE = [[0, 0], [1, 1], [1, 1]]


@pytest.mark.parametrize(
    'original_line, max_points, simplified_line',
    [
        ([], 2, []),
        (_SIMPLE_LINE, 1, _SIMPLE_LINE[:1] + _SIMPLE_LINE[-1:]),
        (_SIMPLE_LINE, len(_SIMPLE_LINE), _SIMPLE_LINE),
        (_SIMPLE_LINE, 4, _SIMPLE_LINE[:3] + _SIMPLE_LINE[-1:]),
        (_TRICKY_LINE, 3, _TRICKY_LINE[:2] + _TRICKY_LINE[3:]),
        (_DUPLICATE_POINTS_LINE, 3, _DUPLICATE_POINTS_LINE),
    ],
)
def test_simplify_track(original_line, max_points, simplified_line):
    assert (
        simplify_track.simplify_polyline(original_line, max_points)
        == simplified_line
    )
