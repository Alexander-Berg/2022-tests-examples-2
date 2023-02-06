import datetime
import decimal

import pytest

from fleet_rent.generated.cron import cron_context as context_module

d = decimal.Decimal  # pylint: disable=invalid-name


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_sptl(cron_context: context_module.Context):
    await cron_context.pg_access.ext_park_trans_log.fill(
        datetime.datetime(2020, 1, 4, tzinfo=datetime.timezone.utc),
    )
    entries_raw = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.external_park_transactions_log ORDER BY id',
    )
    entries = [dict(e) for e in entries_raw]
    for transaction in entries:
        del transaction['modified_at_tz']

    assert entries == [
        {
            'amount': d('100'),
            'external_driver_id': 'original_driver_id',
            'external_driver_park_id': 'original_driver_park_id',
            'id': 1,
            'local_driver_id': 'driver_id',
            'park_id': 'park_id',
            'record_id': 'record_id1',
            'record_serial_id': 1,
            'serial_id': 1,
            'scheduled_at_tz': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'uploaded_at_tz': None,
        },
        {
            'amount': d('100'),
            'external_driver_id': 'original_driver_id',
            'external_driver_park_id': 'original_driver_park_id',
            'id': 2,
            'local_driver_id': 'driver_id',
            'park_id': 'park_id',
            'record_id': 'record_id2',
            'record_serial_id': 2,
            'serial_id': 1,
            'scheduled_at_tz': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'uploaded_at_tz': None,
        },
        {
            'amount': d('0'),
            'external_driver_id': 'original_driver_id',
            'external_driver_park_id': 'original_driver_park_id',
            'id': 3,
            'local_driver_id': 'driver_id',
            'park_id': 'park_id',
            'record_id': 'record_id1',
            'record_serial_id': 1,
            'serial_id': 2,
            'scheduled_at_tz': datetime.datetime(
                2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'uploaded_at_tz': None,
        },
        {
            'amount': d('100'),
            'external_driver_id': 'original_driver_id',
            'external_driver_park_id': 'original_driver_park_id',
            'id': 4,
            'local_driver_id': 'driver_id',
            'park_id': 'park_id',
            'record_id': 'record_id1',
            'record_serial_id': 1,
            'serial_id': 3,
            'scheduled_at_tz': datetime.datetime(
                2020, 1, 3, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'uploaded_at_tz': None,
        },
        {
            'amount': d('100'),
            'external_driver_id': 'original_driver_id',
            'external_driver_park_id': 'original_driver_park_id',
            'id': 5,
            'local_driver_id': 'driver_id',
            'park_id': 'park_id',
            'record_id': 'record_id2',
            'record_serial_id': 2,
            'serial_id': 2,
            'scheduled_at_tz': datetime.datetime(
                2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'uploaded_at_tz': None,
        },
        {
            'amount': d('100'),
            'external_driver_id': 'original_driver_id',
            'external_driver_park_id': 'original_driver_park_id',
            'id': 6,
            'local_driver_id': 'driver_id',
            'park_id': 'park_id',
            'record_id': 'record_id3',
            'record_serial_id': 3,
            'serial_id': 1,
            'scheduled_at_tz': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'uploaded_at_tz': None,
        },
        {
            'amount': d('0'),
            'external_driver_id': 'original_driver_id',
            'external_driver_park_id': 'original_driver_park_id',
            'id': 7,
            'local_driver_id': 'driver_id',
            'park_id': 'park_id',
            'record_id': 'record_id3',
            'record_serial_id': 3,
            'serial_id': 2,
            'scheduled_at_tz': datetime.datetime(
                2020, 1, 2, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'uploaded_at_tz': None,
        },
        {
            'amount': d('100'),
            'external_driver_id': 'original_driver_id',
            'external_driver_park_id': 'original_driver_park_id',
            'id': 8,
            'local_driver_id': 'driver_id',
            'park_id': 'park_id',
            'record_id': 'record_id3',
            'record_serial_id': 3,
            'serial_id': 3,
            'scheduled_at_tz': datetime.datetime(
                2020, 1, 3, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'uploaded_at_tz': None,
        },
    ]
