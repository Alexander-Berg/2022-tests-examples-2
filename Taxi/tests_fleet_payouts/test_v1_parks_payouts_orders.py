import copy
import typing

import pytest

from tests_fleet_payouts.utils import pg
from tests_fleet_payouts.utils import xcmp


DEFAULT_CONFIG = {
    'FLEET_PAYOUTS_WITHDRAWAL_RULES': [
        {
            'condition': {
                'clid': ['CLID00', 'CLID01', 'CLID02'],
                'fleet_version': ['basic'],
            },
            'definition': {'enable_requests': True},
        },
        {
            'condition': {
                'clid': ['CLID00', 'CLID01', 'CLID02'],
                'fleet_version': ['simple'],
            },
            'definition': {'enable_requests': False},
        },
    ],
}

DEFAULT_REQUEST: typing.Dict[str, typing.Any] = {
    'path': 'v1/parks/payouts/orders',
    'params': {'park_id': '00000000000000000000000000000000'},
    'headers': {
        'X-Yandex-UID': '1000',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
        'X-Idempotency-Token': 'TESTSUITE-IDEMPOTENCY-TOKEN',
    },
    'json': {
        'balance_id': '75054400',
        'entries': [
            {'contract_id': '278761', 'amount': '4232.21', 'currency': 'RUB'},
            {'contract_id': '656839', 'amount': '423.21', 'currency': 'EUR'},
            {'contract_id': '679178', 'amount': '703.0', 'currency': 'EUR'},
            {'contract_id': '844463', 'amount': '19660.8', 'currency': 'RUB'},
        ],
    },
}

DEFAULT_REQUEST_ENTRIES = DEFAULT_REQUEST['json']['entries']


async def test_non_production_park(taxi_fleet_payouts, mock_users, mock_parks):
    response = await taxi_fleet_payouts.post(
        'v1/parks/payouts/orders',
        params={'park_id': '22222222222222222222222222222222'},
        headers={
            'X-Yandex-UID': '1200',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
            'X-Idempotency-Token': 'TESTSUITE-IDEMPOTENCY-TOKEN',
        },
        json={
            'balance_id': '75054400',
            'entries': [
                {
                    'contract_id': '285703',
                    'amount': '11701.32',
                    'currency': 'RUB',
                },
            ],
        },
    )
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'Park must be of type production.',
    }


async def test_non_configured_park(taxi_fleet_payouts, mock_users, mock_parks):
    response = await taxi_fleet_payouts.post(**DEFAULT_REQUEST)
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'Park must be configured to perform this operation.',
    }


async def test_non_park_user(taxi_fleet_payouts, mock_users, mock_parks):
    request = copy.deepcopy(DEFAULT_REQUEST)
    request['headers']['X-Yandex-UID'] = '9999'

    response = await taxi_fleet_payouts.post(**request)
    assert response.status_code == 403, response.text
    assert response.json() == {'code': '403', 'message': 'User not found.'}


async def test_non_park_super_user(taxi_fleet_payouts, mock_users, mock_parks):
    request = copy.deepcopy(DEFAULT_REQUEST)
    request['headers']['X-Yandex-UID'] = '1001'

    response = await taxi_fleet_payouts.post(**request)
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'User must be the super user of this park.',
    }


async def test_yandex_team_user(taxi_fleet_payouts, mock_users, mock_parks):
    request = copy.deepcopy(DEFAULT_REQUEST)
    request['headers']['X-Yandex-UID'] = '9999'
    request['headers']['X-Ya-User-Ticket-Provider'] = 'yandex_team'

    response = await taxi_fleet_payouts.post(**request)
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'User must be the super user of this park.',
    }


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'simple_fleet_version.sql'],
)
@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_simple_fleet_version(
        taxi_fleet_payouts, mock_users, mock_parks,
):
    response = await taxi_fleet_payouts.post(**DEFAULT_REQUEST)
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'Park must be configured to perform this operation.',
    }


@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_invalid_balance_id(taxi_fleet_payouts, mock_users, mock_parks):
    request = copy.deepcopy(DEFAULT_REQUEST)
    request['json']['balance_id'] = '99999999'

    response = await taxi_fleet_payouts.post(**request)
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': 'Invalid balance id.'}


@pytest.mark.parametrize(
    'data',
    [
        (
            [
                *DEFAULT_REQUEST_ENTRIES,
                {
                    'contract_id': '999999',
                    'amount': '999.99',
                    'currency': 'RUB',
                },
            ],
            'Unexpected payment entry with contract id \'999999\'.',
        ),
        (
            [*DEFAULT_REQUEST_ENTRIES, DEFAULT_REQUEST_ENTRIES[0]],
            'Duplicated payment entry with contract id \'278761\'.',
        ),
        (
            DEFAULT_REQUEST_ENTRIES[1:],
            'Missed payment entry with contract id \'278761\'.',
        ),
        (
            [
                *DEFAULT_REQUEST_ENTRIES,
                {
                    'contract_id': '253207',
                    'amount': '45332.88',
                    'currency': 'RUB',
                },
            ],
            # reject_code is not null
            'Unexpected payment entry with contract id \'253207\'.',
        ),
        (
            [
                *DEFAULT_REQUEST_ENTRIES,
                {'contract_id': '295059', 'amount': '0.0', 'currency': 'RUB'},
            ],
            # amount = 0
            'Unexpected payment entry with contract id \'295059\'.',
        ),
        (
            [
                *DEFAULT_REQUEST_ENTRIES,
                {
                    'contract_id': '279770',
                    'amount': '24421.24',
                    'currency': 'RUB',
                },
            ],
            # amount < contract_limit
            'Unexpected payment entry with contract id \'279770\'.',
        ),
        (
            [
                {**DEFAULT_REQUEST_ENTRIES[0], 'amount': '0.00'},
                *DEFAULT_REQUEST_ENTRIES[1:],
            ],
            'Payment amount mismatch.',
        ),
        (
            [
                *DEFAULT_REQUEST_ENTRIES[:3],
                {**DEFAULT_REQUEST_ENTRIES[3], 'amount': '749.00'},
            ],
            'Payment amount mismatch.',
        ),
        (
            [
                {**DEFAULT_REQUEST_ENTRIES[0], 'amount': '4300.00'},
                *DEFAULT_REQUEST_ENTRIES[1:],
            ],
            'Payment amount mismatch.',
        ),
        (
            [
                {**DEFAULT_REQUEST_ENTRIES[0], 'amount': '4000.00'},
                *DEFAULT_REQUEST_ENTRIES[1:],
            ],
            'Payment amount mismatch.',
        ),
        (
            [
                {**DEFAULT_REQUEST_ENTRIES[0], 'currency': 'EUR'},
                *DEFAULT_REQUEST_ENTRIES[1:],
            ],
            'Payment currency mismatch.',
        ),
    ],
)
@pytest.mark.pgsql('fleet_payouts', files=['balances.sql'])
@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_invalid_entries(
        taxi_fleet_payouts, mock_users, mock_parks, mock_docs_select, data,
):
    request = copy.deepcopy(DEFAULT_REQUEST)
    request['json']['entries'] = data[0]

    response = await taxi_fleet_payouts.post(**request)
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': data[1]}


@pytest.mark.pgsql('fleet_payouts', files=['balances.sql'])
@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_correct_data(taxi_fleet_payouts, mock_users, mock_parks, pgsql):
    response = await taxi_fleet_payouts.post(**DEFAULT_REQUEST)
    assert response.status_code == 200, response.text
    assert response.json() == {}

    # Must not change for fixed request.
    payment_id = 'CLID00_75054400_a85b0e2c'

    assert pg.dump_payments(pgsql) == {
        payment_id: {
            'payment_id': payment_id,
            'clid': 'CLID00',
            'balance_id': '75054400',
            'created_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
            'origin': 'requested',
            'status': 'created',
            'doc_id': None,
        },
    }
    assert pg.dump_payment_entries(pgsql) == {
        (payment_id, '278761'): {
            'payment_id': payment_id,
            'contract_id': '278761',
            'bcid': '32511442',
            'amount': xcmp.Decimal('4232.21'),
            'currency': 'RUB',
            'status_code': None,
            'status_message': None,
            'reject_code': None,
            'reject_message': None,
        },
        (payment_id, '656839'): {
            'payment_id': payment_id,
            'contract_id': '656839',
            'bcid': '55966500',
            'amount': xcmp.Decimal('423.21'),
            'currency': 'EUR',
            'status_code': None,
            'status_message': None,
            'reject_code': None,
            'reject_message': None,
        },
        (payment_id, '679178'): {
            'payment_id': payment_id,
            'contract_id': '679178',
            'bcid': '32511442',
            'amount': xcmp.Decimal('703.0'),
            'currency': 'EUR',
            'status_code': None,
            'status_message': None,
            'reject_code': None,
            'reject_message': None,
        },
        (payment_id, '844463'): {
            'payment_id': payment_id,
            'contract_id': '844463',
            'bcid': '30429664',
            'amount': xcmp.Decimal('19660.8'),
            'currency': 'RUB',
            'status_code': None,
            'status_message': None,
            'reject_code': None,
            'reject_message': None,
        },
    }


@pytest.mark.pgsql('fleet_payouts', files=['balances.sql'])
@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_idempotency(taxi_fleet_payouts, mock_users, mock_parks):
    response = await taxi_fleet_payouts.post(**DEFAULT_REQUEST)
    assert response.status_code == 200, response.text
    assert response.json() == {}

    response = await taxi_fleet_payouts.post(**DEFAULT_REQUEST)
    assert response.status_code == 200, response.text
    assert response.json() == {}


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'another_with_same_balance.sql'],
)
@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_another_with_same_balance(
        taxi_fleet_payouts, mock_users, mock_parks,
):
    response = await taxi_fleet_payouts.post(**DEFAULT_REQUEST)
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': 'Another payment exists with same balance id.',
    }


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'another_created.sql'],
)
@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_another_created(taxi_fleet_payouts, mock_users, mock_parks):
    response = await taxi_fleet_payouts.post(**DEFAULT_REQUEST)
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': 'Another pending payment exists.',
    }


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'another_pending.sql'],
)
@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_another_pending(taxi_fleet_payouts, mock_users, mock_parks):
    response = await taxi_fleet_payouts.post(**DEFAULT_REQUEST)
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': 'Another pending payment exists.',
    }
