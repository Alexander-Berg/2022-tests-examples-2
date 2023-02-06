import datetime
import decimal

import pytest

from fleet_rent.entities import park
from fleet_rent.generated.cron import cron_context as context
from fleet_rent.generated.cron import run_cron


@pytest.mark.now('2020-01-04T00:00:00+00:00')
@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
@pytest.mark.config(
    FLEET_RENT_SAME_PARK_TRANSACTIONS_PROCESSING={'is_enabled': True},
)
async def test_sptl(cron_context: context.Context, patch):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info_batch')
    async def _get_batch(park_ids):
        parks = [park.Park(id='owner_park_id', clid='clid', tz_offset=3)]
        return {x.id: x for x in parks}

    await run_cron.main(
        ['fleet_rent.crontasks.create_same_park_transactions', '-t', '0'],
    )
    transactions_raw = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.same_park_transactions_log ORDER BY id',
    )
    transactions = [dict(t) for t in transactions_raw]
    for transaction in transactions:
        del transaction['modified_at_tz']

    d = decimal.Decimal  # pylint: disable=invalid-name
    utc = datetime.timezone.utc
    assert transactions == [
        {
            'id': 1,
            'record_id': 'record_id1',
            'serial_id': 1,
            'category_id': 'partner_service_recurring_payment',
            'description': '1 (title)',
            'driver_id': 'driver_id',
            'park_id': 'owner_park_id',
            'event_at_tz': datetime.datetime(2020, 1, 1, 0, 0, tzinfo=utc),
            'amount': d('100'),
            'uploaded_at_tz': None,
        },
        {
            'id': 2,
            'record_id': 'record_id2',
            'serial_id': 1,
            'category_id': 'partner_service_recurring_payment',
            'description': '2 (title)',
            'driver_id': 'driver_id',
            'park_id': 'owner_park_id',
            'event_at_tz': datetime.datetime(2020, 1, 1, 0, 0, tzinfo=utc),
            'amount': d('100'),
            'uploaded_at_tz': None,
        },
        {
            'id': 3,
            'record_id': 'record_id1',
            'serial_id': 2,
            'category_id': 'partner_service_recurring_payment',
            'description': '1 (title)',
            'driver_id': 'driver_id',
            'park_id': 'owner_park_id',
            'event_at_tz': datetime.datetime(2020, 1, 2, 0, 0, tzinfo=utc),
            'amount': d('0'),
            'uploaded_at_tz': None,
        },
        {
            'id': 4,
            'record_id': 'record_id1',
            'serial_id': 3,
            'category_id': 'partner_service_recurring_payment',
            'description': '1 (title)',
            'driver_id': 'driver_id',
            'park_id': 'owner_park_id',
            'event_at_tz': datetime.datetime(2020, 1, 3, 0, 0, tzinfo=utc),
            'amount': d('100'),
            'uploaded_at_tz': None,
        },
        {
            'id': 5,
            'record_id': 'record_id2',
            'serial_id': 2,
            'category_id': 'partner_service_recurring_payment',
            'description': '2 (title)',
            'driver_id': 'driver_id',
            'park_id': 'owner_park_id',
            'event_at_tz': datetime.datetime(2020, 1, 2, 0, 0, tzinfo=utc),
            'amount': d('100'),
            'uploaded_at_tz': None,
        },
        {
            'id': 6,
            'record_id': 'record_id3',
            'serial_id': 1,
            'category_id': 'partner_service_recurring_payment',
            'description': '3 (title)',
            'driver_id': 'driver_id',
            'park_id': 'owner_park_id',
            'event_at_tz': datetime.datetime(2020, 1, 1, 0, 0, tzinfo=utc),
            'amount': d('100'),
            'uploaded_at_tz': None,
        },
        {
            'id': 7,
            'record_id': 'record_id3',
            'serial_id': 2,
            'category_id': 'partner_service_recurring_payment',
            'description': '3 (title)',
            'driver_id': 'driver_id',
            'park_id': 'owner_park_id',
            'event_at_tz': datetime.datetime(2020, 1, 2, 0, 0, tzinfo=utc),
            'amount': d('0'),
            'uploaded_at_tz': None,
        },
        {
            'id': 8,
            'record_id': 'record_id3',
            'serial_id': 3,
            'category_id': 'partner_service_recurring_payment',
            'description': '3 (title)',
            'driver_id': 'driver_id',
            'park_id': 'owner_park_id',
            'event_at_tz': datetime.datetime(2020, 1, 3, 0, 0, tzinfo=utc),
            'amount': d('100'),
            'uploaded_at_tz': None,
        },
    ]
