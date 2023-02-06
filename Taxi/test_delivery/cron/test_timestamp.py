# pylint: disable=redefined-outer-name
import datetime

import pytest


@pytest.fixture
def get_timestamp(pgsql):
    query = 'SELECT updated_at FROM delivery.avito_timestamp'
    cursor = pgsql['delivery'].cursor()

    def _get_timestamp():
        cursor.execute(query)
        row = cursor.fetchone()
        return row[0] if row else None

    return _get_timestamp


@pytest.mark.now('2020-04-22 12:00:00')
async def test_previous_null(mock_avito, cron_runner, get_timestamp):
    mock_avito()

    assert get_timestamp() is None
    await cron_runner.avito_process()
    assert get_timestamp() == datetime.datetime(2020, 4, 22, 12, 0)


@pytest.mark.pgsql(
    'delivery',
    queries=[
        'INSERT INTO delivery.avito_timestamp (updated_at)'
        ' VALUES (\'2020-04-22 11:50:00\')',
    ],
)
@pytest.mark.now('2020-04-22 12:00:00')
async def test_previous_update(mock_avito, cron_runner, get_timestamp):
    mock_avito()

    assert get_timestamp() == datetime.datetime(2020, 4, 22, 11, 50)
    await cron_runner.avito_process()
    assert get_timestamp() == datetime.datetime(2020, 4, 22, 12, 0)
