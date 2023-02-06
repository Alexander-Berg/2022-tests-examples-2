import datetime

import pytest

from discounts_operation_calculations.internals import error as error_lib
from discounts_operation_calculations.stq import multidraft


def task_body(closed_at, city):
    return {
        'city': city,
        'x_yandex_login': 'yandex_login',
        'active_suggest_id': 1747,
        'not_approved_suggests': False,
        'closed_at': closed_at,
    }


@pytest.mark.now('2022-06-22 17:30:00')
@pytest.mark.parametrize(
    'city, closed_at, expected_end, expected_lag',
    [
        (
            'test_city',
            None,
            datetime.datetime.fromisoformat('2022-06-22 19:10:00'),
            100,
        ),
        (
            'test_city_push',
            None,
            datetime.datetime.fromisoformat('2022-06-22 18:20:00'),
            50,
        ),
        (
            'test_city',
            '2022-06-22 21:40:00',
            datetime.datetime.fromisoformat('2022-06-22 21:40:00'),
            250,
        ),
        (
            'test_city_push',
            '2022-06-23',
            datetime.datetime.fromisoformat('2022-06-23 00:00:00'),
            390,
        ),
        (
            'test_city',
            '2022-06-22 17:41:00',
            datetime.datetime.fromisoformat('2022-06-22 17:41:00'),
            11,
        ),
        (
            'test_city_push',
            '2022-06-22 18:21:00',
            datetime.datetime.fromisoformat('2022-06-22 18:21:00'),
            51,
        ),
    ],
)
@pytest.mark.usefixtures('mock_active_discounts')
async def test_task_end_time(
        stq3_context, city, closed_at, expected_end, expected_lag,
):
    body = task_body(closed_at=closed_at, city=city)
    # pylint: disable=protected-access
    end, lag = await multidraft._get_task_end(stq3_context, body)
    assert end == expected_end
    assert lag == expected_lag


@pytest.mark.now('2022-06-22 17:30:00')
@pytest.mark.parametrize(
    'city, closed_at',
    [
        ('test_city', '2022-06-22 15:41'),
        ('test_city_push', '2022-06-18'),
        ('test_city_push', '2022-06-22 18:00'),
        ('test_city', '2022-06-22 17:39:00'),
    ],
)
@pytest.mark.usefixtures('mock_active_discounts')
async def test_task_end_time_error(stq3_context, city, closed_at):
    body = task_body(closed_at=closed_at, city=city)
    with pytest.raises(error_lib.DiscountDurationError):
        # pylint: disable=protected-access
        await multidraft._get_task_end(stq3_context, body)
