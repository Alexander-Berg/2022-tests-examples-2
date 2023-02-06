import decimal

import dateutil
import pytest


NOW = '2020-01-01T20:00:00+03:00'


async def test_get_rule(fleet_v2):
    response = await fleet_v2.get_rule(
        park_id='PARK-01', rule_id='00000000-0000-0000-0000-000000000003',
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'is_enabled': True,
        'name': 'Rule 3',
        'withdrawal_minimum': '500.0005',
        'withdrawal_maximum': '5000.0005',
        'withdrawal_daily_maximum': '50000.0005',
        'fee_percent': '55.55',
        'fee_minimum': '50.0005',
        'balance_minimum': '500.0005',
        'is_default': False,
    }


async def test_get_rule_list__empty(fleet_v2):
    response = await fleet_v2.get_rule_list(park_id='PARK-XX')
    assert response.status_code == 200, response.text
    assert response.json() == {'items': []}


async def test_get_rule_list__1st_park(fleet_v2):
    response = await fleet_v2.get_rule_list(park_id='PARK-01')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'items': [
            {
                'id': '00000000-0000-0000-0000-000000000003',
                'created_at': '2020-01-01T13:00:00+00:00',
                'updated_at': '2020-01-01T13:00:00+00:00',
                'is_enabled': True,
                'name': 'Rule 3',
                'withdrawal_minimum': '500.0005',
                'withdrawal_maximum': '5000.0005',
                'withdrawal_daily_maximum': '50000.0005',
                'fee_percent': '55.55',
                'fee_minimum': '50.0005',
                'balance_minimum': '500.0005',
                'is_default': False,
            },
            {
                'id': '00000000-0000-0000-0000-000000000001',
                'created_at': '2020-01-01T09:00:00+00:00',
                'updated_at': '2020-01-01T09:00:00+00:00',
                'is_enabled': False,
                'name': 'Rule 1',
                'withdrawal_minimum': '100.0001',
                'withdrawal_maximum': '1000.0001',
                'withdrawal_daily_maximum': '10000.0001',
                'fee_percent': '11.11',
                'fee_minimum': '10.0001',
                'balance_minimum': '100.0001',
                'is_default': False,
            },
        ],
    }


async def test_get_rule_list__2nd_park(fleet_v2):
    response = await fleet_v2.get_rule_list(park_id='PARK-02')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'items': [
            {
                'id': '00000000-0000-0000-0000-000000000003',
                'created_at': '2020-01-01T10:00:00+00:00',
                'updated_at': '2020-01-01T10:00:00+00:00',
                'is_enabled': True,
                'name': 'Rule 3',
                'withdrawal_minimum': '600.0006',
                'withdrawal_maximum': '6000.0006',
                'withdrawal_daily_maximum': '60000.0006',
                'fee_percent': '66.66',
                'fee_minimum': '60.0006',
                'balance_minimum': '600.0006',
                'is_default': False,
            },
            {
                'id': '00000000-0000-0000-0000-000000000001',
                'created_at': '2020-01-01T10:00:00+00:00',
                'updated_at': '2020-01-01T10:00:00+00:00',
                'is_enabled': True,
                'name': 'Rule 1',
                'withdrawal_minimum': '200.0002',
                'withdrawal_maximum': '2000.0002',
                'withdrawal_daily_maximum': '20000.0002',
                'fee_percent': '22.22',
                'fee_minimum': '20.0002',
                'balance_minimum': '200.0002',
                'is_default': True,
            },
        ],
    }


@pytest.mark.now(NOW)
async def test_create_rule__success(fleet_v2, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.create_rule(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-000000000009',
            'name': 'New Rule',
            'withdrawal_minimum': '900.0009',
            'withdrawal_maximum': '9000.0009',
            'withdrawal_daily_maximum': '90000.0009',
            'fee_percent': '99.99',
            'fee_minimum': '90.0009',
            'balance_minimum': '900.0009',
            'is_default': True,
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
                'create_rule',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'rule': {
            **pg_initial['rule'],
            1: (
                0,
                1,
                dateutil.parser.parse(NOW),
                1,
                dateutil.parser.parse(NOW),
                'PARK-01',
                '00000000-0000-0000-0000-000000000009',
                False,
                True,
                'New Rule',
                decimal.Decimal('900.0009'),
                decimal.Decimal('9000.0009'),
                decimal.Decimal('90000.0009'),
                decimal.Decimal('0.9999'),
                decimal.Decimal('90.0009'),
                decimal.Decimal('900.0009'),
                True,
            ),
        },
        'rule_change_log': {
            (1, 0): (
                1,
                dateutil.parser.parse(NOW),
                None,
                False,
                None,
                True,
                None,
                'New Rule',
                None,
                decimal.Decimal('900.0009'),
                None,
                decimal.Decimal('9000.0009'),
                None,
                decimal.Decimal('90000.0009'),
                None,
                decimal.Decimal('0.9999'),
                None,
                decimal.Decimal('90.0009'),
                None,
                decimal.Decimal('900.0009'),
                None,
                True,
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_create_rule__change_default(fleet_v2, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.create_rule(
        park_id='PARK-02',
        json={
            'id': '00000000-0000-0000-0000-000000000004',
            'name': 'Default Rule',
            'withdrawal_minimum': '300.0003',
            'withdrawal_maximum': '3000.0003',
            'withdrawal_daily_maximum': '30000.0003',
            'fee_percent': '33.33',
            'fee_minimum': '30.0003',
            'balance_minimum': '300.0003',
            'is_default': True,
        },
    )

    assert response.status_code == 204, response.text

    print(pg_dump()['rule'][1])

    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'create_rule',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'rule': {
            **pg_initial['rule'],
            1: (
                0,
                1,
                dateutil.parser.parse(NOW),
                1,
                dateutil.parser.parse(NOW),
                'PARK-02',
                '00000000-0000-0000-0000-000000000004',
                False,
                True,
                'Default Rule',
                decimal.Decimal('300.0003'),
                decimal.Decimal('3000.0003'),
                decimal.Decimal('30000.0003'),
                decimal.Decimal('0.3333'),
                decimal.Decimal('30.0003'),
                decimal.Decimal('300.0003'),
                True,
            ),
            102: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T13:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'PARK-02',
                '00000000-0000-0000-0000-000000000001',
                False,
                True,
                'Rule 1',
                decimal.Decimal('200.0002'),
                decimal.Decimal('2000.0002'),
                decimal.Decimal('20000.0002'),
                decimal.Decimal('0.2222'),
                decimal.Decimal('20.0002'),
                decimal.Decimal('200.0002'),
                False,
            ),
        },
        'rule_change_log': {
            (1, 0): (
                1,
                dateutil.parser.parse(NOW),
                None,
                False,
                None,
                True,
                None,
                'Default Rule',
                None,
                decimal.Decimal('300.0003'),
                None,
                decimal.Decimal('3000.0003'),
                None,
                decimal.Decimal('30000.0003'),
                None,
                decimal.Decimal('0.3333'),
                None,
                decimal.Decimal('30.0003'),
                None,
                decimal.Decimal('300.0003'),
                None,
                True,
            ),
            (102, 1): (
                1,
                dateutil.parser.parse(NOW),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                True,
                False,
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_create_rule__idempotency(fleet_v2, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.create_rule(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-000000000001',
            'name': 'Rule 1',
            'withdrawal_minimum': '100.0001',
            'withdrawal_maximum': '1000.0001',
            'withdrawal_daily_maximum': '10000.0001',
            'fee_percent': '11.11',
            'fee_minimum': '10.0001',
            'balance_minimum': '100.0001',
        },
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == pg_initial, 'Nothing was expected to change'


@pytest.mark.now(NOW)
async def test_create_rule__already_exists(fleet_v2, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.create_rule(
        park_id='PARK-01',
        json={
            'id': '00000000-0000-0000-0000-000000000001',
            'name': 'Rule 1',
            'withdrawal_minimum': '100.0002',  # 100.0001 in exisitng rule
            'withdrawal_maximum': '1000.0001',
            'withdrawal_daily_maximum': '10000.0001',
            'fee_percent': '11.11',
            'fee_minimum': '10.0001',
            'balance_minimum': '100.0001',
        },
    )
    assert response.status_code == 409, response.text
    assert response.json() == {
        'code': 'already_exists',
        'message': (
            'Another rule has already been created with the specified '
            'identifier.'
        ),
    }

    assert pg_dump() == pg_initial, 'Nothing was expected to change'


@pytest.mark.now(NOW)
async def test_update_rule__success(fleet_v2, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.update_rule(
        park_id='PARK-01',
        rule_id='00000000-0000-0000-0000-000000000001',
        json={
            'is_enabled': True,
            'name': 'Rule 9',
            'withdrawal_minimum': '900.0009',
            'withdrawal_maximum': '9000.0009',
            'withdrawal_daily_maximum': '90000.0009',
            'fee_percent': '99.99',
            'fee_minimum': '90.0009',
            'balance_minimum': '900.0009',
            'is_default': True,
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
                'update_rule',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'rule': {
            **pg_initial['rule'],
            101: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                False,
                True,
                'Rule 9',
                decimal.Decimal('900.0009'),
                decimal.Decimal('9000.0009'),
                decimal.Decimal('90000.0009'),
                decimal.Decimal('0.9999'),
                decimal.Decimal('90.0009'),
                decimal.Decimal('900.0009'),
                True,
            ),
        },
        'rule_change_log': {
            **pg_initial['rule_change_log'],
            (101, 1): (
                1,
                dateutil.parser.parse(NOW),
                None,
                None,
                False,
                True,
                'Rule 1',
                'Rule 9',
                decimal.Decimal('100.0001'),
                decimal.Decimal('900.0009'),
                decimal.Decimal('1000.0001'),
                decimal.Decimal('9000.0009'),
                decimal.Decimal('10000.0001'),
                decimal.Decimal('90000.0009'),
                decimal.Decimal('0.1111'),
                decimal.Decimal('0.9999'),
                decimal.Decimal('10.0001'),
                decimal.Decimal('90.0009'),
                decimal.Decimal('100.0001'),
                decimal.Decimal('900.0009'),
                False,
                True,
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_update_rule__change_default(fleet_v2, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.update_rule(
        park_id='PARK-02',
        rule_id='00000000-0000-0000-0000-000000000003',
        json={
            'name': 'Rule Default',
            'withdrawal_minimum': '100.0001',
            'withdrawal_maximum': '1000.0001',
            'withdrawal_daily_maximum': '10000.0001',
            'fee_percent': '11.11',
            'fee_minimum': '10.0001',
            'balance_minimum': '100.0001',
            'is_default': True,
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
                'update_rule',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'rule': {
            **pg_initial['rule'],
            102: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T13:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'PARK-02',
                '00000000-0000-0000-0000-000000000001',
                False,
                True,
                'Rule 1',
                decimal.Decimal('200.0002'),
                decimal.Decimal('2000.0002'),
                decimal.Decimal('20000.0002'),
                decimal.Decimal('0.2222'),
                decimal.Decimal('20.0002'),
                decimal.Decimal('200.0002'),
                False,
            ),
            106: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T13:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'PARK-02',
                '00000000-0000-0000-0000-000000000003',
                False,
                True,
                'Rule Default',
                decimal.Decimal('100.0001'),
                decimal.Decimal('1000.0001'),
                decimal.Decimal('10000.0001'),
                decimal.Decimal('0.1111'),
                decimal.Decimal('10.0001'),
                decimal.Decimal('100.0001'),
                True,
            ),
        },
        'rule_change_log': {
            **pg_initial['rule_change_log'],
            (106, 1): (
                1,
                dateutil.parser.parse(NOW),
                None,
                None,
                None,
                None,
                'Rule 3',
                'Rule Default',
                decimal.Decimal('600.0006'),
                decimal.Decimal('100.0001'),
                decimal.Decimal('6000.0006'),
                decimal.Decimal('1000.0001'),
                decimal.Decimal('60000.0006'),
                decimal.Decimal('10000.0001'),
                decimal.Decimal('0.6666'),
                decimal.Decimal('0.1111'),
                decimal.Decimal('60.0006'),
                decimal.Decimal('10.0001'),
                decimal.Decimal('600.0006'),
                decimal.Decimal('100.0001'),
                False,
                True,
            ),
            (102, 1): (
                1,
                dateutil.parser.parse(NOW),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                True,
                False,
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_update_rule__idempotency(fleet_v2, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.update_rule(
        park_id='PARK-01',
        rule_id='00000000-0000-0000-0000-000000000001',
        json={
            'is_enabled': False,
            'name': 'Rule 1',
            'withdrawal_minimum': '100.0001',
            'withdrawal_maximum': '1000.0001',
            'withdrawal_daily_maximum': '10000.0001',
            'fee_percent': '11.11',
            'fee_minimum': '10.0001',
            'balance_minimum': '100.0001',
        },
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == pg_initial, 'Nothing was expected to change'


@pytest.mark.now(NOW)
async def test_delete_rule__success(fleet_v2, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.delete_rule(
        park_id='PARK-01', rule_id='00000000-0000-0000-0000-000000000001',
    )
    assert response.status_code == 204, response.text
    assert pg_dump() == {
        **pg_initial,
        'operation': {
            **pg_initial['operation'],
            1: (
                dateutil.parser.parse(NOW),
                dateutil.parser.parse(NOW),
                'delete_rule',
                'park',
                None,
                None,
                1000,
                'yandex',
            ),
        },
        'rule': {
            **pg_initial['rule'],
            101: (
                1,
                999,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                1,
                dateutil.parser.parse(NOW),
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                True,
                False,
                'Rule 1',
                decimal.Decimal('100.0001'),
                decimal.Decimal('1000.0001'),
                decimal.Decimal('10000.0001'),
                decimal.Decimal('0.1111'),
                decimal.Decimal('10.0001'),
                decimal.Decimal('100.0001'),
                False,
            ),
        },
        'rule_change_log': {
            **pg_initial['rule_change_log'],
            (101, 1): (
                1,
                dateutil.parser.parse(NOW),
                False,
                True,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
        },
    }


@pytest.mark.now(NOW)
async def test_delete_account__idempotency(fleet_v2, pg_dump):
    pg_initial = pg_dump()

    response = await fleet_v2.delete_rule(
        park_id='PARK-01', rule_id='00000000-0000-0000-0000-000000000002',
    )
    assert response.status_code == 204, response.text

    assert pg_dump() == pg_initial, 'Nothing was expected to change'


async def test_get_default_rule_exists(fleet_v2):
    response = await fleet_v2.get_default_rule(park_id='PARK-02')
    assert response.status_code == 200
    assert response.json()['rule'] == {
        'id': '00000000-0000-0000-0000-000000000001',
        'created_at': '2020-01-01T10:00:00+00:00',
        'updated_at': '2020-01-01T10:00:00+00:00',
        'is_enabled': True,
        'name': 'Rule 1',
        'withdrawal_minimum': '200.0002',
        'withdrawal_maximum': '2000.0002',
        'withdrawal_daily_maximum': '20000.0002',
        'fee_percent': '0.22',
        'fee_minimum': '20.0002',
        'balance_minimum': '200.0002',
        'is_default': True,
    }


async def test_get_default_rule_not_exists(fleet_v2):
    response = await fleet_v2.get_default_rule(park_id='PARK-01')
    assert response.status_code == 200
    assert response.json() == {}
