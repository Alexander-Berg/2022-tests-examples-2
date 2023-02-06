import pytest

from tests_fleet_payouts.utils import pg
from tests_fleet_payouts.utils import xcmp


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@pytest.mark.pgsql(
    'fleet_payouts', files=['test_on_demand_order.sql', 'balances.sql'],
)
@pytest.mark.config(
    FLEET_PAYOUTS_WITHDRAWAL_RULES=[
        {
            'condition': {
                'partner_type': ['self_employed'],
                'payout_mode': 'on_demand',
            },
            'definition': {
                'enable_requests': True,
                'enable_schedule': {'period': 14, 'time': '03:00'},
            },
        },
        {
            'condition': {'partner_type': ['self_employed']},
            'definition': {
                'enable_requests': True,
                'enable_schedule': {'period': 1, 'time': '03:00'},
            },
        },
    ],
)
@pytest.mark.parametrize(
    'status_code,clid,expected_expires_at',
    [
        pytest.param(
            200, 'CLID00', '2021-01-02T03:00+03:00', id='move_to_tomorrow',
        ),
        pytest.param(
            200, 'CLID01', '2021-01-02T03:00+03:00', id='dont_change',
        ),
        pytest.param(400, 'CLID02', None, id='not_allowed_partner_type'),
        pytest.param(400, 'CLID03', None, id='not_allowed_payout_mode'),
        pytest.param(
            200,
            'CLID04',
            '2021-01-02T03:00+03:00',
            id='pick_right_payout_mode',
        ),
    ],
)
async def test_create_order(
        taxi_fleet_payouts,
        mock_parks_by_clids,
        pgsql,
        status_code,
        clid,
        expected_expires_at,
):
    request = {
        'path': 'internal/on-demand-payouts/v1/order',
        'params': {'clid': clid},
        'headers': {
            'X-Yandex-UID': '1000',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
            'X-Idempotency-Token': 'TESTSUITE-IDEMPOTENCY-TOKEN',
            'Content-Type': 'application/json',
        },
    }
    response = await taxi_fleet_payouts.put(**request)
    assert response.status_code == status_code
    if status_code == 200:
        assert pg.dump_payment_timers(pgsql)[clid] == {
            'clid': clid,
            'expires_at': xcmp.Date(expected_expires_at),
        }
