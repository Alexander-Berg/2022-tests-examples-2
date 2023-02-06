import pytest


@pytest.mark.now('2021-01-01T12:00+03:00')
@pytest.mark.pgsql(
    'fleet_payouts',
    files=[
        'payments.sql',
        'payment_entries.sql',
        'fleet_statistics.sql',
        'partner_payout_mode_changes.sql',
        'payment_timers.sql',
    ],
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
@pytest.mark.parametrize(
    'status_code,clid,payout_mode,pending_payment,'
    'payout_scheduled_at,on_demand_available',
    [
        (200, 'CLID00', 'regular', None, None, False),
        (
            200,
            'CLID01',
            'regular',
            {'status': 'pending', 'amount': '100', 'currency': 'RUB'},
            '2021-01-02T22:30:00+00:00',
            False,
        ),
        (200, 'CLID02', 'on_demand', None, None, True),
        (200, 'CLID03', 'on_demand', None, '2021-01-31T22:30:00+00:00', True),
        (
            200,
            'CLID05',
            'on_demand',
            {'status': 'created'},
            '2021-01-01T22:30:00+00:00',
            False,
        ),
        (
            200,
            'CLID06',
            'on_demand',
            {'status': 'pending', 'amount': '200', 'currency': 'RUB'},
            '2021-01-31T22:30:00+00:00',
            False,
        ),
        pytest.param(
            200,
            'CLID07',
            'regular',
            {'status': 'created'},
            '2021-01-01T22:30:00+00:00',
            False,
            id='no_payout_mode_in_db',
        ),
        (400, 'CLID08', None, None, None, None),
    ],
)
async def test_on_demand_status(
        taxi_fleet_payouts,
        mock_users,
        mock_parks,
        status_code,
        clid,
        payout_mode,
        pending_payment,
        payout_scheduled_at,
        on_demand_available,
):
    request = {
        'path': 'internal/on-demand-payouts/v1/status',
        'params': {'clid': clid},
        'headers': {
            'X-Yandex-UID': '1000',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
            'X-Idempotency-Token': 'TESTSUITE-IDEMPOTENCY-TOKEN',
        },
    }
    response = await taxi_fleet_payouts.get(**request)
    assert response.status_code == status_code, response.text
    if status_code == 200:
        _expected = {
            'payout_mode': payout_mode,
            'on_demand_available': on_demand_available,
        }
        if pending_payment is not None:
            _expected['pending_payment'] = pending_payment
        if payout_scheduled_at is not None:
            _expected['payout_scheduled_at'] = payout_scheduled_at
        assert response.json() == _expected
