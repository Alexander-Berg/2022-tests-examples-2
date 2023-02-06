import pytest

HEADERS = {
    'X-Yandex-UID': '1000',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
    'X-Idempotency-Token': 'TESTSUITE-IDEMPOTENCY-TOKEN',
}

ENDPOINT = 'internal/on-demand-payouts/v1/history'


@pytest.mark.now('2021-01-03T00:01+00:00')
@pytest.mark.pgsql(
    'fleet_payouts',
    files=['fleet_statistics.sql', 'partner_payout_mode_changes.sql'],
)
@pytest.mark.config(
    FLEET_PAYOUTS_WITHDRAWAL_RULES=[
        {
            'condition': {
                'partner_type': ['self_employed', 'individual_entrepreneur'],
                'payout_mode': 'on_demand',
            },
            'definition': {
                'enable_requests': True,
                'enable_schedule': {'period': 14, 'time': '03:00'},
            },
        },
        {
            'condition': {
                'partner_type': ['self_employed', 'individual_entrepreneur'],
            },
            'definition': {
                'enable_requests': True,
                'enable_schedule': {'period': 1, 'time': '03:00'},
            },
        },
    ],
)
async def test_on_demand_history(taxi_fleet_payouts, mock_users, mock_parks):
    request = {
        'path': ENDPOINT,
        'params': {'clid': 'CLID01', 'limit': 2},
        'headers': HEADERS,
    }
    first_response = await taxi_fleet_payouts.get(**request)
    assert first_response.status_code == 200
    assert first_response.json() == {
        'items': [
            {
                'payout_mode': 'on_demand',
                'modified_date': '2021-01-03T00:00:00+00:00',
            },
            {
                'payout_mode': 'on_demand',
                'modified_date': '2021-01-02T00:00:00+00:00',
            },
        ],
    }

    request['params']['before'] = first_response.json()['items'][-1][
        'modified_date'
    ]
    second_response = await taxi_fleet_payouts.get(**request)
    assert second_response.status_code == 200
    assert second_response.json() == {
        'items': [
            {
                'payout_mode': 'regular',
                'modified_date': '2021-01-01T00:00:00+00:00',
            },
        ],
    }
