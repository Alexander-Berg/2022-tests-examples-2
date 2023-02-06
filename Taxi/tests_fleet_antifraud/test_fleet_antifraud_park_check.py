import datetime

import dateutil
import pytest

NOW = '2020-01-01T12:00:00+00:00'


@pytest.mark.now(NOW)
@pytest.mark.config(
    FLEET_ANTIFRAUD_PARK_CHECK={
        'is_enabled': True,
        'expiring_interval': 86400,
        'billing_fetching_overlap': 3600,
    },
)
async def test_duration(stq_runner, mock_api, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_antifraud_park_check.call(
        task_id='1',
        kwargs={
            'park_id': 'PARK-01',
            'contractor_id': 'CONTRACTOR-01',
            'order_id': 'ORDER-04',
        },
    )

    assert pg_dump() == {
        **pg_initial,
        'park_check_suspicious': {
            **pg_initial['park_check_suspicious'],
            ('PARK-01', 'CONTRACTOR-01', 'ORDER-04', None): (
                'duration_max',
                None,
                datetime.timedelta(seconds=1000),
                dateutil.parser.parse('2020-01-01T01:00:00+00:00'),
                dateutil.parser.parse('2020-01-02T01:00:00+00:00'),
                None,
                None,
                None,
                2,
                dateutil.parser.parse('2020-01-02T01:00:00+00:00'),
            ),
        },
    }


@pytest.mark.now(NOW)
@pytest.mark.config(
    FLEET_ANTIFRAUD_PARK_CHECK={
        'is_enabled': True,
        'expiring_interval': 86400,
        'billing_fetching_overlap': 3600,
    },
)
async def test_transporting(stq_runner, mock_api, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_antifraud_park_check.call(
        task_id='1',
        kwargs={
            'park_id': 'PARK-01',
            'contractor_id': 'CONTRACTOR-01',
            'order_id': 'ORDER-05',
        },
        expect_fail=True,
    )

    assert pg_dump() == pg_initial


@pytest.mark.now(NOW)
@pytest.mark.config(
    FLEET_ANTIFRAUD_PARK_CHECK={
        'is_enabled': True,
        'expiring_interval': 86400,
        'billing_fetching_overlap': 3600,
    },
)
async def test_not_suspicious(stq_runner, mock_api, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_antifraud_park_check.call(
        task_id='1',
        kwargs={
            'park_id': 'PARK-01',
            'contractor_id': 'CONTRACTOR-01',
            'order_id': 'ORDER-06',
        },
    )

    assert pg_dump() == pg_initial


@pytest.mark.now(NOW)
@pytest.mark.config(
    FLEET_ANTIFRAUD_PARK_CHECK={
        'is_enabled': True,
        'expiring_interval': 86400,
        'billing_fetching_overlap': 3600,
    },
)
async def test_minute_cost(stq_runner, mock_api, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_antifraud_park_check.call(
        task_id='1',
        kwargs={
            'park_id': 'PARK-01',
            'contractor_id': 'CONTRACTOR-01',
            'order_id': 'ORDER-07',
        },
    )

    assert pg_dump() == {
        **pg_initial,
        'park_check_suspicious': {
            **pg_initial['park_check_suspicious'],
            ('PARK-01', 'CONTRACTOR-01', 'ORDER-07', None): (
                'minute_cost_max',
                100,
                None,
                dateutil.parser.parse('2020-01-01T01:00:00+00:00'),
                dateutil.parser.parse('2020-01-02T01:00:00+00:00'),
                None,
                None,
                None,
                2,
                dateutil.parser.parse('2020-01-02T01:00:00+00:00'),
            ),
        },
    }


@pytest.mark.now(NOW)
@pytest.mark.config(
    FLEET_ANTIFRAUD_PARK_CHECK={
        'is_enabled': True,
        'expiring_interval': 86400,
        'billing_fetching_overlap': 3600,
    },
)
async def test_cash(stq_runner, mock_api, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_antifraud_park_check.call(
        task_id='1',
        kwargs={
            'park_id': 'PARK-01',
            'contractor_id': 'CONTRACTOR-01',
            'order_id': 'ORDER-08',
        },
    )

    assert pg_dump() == pg_initial
