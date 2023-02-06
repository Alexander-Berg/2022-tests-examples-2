# pylint: disable=redefined-outer-name
import datetime

import pytest


@pytest.fixture
def get_applied_at(pgsql):
    query = (
        'SELECT applied_at FROM'
        ' delivery.avito_subscription'
        ' WHERE item_id = %s AND vas_package_id = %s'
    )
    cursor = pgsql['delivery'].cursor()

    def _get_applied(item_id, vas_package_id):
        cursor.execute(query, (item_id, vas_package_id))
        row = cursor.fetchone()
        return row[0]

    return _get_applied


@pytest.mark.config(
    DELIVERY_AVITO_PUSHUP_SCHEDULE={
        'city2': {
            'pushup': {
                'item_ids': [7, 8, 9],
                'time_of_day_start': '09:00',
                'time_of_day_finish': '12:00',
            },
        },
    },
)
@pytest.mark.parametrize(
    'vas_count, item_id',
    [
        pytest.param(
            1,
            7,
            marks=pytest.mark.now('2020-04-21 09:10'),
            id='positive, expired',
        ),
        pytest.param(
            1,
            8,
            marks=pytest.mark.now('2020-04-21 10:10'),
            id='positive, applied today',
        ),
        pytest.param(
            0,
            9,
            marks=pytest.mark.now('2020-04-21 11:10'),
            id='negative, applied yesterday',
        ),
    ],
)
async def test_expire(
        get_applied_at, cron_runner, mock_avito, vas_count, item_id,
):
    handler_vas, _ = mock_avito()

    old_applied = get_applied_at(item_id, 'pushup')
    await cron_runner.avito_process()

    assert handler_vas.times_called == vas_count
    new_applied = get_applied_at(item_id, 'pushup')
    if vas_count:
        assert new_applied > old_applied
        assert new_applied == datetime.datetime.utcnow()
    else:
        assert new_applied == old_applied
