import datetime

import aiohttp.web
import pytest

from testsuite.utils import http

from fleet_rent.generated.cron import cron_context as context
from fleet_rent.generated.cron import run_cron


@pytest.mark.now('2020-01-04T00:00:00')
@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
@pytest.mark.config(
    FLEET_RENT_SAME_PARK_TRANSACTIONS_PROCESSING={'is_enabled': True},
)
async def test_run_cspt(
        mock_fleet_transactions_api, cron_context: context.Context,
):
    expected_tokens = [
        'a6762855d59b488790ebd8e564b31ddc_3',
        'a6762855d59b488790ebd8e564b31ddc_4',
    ]
    requests = [
        {
            'park_id': 'owner_park_id',
            'driver_profile_id': 'driver_id',
            'category_id': 'category',
            'amount': '-100',
            'description': 'title (#1)',
            'event_at': '2020-01-04T03:00:00+03:00',
        },
        {
            'park_id': 'owner_park_id',
            'driver_profile_id': 'driver_id',
            'category_id': 'category',
            'amount': '-100',
            'description': 'title (#1)',
            'event_at': '2020-01-03T15:00:00+03:00',
        },
    ]

    @mock_fleet_transactions_api(
        '/v1/parks/driver-profiles/transactions/by-platform',
    )
    async def _fill(request: http.Request):
        assert request.headers['X-Idempotency-Token'] == expected_tokens.pop(0)
        assert request.json == requests.pop(0)
        return aiohttp.web.json_response(
            {
                'park_id': 'owner_park_id',
                'driver_profile_id': 'driver_id',
                'category_id': 'category',
                'amount': '-100',
                'description': 'title (#1)',
                'event_at': '2020-01-03T03:00:00+03:00',
                'currency_code': 'RUB',
                'created_by': {'identity': 'platform'},
            },
        )

    await run_cron.main(
        ['fleet_rent.crontasks.send_same_park_transactions', '-t', '0'],
    )

    transactions = await cron_context.pg.master.fetch(
        'SELECT * FROM rent.same_park_transactions_log ORDER BY id',
    )
    upload_dts = [t['uploaded_at_tz'] for t in transactions]
    utc = datetime.timezone.utc
    assert upload_dts == [
        datetime.datetime(2020, 1, 1, 0, 0, tzinfo=utc),
        None,
        datetime.datetime(2020, 1, 4, 0, 0, tzinfo=utc),
        datetime.datetime(2020, 1, 4, 0, 0, tzinfo=utc),
    ]
