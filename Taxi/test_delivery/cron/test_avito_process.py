# pylint: disable=redefined-outer-name
import pytest

DELIVERY_AVITO_PUSHUP_SCHEDULE = {
    'city1': {
        'x10_1': {
            'item_ids': [1, 2, 3],
            'time_of_day_start': '09:00',
            'time_of_day_finish': '12:00',
        },
    },
    'city2': {
        'turbo_sale&xl': {
            'item_ids': [4, 5, 6],
            'time_of_day_start': '09:00',
            'time_of_day_finish': '12:00',
        },
        'pushup': {
            'item_ids': [4, 5, 6],
            'time_of_day_start': '12:00',
            'time_of_day_finish': '18:00',
            'period_minutes': 60,
        },
    },
}


@pytest.mark.parametrize(
    'vas_count, package_count',
    [
        pytest.param(
            0,
            0,
            marks=pytest.mark.now('2020-04-21 08:10:00'),
            id='before interval',
        ),
        pytest.param(
            1, 2, marks=pytest.mark.now('2020-04-21 09:10:00'), id='2 groups',
        ),
        pytest.param(
            1,
            2,
            marks=pytest.mark.now('2020-04-21 10:10:00'),
            id='2 groups repeat',
        ),
        pytest.param(
            1,
            0,
            marks=pytest.mark.now('2020-04-21 12:10:00'),
            id='3 group start',
        ),
        pytest.param(
            1,
            0,
            marks=pytest.mark.now('2020-04-21 17:10:00'),
            id='3 group end',
        ),
        pytest.param(
            0,
            0,
            marks=pytest.mark.now('2020-04-21 18:10:00'),
            id='after interval',
        ),
    ],
)
@pytest.mark.config(
    DELIVERY_AVITO_PUSHUP_SCHEDULE=DELIVERY_AVITO_PUSHUP_SCHEDULE,
)
async def test_new_subscription(
        cron_runner, mock_avito, vas_count, package_count,
):
    handler_vas, handler_package = mock_avito()

    await cron_runner.avito_process()

    assert handler_vas.times_called == vas_count
    assert handler_package.times_called == package_count


@pytest.mark.config(
    DELIVERY_AVITO_PUSHUP_SCHEDULE=DELIVERY_AVITO_PUSHUP_SCHEDULE,
)
@pytest.mark.now('2020-04-21 09:10:00')
async def test_api_error(cron_runner, mock_avito, pgsql):
    """API errors should be skipped
    No DB changes afterwards"""
    handler_vas, handler_package = mock_avito(return_code=403)

    await cron_runner.avito_process()

    assert handler_vas.times_called == 0  # one call to "xl" should be skipped
    assert handler_package.times_called == 2

    cursor = pgsql['delivery'].cursor()
    cursor.execute('SELECT COUNT(*) FROM delivery.avito_subscription')
    assert cursor.fetchone()[0] == 0
