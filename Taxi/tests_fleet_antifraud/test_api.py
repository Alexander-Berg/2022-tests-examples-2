import datetime
import decimal

import dateutil
import pytest


NOW = '2020-01-01T12:00:00+03:00'
PARK_ID = 'PARK-01'


@pytest.mark.now(NOW)
async def test_put_settings(fleet_v1, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v1.change_park_check_settings(
        park_id=PARK_ID,
        json={'cost_max': '10000', 'duration_min': 5, 'tips_max': '50'},
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'set_park_check_settings',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'park_check_settings': {
            **pg_initial['park_check_settings'],
            1: (
                'PARK-01',
                1,
                dateutil.parser.parse(NOW),
                decimal.Decimal('10000'),
                None,
                None,
                datetime.timedelta(seconds=5),
                decimal.Decimal('50'),
                None,
            ),
        },
    }


async def test_get_settings(fleet_v1):
    response = await fleet_v1.get_park_check_settings(park_id=PARK_ID)
    assert response.status_code == 200, response.text
    assert response.json() == {
        'cost_max': '1000',
        'duration_max': 1000,
        'cost_per_min_max': '100',
        'duration_min': 100,
        'tips_max': '100',
        'bonus_max': '100',
    }


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'query, expected_response, expected_total',
    [
        (
            {'limit': 10, 'query': {}},
            [
                {
                    'id': '00000000-0000-0000-0000-000000000006',
                    'order_id': 'ORDER-01',
                    'short_id': 111,
                    'address_from': 'FROM',
                    'address_to': 'TO',
                    'ended_at': '2020-01-01T00:00:05+00:00',
                    'blocked_money': '1000',
                    'contractor_id': 'CONTRACTOR-03',
                    'contractor_name': 'Contractor 3',
                    'reason': 'duration_max',
                    'metric': {
                        'kind': 'duration',
                        'factual': 10,
                        'threshold': 1000,
                    },
                },
                {
                    'id': '00000000-0000-0000-0000-000000000003',
                    'order_id': 'ORDER-01',
                    'short_id': 111,
                    'address_from': 'FROM',
                    'address_to': 'TO',
                    'ended_at': '2020-01-01T00:00:02+00:00',
                    'blocked_money': '100',
                    'contractor_id': 'CONTRACTOR-02',
                    'contractor_name': 'Contractor 2',
                    'reason': 'tips',
                    'metric': {
                        'kind': 'money',
                        'factual': '100',
                        'threshold': '100',
                    },
                },
                {
                    'id': '00000000-0000-0000-0000-000000000002',
                    'ended_at': '2020-01-01T00:00:01+00:00',
                    'blocked_money': '100',
                    'contractor_id': 'CONTRACTOR-01',
                    'contractor_name': 'Contractor 1',
                    'reason': 'tips',
                    'metric': {
                        'kind': 'money',
                        'factual': '100',
                        'threshold': '100',
                    },
                },
                {
                    'id': '00000000-0000-0000-0000-000000000001',
                    'order_id': 'ORDER-01',
                    'short_id': 111,
                    'address_from': 'FROM',
                    'address_to': 'TO',
                    'ended_at': '2020-01-01T00:00:00+00:00',
                    'blocked_money': '1000',
                    'contractor_id': 'CONTRACTOR-01',
                    'contractor_name': 'Contractor 1',
                    'reason': 'cost_max',
                    'metric': {
                        'kind': 'money',
                        'factual': '1000',
                        'threshold': '1000',
                    },
                },
            ],
            4,
        ),
        (
            {'limit': 1, 'offset': 1, 'query': {}},
            [
                {
                    'id': '00000000-0000-0000-0000-000000000003',
                    'order_id': 'ORDER-01',
                    'short_id': 111,
                    'address_from': 'FROM',
                    'address_to': 'TO',
                    'ended_at': '2020-01-01T00:00:02+00:00',
                    'blocked_money': '100',
                    'contractor_id': 'CONTRACTOR-02',
                    'contractor_name': 'Contractor 2',
                    'reason': 'tips',
                    'metric': {
                        'kind': 'money',
                        'factual': '100',
                        'threshold': '100',
                    },
                },
            ],
            4,
        ),
        (
            {'limit': 10, 'query': {'contractor_id': 'CONTRACTOR-02'}},
            [
                {
                    'id': '00000000-0000-0000-0000-000000000003',
                    'order_id': 'ORDER-01',
                    'short_id': 111,
                    'address_from': 'FROM',
                    'address_to': 'TO',
                    'ended_at': '2020-01-01T00:00:02+00:00',
                    'blocked_money': '100',
                    'contractor_id': 'CONTRACTOR-02',
                    'contractor_name': 'Contractor 2',
                    'reason': 'tips',
                    'metric': {
                        'kind': 'money',
                        'factual': '100',
                        'threshold': '100',
                    },
                },
            ],
            1,
        ),
        (
            {'limit': 10, 'query': {'reasons': ['cost_max']}},
            [
                {
                    'id': '00000000-0000-0000-0000-000000000001',
                    'order_id': 'ORDER-01',
                    'short_id': 111,
                    'address_from': 'FROM',
                    'address_to': 'TO',
                    'ended_at': '2020-01-01T00:00:00+00:00',
                    'blocked_money': '1000',
                    'contractor_id': 'CONTRACTOR-01',
                    'contractor_name': 'Contractor 1',
                    'reason': 'cost_max',
                    'metric': {
                        'kind': 'money',
                        'factual': '1000',
                        'threshold': '1000',
                    },
                },
            ],
            1,
        ),
    ],
)
async def test_get_suspicious(
        fleet_v1, mock_api, query, expected_response, expected_total,
):
    response = await fleet_v1.retrieve_suspicious(park_id=PARK_ID, json=query)
    assert response.status_code == 200, response.text
    assert response.json()['orders'] == expected_response
    assert response.json()['total'] == expected_total


@pytest.mark.now(NOW)
async def test_approve(fleet_v1, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v1.approve_suspicious_orders(
        park_id=PARK_ID,
        json={
            'ids': [
                '00000000-0000-0000-0000-000000000001',
                '00000000-0000-0000-0000-000000000002',
                '00000000-0000-0000-0000-000000000003',
            ],
        },
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'approve_suspicious',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'park_check_suspicious': {
            **pg_initial['park_check_suspicious'],
            ('PARK-01', 'CONTRACTOR-01', 'ORDER-01', None): (
                'cost_max',
                1000,
                None,
                dateutil.parser.parse('2020-01-01T03:00:00+03:00'),
                dateutil.parser.parse('2020-01-02T03:00:00+03:00'),
                None,
                1,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                2,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
            ),
            ('PARK-01', 'CONTRACTOR-01', None, '1'): (
                'tips',
                100,
                None,
                dateutil.parser.parse('2020-01-01T03:00:01+03:00'),
                dateutil.parser.parse('2020-01-02T03:00:00+03:00'),
                100,
                1,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                2,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
            ),
            ('PARK-01', 'CONTRACTOR-02', 'ORDER-01', '1'): (
                'tips',
                100,
                None,
                dateutil.parser.parse('2020-01-01T03:00:02+03:00'),
                dateutil.parser.parse('2020-01-02T03:00:00+03:00'),
                100,
                1,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                2,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_approve_idempotency(fleet_v1, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v1.approve_suspicious_orders(
        park_id=PARK_ID,
        json={
            'ids': [
                '00000000-0000-0000-0000-000000000001',
                '00000000-0000-0000-0000-000000000004',
            ],
        },
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'approve_suspicious',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'park_check_suspicious': {
            **pg_initial['park_check_suspicious'],
            ('PARK-01', 'CONTRACTOR-01', 'ORDER-01', None): (
                'cost_max',
                1000,
                None,
                dateutil.parser.parse('2020-01-01T03:00:00+03:00'),
                dateutil.parser.parse('2020-01-02T03:00:00+03:00'),
                None,
                1,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                2,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_approve_nonexistant(fleet_v1, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v1.approve_suspicious_orders(
        park_id=PARK_ID,
        json={
            'ids': [
                '00000000-0000-0000-0000-000000000001',
                '00000000-1111-0000-0000-000000000001',
            ],
        },
    )
    assert response.status_code == 400, response.text

    assert pg_dump() == pg_initial


@pytest.mark.config(
    FLEET_ANTIFRAUD_PARK_CHECK={
        'is_enabled': True,
        'expiring_interval': 86400,
        'billing_fetching_overlap': 3600,
    },
)
@pytest.mark.now(NOW)
async def test_get_blocked_balance(fleet_v1):
    response = await fleet_v1.get_blocked_balance(
        park_id=PARK_ID, contractor_id='CONTRACTOR-02',
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'blocked_balance': '100'}


@pytest.mark.config(
    FLEET_ANTIFRAUD_PARK_CHECK={
        'is_enabled': True,
        'expiring_interval': 86400,
        'billing_fetching_overlap': 3600,
    },
)
@pytest.mark.now(NOW)
async def test_instant_payout_get_blocked_balance(fleet_v1):
    response = await fleet_v1.ip_get_blocked_balance(
        park_id=PARK_ID, contractor_id='CONTRACTOR-02',
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'blocked_balance': '100'}


@pytest.mark.now(NOW)
async def test_instant_payout_approve(fleet_v1, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v1.ip_approve_suspicious_orders(
        park_id=PARK_ID,
        json={
            'ids': [
                '00000000-0000-0000-0000-000000000001',
                '00000000-0000-0000-0000-000000000002',
                '00000000-0000-0000-0000-000000000003',
            ],
        },
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'approve_suspicious',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'park_check_suspicious': {
            **pg_initial['park_check_suspicious'],
            ('PARK-01', 'CONTRACTOR-01', 'ORDER-01', None): (
                'cost_max',
                1000,
                None,
                dateutil.parser.parse('2020-01-01T03:00:00+03:00'),
                dateutil.parser.parse('2020-01-02T03:00:00+03:00'),
                None,
                1,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                2,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
            ),
            ('PARK-01', 'CONTRACTOR-01', None, '1'): (
                'tips',
                100,
                None,
                dateutil.parser.parse('2020-01-01T03:00:01+03:00'),
                dateutil.parser.parse('2020-01-02T03:00:00+03:00'),
                100,
                1,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                2,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
            ),
            ('PARK-01', 'CONTRACTOR-02', 'ORDER-01', '1'): (
                'tips',
                100,
                None,
                dateutil.parser.parse('2020-01-01T03:00:02+03:00'),
                dateutil.parser.parse('2020-01-02T03:00:00+03:00'),
                100,
                1,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                2,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_instant_payout_approve_idempotency(fleet_v1, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v1.ip_approve_suspicious_orders(
        park_id=PARK_ID,
        json={
            'ids': [
                '00000000-0000-0000-0000-000000000001',
                '00000000-0000-0000-0000-000000000004',
            ],
        },
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'approve_suspicious',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'park_check_suspicious': {
            **pg_initial['park_check_suspicious'],
            ('PARK-01', 'CONTRACTOR-01', 'ORDER-01', None): (
                'cost_max',
                1000,
                None,
                dateutil.parser.parse('2020-01-01T03:00:00+03:00'),
                dateutil.parser.parse('2020-01-02T03:00:00+03:00'),
                None,
                1,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                2,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_instant_payout_approve_nonexistant(fleet_v1, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v1.ip_approve_suspicious_orders(
        park_id=PARK_ID,
        json={
            'ids': [
                '00000000-0000-0000-0000-000000000001',
                '00000000-1111-0000-0000-000000000001',
            ],
        },
    )
    assert response.status_code == 400, response.text

    assert pg_dump() == pg_initial


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'query, expected_response, expected_total',
    [
        (
            {'limit': 10, 'query': {}},
            [
                {
                    'id': '00000000-0000-0000-0000-000000000006',
                    'order_id': 'ORDER-01',
                    'short_id': 111,
                    'address_from': 'FROM',
                    'address_to': 'TO',
                    'ended_at': '2020-01-01T00:00:05+00:00',
                    'blocked_money': '1000',
                    'contractor_id': 'CONTRACTOR-03',
                    'contractor_name': 'Contractor 3',
                    'reason': 'duration_max',
                    'metric': {
                        'kind': 'duration',
                        'factual': 10,
                        'threshold': 1000,
                    },
                },
                {
                    'id': '00000000-0000-0000-0000-000000000003',
                    'order_id': 'ORDER-01',
                    'short_id': 111,
                    'address_from': 'FROM',
                    'address_to': 'TO',
                    'ended_at': '2020-01-01T00:00:02+00:00',
                    'blocked_money': '100',
                    'contractor_id': 'CONTRACTOR-02',
                    'contractor_name': 'Contractor 2',
                    'reason': 'tips',
                    'metric': {
                        'kind': 'money',
                        'factual': '100',
                        'threshold': '100',
                    },
                },
                {
                    'id': '00000000-0000-0000-0000-000000000002',
                    'ended_at': '2020-01-01T00:00:01+00:00',
                    'blocked_money': '100',
                    'contractor_id': 'CONTRACTOR-01',
                    'contractor_name': 'Contractor 1',
                    'reason': 'tips',
                    'metric': {
                        'kind': 'money',
                        'factual': '100',
                        'threshold': '100',
                    },
                },
                {
                    'id': '00000000-0000-0000-0000-000000000001',
                    'order_id': 'ORDER-01',
                    'short_id': 111,
                    'address_from': 'FROM',
                    'address_to': 'TO',
                    'ended_at': '2020-01-01T00:00:00+00:00',
                    'blocked_money': '1000',
                    'contractor_id': 'CONTRACTOR-01',
                    'contractor_name': 'Contractor 1',
                    'reason': 'cost_max',
                    'metric': {
                        'kind': 'money',
                        'factual': '1000',
                        'threshold': '1000',
                    },
                },
            ],
            4,
        ),
        (
            {'limit': 1, 'offset': 1, 'query': {}},
            [
                {
                    'id': '00000000-0000-0000-0000-000000000003',
                    'order_id': 'ORDER-01',
                    'short_id': 111,
                    'address_from': 'FROM',
                    'address_to': 'TO',
                    'ended_at': '2020-01-01T00:00:02+00:00',
                    'blocked_money': '100',
                    'contractor_id': 'CONTRACTOR-02',
                    'contractor_name': 'Contractor 2',
                    'reason': 'tips',
                    'metric': {
                        'kind': 'money',
                        'factual': '100',
                        'threshold': '100',
                    },
                },
            ],
            4,
        ),
        (
            {'limit': 10, 'query': {'contractor_id': 'CONTRACTOR-02'}},
            [
                {
                    'id': '00000000-0000-0000-0000-000000000003',
                    'order_id': 'ORDER-01',
                    'short_id': 111,
                    'address_from': 'FROM',
                    'address_to': 'TO',
                    'ended_at': '2020-01-01T00:00:02+00:00',
                    'blocked_money': '100',
                    'contractor_id': 'CONTRACTOR-02',
                    'contractor_name': 'Contractor 2',
                    'reason': 'tips',
                    'metric': {
                        'kind': 'money',
                        'factual': '100',
                        'threshold': '100',
                    },
                },
            ],
            1,
        ),
        (
            {'limit': 10, 'query': {'reasons': ['cost_max']}},
            [
                {
                    'id': '00000000-0000-0000-0000-000000000001',
                    'order_id': 'ORDER-01',
                    'short_id': 111,
                    'address_from': 'FROM',
                    'address_to': 'TO',
                    'ended_at': '2020-01-01T00:00:00+00:00',
                    'blocked_money': '1000',
                    'contractor_id': 'CONTRACTOR-01',
                    'contractor_name': 'Contractor 1',
                    'reason': 'cost_max',
                    'metric': {
                        'kind': 'money',
                        'factual': '1000',
                        'threshold': '1000',
                    },
                },
            ],
            1,
        ),
    ],
)
async def test_instant_payout_get_suspicious(
        fleet_v1, mock_api, query, expected_response, expected_total,
):
    response = await fleet_v1.ip_retrieve_suspicious(
        park_id=PARK_ID, json=query,
    )
    assert response.status_code == 200, response.text
    assert response.json()['orders'] == expected_response
    assert response.json()['total'] == expected_total


async def test_instant_payout_get_settings(fleet_v1):
    response = await fleet_v1.ip_get_park_check_settings(park_id=PARK_ID)
    assert response.status_code == 200, response.text
    assert response.json() == {
        'cost_max': '1000',
        'duration_max': 1000,
        'cost_per_min_max': '100',
        'duration_min': 100,
        'tips_max': '100',
        'bonus_max': '100',
    }


@pytest.mark.now(NOW)
async def test_instant_payout_put_settings(fleet_v1, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v1.ip_change_park_check_settings(
        park_id=PARK_ID,
        json={'cost_max': '10000', 'duration_min': 5, 'tips_max': '50'},
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'set_park_check_settings',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'park_check_settings': {
            **pg_initial['park_check_settings'],
            1: (
                'PARK-01',
                1,
                dateutil.parser.parse(NOW),
                decimal.Decimal('10000'),
                None,
                None,
                datetime.timedelta(seconds=5),
                decimal.Decimal('50'),
                None,
            ),
        },
    }
