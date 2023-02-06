import datetime

import pytest

from workforce_management.common.models import schedule as schedule_module


@pytest.mark.parametrize(
    'input_data, expected_res',
    [
        (
            [[1, 5, 1], datetime.time(23), True, 60],
            [1380, 60, 1380, 60, 1380, 60, 1380, 60, 1380, 60, 2880],
        ),
        (
            [[3, 2], datetime.time(22), False, 60],
            [1320, 60, 1380, 60, 4260, 60, 60],
        ),
        (
            [[4, 3], datetime.time(15), True, 540],
            [6660, 540, 900, 540, 900, 540],
        ),
        ([[2, 2], datetime.time(10), False, 540], [600, 540, 900, 540, 3180]),
        ([[2, 2], datetime.time(10), True, 540], [3480, 540, 900, 540, 300]),
        (
            [[5, 2], datetime.time(21), False, 540],
            [0, 360, 900, 540, 900, 540, 900, 540, 900, 540, 3780, 180],
        ),
        (
            [[1, 3, 2, 1], datetime.time(15), True, 720],
            [0, 180, 2160, 720, 720, 720, 720, 720, 3600, 540],
        ),
        ([[2, 3], datetime.time(0), False, 720], [0, 720, 720, 720, 5040]),
        (
            [[2, 2], datetime.time(21), False, 360],
            [0, 180, 1080, 360, 3960, 180],
        ),
        (
            [[2, 2], datetime.time(22), False, 360],
            [0, 240, 1080, 360, 3960, 120],
        ),
        (
            [[4, 3], datetime.time(12), True, 720],
            [6480, 720, 720, 720, 720, 720, 0],
        ),
    ],
)
def test_schedule_v2(input_data, expected_res):
    res = schedule_module.format_schedule_v2(*input_data)
    assert res == expected_res
    assert sum(res) >= sum(input_data[0]) * 24 * 60
