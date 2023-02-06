import contextlib
import copy
import typing

import pytest

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
    'path': 'v1/parks/payouts/status',
    'params': {'park_id': '00000000000000000000000000000000'},
    'headers': {
        'X-Yandex-UID': '1000',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
        'X-Idempotency-Token': 'TESTSUITE-IDEMPOTENCY-TOKEN',
    },
}

DEFAULT_RESPONSE: typing.Dict[str, typing.Any] = {
    'balance': {
        'balance_id': '75054400',
        'balance_date': xcmp.Date('2020-03-21T13:30:00+03:00'),
        'entries': [
            {
                'contract_id': '253207',
                'contract_type': 'PROMOCODES',
                'contract_alias': 'ОФ-34629/15',
                'contract_limit': xcmp.Decimal('10000.00'),
                'amount': xcmp.Decimal('45332.88'),
                'currency': 'RUB',
                'reject_code': 'N_CONTRACT_ORIGINAL_NOT_PRESENT',
                'reject_message': 'Отсутствует оригинал договора.',
            },
            {
                'contract_id': '278761',
                'contract_type': 'TAXI',
                'contract_alias': 'ОФ-63864/17',
                'contract_limit': xcmp.Decimal('0.00'),
                'amount': xcmp.Decimal('4232.21'),
                'currency': 'RUB',
            },
            {
                'contract_id': '279770',
                'contract_type': 'PROMOCODES',
                'contract_alias': 'ОФ-63287/17',
                'contract_limit': xcmp.Decimal('25000.00'),
                'amount': xcmp.Decimal('24421.24'),
                'currency': 'RUB',
            },
            {
                'contract_id': '295059',
                'contract_type': 'PROMOCODES',
                'contract_alias': 'ОФ-70254/17',
                'contract_limit': xcmp.Decimal('0.00'),
                'amount': xcmp.Decimal('0.00'),
                'currency': 'RUB',
            },
            {
                'contract_id': '323534',
                'contract_type': 'CORPORATE',
                'contract_alias': 'РАС-30788',
                'contract_limit': xcmp.Decimal('750.00'),
                'amount': xcmp.Decimal('6522.0'),
                'currency': 'RUB',
                'reject_code': 'N_DOCUMENT_ORIGINAL_NOT_PRESENT',
                'reject_message': (
                    'Отсутствуют оригиналы документов за предыдущие периоды.'
                ),
            },
            {
                'contract_id': '656839',
                'contract_type': 'TAXI',
                'contract_alias': 'ОФ-198875/19',
                'contract_limit': xcmp.Decimal('100.00'),
                'amount': xcmp.Decimal('423.21'),
                'currency': 'EUR',
            },
            {
                'contract_id': '679178',
                'contract_type': 'CORPORATE',
                'contract_alias': 'РАС-206300',
                'contract_limit': xcmp.Decimal('100.00'),
                'amount': xcmp.Decimal('703.0'),
                'currency': 'EUR',
            },
            {
                'contract_id': '732636',
                'contract_type': 'PROMOCODES',
                'contract_alias': 'ОФ-228369/19',
                'contract_limit': xcmp.Decimal('1500.00'),
                'amount': xcmp.Decimal('1017.02'),
                'currency': 'EUR',
            },
            {
                'contract_id': '844463',
                'contract_type': 'CORPORATE',
                'contract_alias': 'РАС-285640',
                'contract_limit': xcmp.Decimal('750.00'),
                'amount': xcmp.Decimal('19660.8'),
                'currency': 'RUB',
            },
        ],
    },
    'payout_status': 'ready_to_pay',
}


def response_json(response):
    response = response.json()
    with contextlib.suppress(TypeError, KeyError, AttributeError):
        if 'balance' in response:
            entries = response['balance']['entries']
            entries.sort(key=lambda x: x['contract_id'])
        if 'pending_payment' in response:
            entries = response['pending_payment']['entries']
            entries.sort(key=lambda x: x['contract_id'])
    return response


@pytest.mark.pgsql('fleet_payouts', files=['balances.sql'])
@pytest.mark.now('2020-03-21T21:00:00+03:00')
async def test_non_configured_park(taxi_fleet_payouts, mock_users, mock_parks):
    response = await taxi_fleet_payouts.get(**DEFAULT_REQUEST)
    assert response.status_code == 200, response.text
    assert response_json(response) == {
        **DEFAULT_RESPONSE,
        'payout_status': 'disabled',
    }


@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_non_park_user(taxi_fleet_payouts, mock_users, mock_parks):
    request = copy.deepcopy(DEFAULT_REQUEST)
    request['headers']['X-Yandex-UID'] = '9999'

    response = await taxi_fleet_payouts.get(**request)
    assert response.status_code == 403, response.text
    assert response_json(response) == {
        'code': '403',
        'message': 'User not found.',
    }


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'simple_fleet_version.sql'],
)
@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_simple_fleet_version(
        taxi_fleet_payouts, mock_users, mock_parks,
):
    response = await taxi_fleet_payouts.get(**DEFAULT_REQUEST)
    assert response.status_code == 200, response.text
    assert response_json(response) == {
        **DEFAULT_RESPONSE,
        'payout_status': 'disabled',
    }


@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_balance_not_found(taxi_fleet_payouts, mock_users, mock_parks):
    response = await taxi_fleet_payouts.get(**DEFAULT_REQUEST)
    assert response.status_code == 200, response.text
    assert response_json(response) == {'payout_status': 'disabled'}


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'test_outdated_balance.sql'],
)
@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_outdated_balance(taxi_fleet_payouts, mock_users, mock_parks):
    response = await taxi_fleet_payouts.get(**DEFAULT_REQUEST)
    assert response.status_code == 200, response.text
    assert response_json(response) == {
        **DEFAULT_RESPONSE,
        'pending_payment': {
            'payment_id': 'PAYMENT00',
            'payment_date': xcmp.Date('2020-03-21T15:00:00+03:00'),
            'status': 'pending',
            'entries': [
                {
                    'contract_id': '278761',
                    'amount': xcmp.Decimal('4232.21'),
                    'currency': 'RUB',
                },
            ],
        },
        'payout_status': 'blocked_until_completed',
    }


@pytest.mark.pgsql(
    'fleet_payouts', files=['balances.sql', 'test_pending_payment.sql'],
)
@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(**DEFAULT_CONFIG)
async def test_pending_payment(taxi_fleet_payouts, mock_users, mock_parks):
    response = await taxi_fleet_payouts.get(**DEFAULT_REQUEST)
    assert response.status_code == 200, response.text
    assert response_json(response) == {
        **DEFAULT_RESPONSE,
        'pending_payment': {
            'payment_id': 'PAYMENT00',
            'payment_date': xcmp.Date('2020-03-20T15:00:00+03:00'),
            'status': 'pending',
            'entries': [
                {
                    'contract_id': '278761',
                    'amount': xcmp.Decimal('4232.21'),
                    'currency': 'RUB',
                },
                {
                    'contract_id': '656839',
                    'amount': xcmp.Decimal('423.21'),
                    'currency': 'EUR',
                },
                {
                    'contract_id': '679178',
                    'amount': xcmp.Decimal('703.00'),
                    'currency': 'EUR',
                },
                {
                    'contract_id': '844463',
                    'amount': xcmp.Decimal('19660.80'),
                    'currency': 'RUB',
                },
            ],
        },
        'payout_status': 'blocked_until_completed',
    }


@pytest.mark.pgsql('fleet_payouts', files=['test_scheduled_at.sql'])
@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(
    FLEET_PAYOUTS_WITHDRAWAL_RULES=[
        {
            'condition': {'clid': ['CLID00']},
            'definition': {'enable_schedule': {'period': 1, 'time': '03:00'}},
        },
    ],
)
async def test_scheduled_at(taxi_fleet_payouts, mock_users, mock_parks):
    response = await taxi_fleet_payouts.get(**DEFAULT_REQUEST)
    assert response.status_code == 200, response.text
    assert response_json(response) == {
        'payout_status': 'disabled',
        'payout_scheduled_at': xcmp.Date('2020-03-22T21:00:00+03:00'),
    }


@pytest.mark.pgsql('fleet_payouts', files=['test_scheduled_at_null.sql'])
@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.config(
    FLEET_PAYOUTS_WITHDRAWAL_RULES=[
        {
            'condition': {'clid': ['CLID00']},
            'definition': {'enable_schedule': {'period': 1, 'time': '03:00'}},
        },
    ],
)
async def test_scheduled_at_null(taxi_fleet_payouts, mock_users, mock_parks):
    response = await taxi_fleet_payouts.get(**DEFAULT_REQUEST)
    assert response.status_code == 200, response.text
    assert response_json(response) == {'payout_status': 'disabled'}


@pytest.mark.pgsql('fleet_payouts', files=['test_scheduled_at.sql'])
@pytest.mark.now('2020-03-21T21:00:00+03:00')
async def test_scheduled_at_without_config(
        taxi_fleet_payouts, mock_users, mock_parks,
):
    response = await taxi_fleet_payouts.get(**DEFAULT_REQUEST)
    assert response.status_code == 200, response.text
    assert response_json(response) == {'payout_status': 'disabled'}
