import pytest


NOW = '2020-01-01T12:00:00+03:00'
PARK_ID = 'PARK-01'


@pytest.mark.config(
    FLEET_ANTIFRAUD_PARK_CHECK={
        'is_enabled': True,
        'expiring_interval': 86400,
        'billing_fetching_overlap': 3600,
        'update_range': 60,
    },
)
@pytest.mark.parametrize('do_update', [True, False])
@pytest.mark.now(NOW)
async def test_get_blocked_balance(fleet_v1, pg_dump, mock_api, do_update):
    pg_initial = pg_dump()

    response = await fleet_v1.get_park_check_blocked_balance(
        park_id=PARK_ID, contractor_id='CONTRACTOR-02', do_update=do_update,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'blocked_balance': '100'}

    if not do_update:
        assert pg_dump() == pg_initial
        assert not mock_api['driver-orders']['/v1/parks/orders/list'].has_calls
        assert not mock_api['fleet-transactions-api'][
            '/v1/parks/driver-profiles/transactions/list'
        ].has_calls
    else:
        assert (
            mock_api['driver-orders']['/v1/parks/orders/list']
            .next_call()['request']
            .json
            == {
                'query': {
                    'park': {
                        'id': 'PARK-01',
                        'order': {
                            'ended_at': {
                                'from': '2020-01-01T08:59:00+00:00',
                                'to': '2020-01-01T09:00:00+00:00',
                            },
                        },
                        'driver_profile': {'id': 'CONTRACTOR-02'},
                    },
                },
                'limit': 500,
            }
        )
        assert (
            mock_api['fleet-transactions-api'][
                '/v1/parks/driver-profiles/transactions/list'
            ]
            .next_call()['request']
            .json
            == {
                'query': {
                    'park': {
                        'id': 'PARK-01',
                        'driver_profile': {'id': 'CONTRACTOR-02'},
                        'transaction': {
                            'event_at': {
                                'from': '2020-01-01T08:59:00+00:00',
                                'to': '2020-01-01T09:00:00+00:00',
                            },
                            'group_ids': ['platform_tip', 'platform_bonus'],
                        },
                    },
                },
                'limit': 1000,
            }
        )
