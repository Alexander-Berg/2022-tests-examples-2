import datetime

import pytest

from tests_fleet_payouts.utils import pg


NOW = '2021-01-01T12:00:00+03:00'
ON_DEMAND_PERIOD = 14
PAYOUT_SCHEDULE_TIME = '03:00'


def parse_time(time):
    return tuple(map(int, time.split(':')))


@pytest.mark.now(NOW)
@pytest.mark.pgsql('fleet_payouts', files=['test_on_demand_change_mode.sql'])
@pytest.mark.config(
    FLEET_PAYOUTS_WITHDRAWAL_RULES=[
        {
            'condition': {
                'partner_type': ['self_employed'],
                'payout_mode': 'on_demand',
            },
            'definition': {
                'enable_requests': True,
                'enable_schedule': {
                    'period': ON_DEMAND_PERIOD,
                    'time': PAYOUT_SCHEDULE_TIME,
                },
            },
        },
        {
            'condition': {'partner_type': ['self_employed']},
            'definition': {
                'enable_requests': True,
                'enable_schedule': {'period': 1, 'time': PAYOUT_SCHEDULE_TIME},
            },
        },
    ],
)
@pytest.mark.parametrize(
    'status_code,clid,mode_to_set,expected_expires_at',
    [
        pytest.param(
            200,
            'CLID00',
            'on_demand',
            '2021-01-15T03:00+03:00',
            id='first_change_ondemand',
        ),
        pytest.param(
            200,
            'CLID01',
            'regular',
            '2021-01-02T03:00+03:00',
            id='first_change_regular',
        ),
        pytest.param(
            200,
            'CLID02',
            'on_demand',
            '2021-01-02T03:00+03:00',
            id='regular_to_ondemand',
        ),
        pytest.param(
            200,
            'CLID03',
            'regular',
            '2021-01-02T03:00+03:00',
            id='ondemand_to_regular',
        ),
        pytest.param(
            200,
            'CLID04',
            'on_demand',
            '2021-01-15T03:00+03:00',
            id='ondemand_to_ondemand',
        ),
        pytest.param(
            200,
            'CLID05',
            'regular',
            '2021-01-02T03:00+03:00',
            id='regular_to_regular',
        ),
        pytest.param(
            400, 'CLID06', None, None, id='not_allowed_by_partner_type',
        ),
    ],
)
async def test_change_mode(
        taxi_fleet_payouts,
        pgsql,
        status_code,
        clid,
        mode_to_set,
        expected_expires_at,
):
    request = {
        'path': 'internal/on-demand-payouts/v1/change-mode',
        'params': {'clid': clid},
        'json': {'payout_mode': mode_to_set},
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
        assert pg.dump_partner_current_mode(pgsql, clid) == {
            'clid': clid,
            'active_since': datetime.datetime.fromisoformat(NOW),
            'active_mode': mode_to_set,
        }
        assert pg.dump_payment_timers(pgsql)[clid] == {
            'clid': clid,
            'expires_at': datetime.datetime.fromisoformat(expected_expires_at),
        }
