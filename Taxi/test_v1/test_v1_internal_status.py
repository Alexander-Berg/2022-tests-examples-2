import pytest

from tests_driver_fix import common


@pytest.mark.now('2020-02-01T12:00:00+0300')
@pytest.mark.config(
    DRIVER_FIX_USE_BSX_VIRTUAL_BY_DRIVER=True,
    DRIVER_FIX_ONLINE_TIME_RESET_ON_SHIFT_CLOSE_ENABLED=False,
)
async def test_internal_status_data(
        taxi_driver_fix, mockserver, mock_offer_requirements, taxi_config,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _driver_mode_subscription_mode_info(request):
        assert request.args['driver_profile_id'] == 'uuid'
        assert request.args['park_id'] == 'dbid'
        return {
            'mode': {
                'name': 'driver_fix_mode',
                'started_at': '2020-01-02T12:00:00+0300',
                'features': [
                    {
                        'name': 'driver_fix',
                        'settings': {
                            'rule_id': 'subvention_rule_id',
                            'shift_close_time': '23:00:00+03:00',
                        },
                    },
                    {'name': 'tags'},
                ],
            },
        }

    @mockserver.json_handler('/billing-subventions-x/v1/virtual_by_driver')
    async def _get_by_driver(request):
        assert request.json == {
            'driver': {'db_id': 'dbid', 'uuid': 'uuid'},
            'types': ['driver_fix'],
        }
        return {
            'subventions': [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': '_id/subvention_rule_id',
                    'payoff': {'amount': '1', 'currency': 'RUB'},
                    'period': {
                        'start': '2020-01-01T00:00:01+03:00',
                        'end': '2020-01-02T00:00:00+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '2',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': 912,
                        'cash_income': {'amount': '3', 'currency': 'RUB'},
                        'guarantee': {'amount': '4', 'currency': 'RUB'},
                        'cash_commission': {'amount': '5', 'currency': 'RUB'},
                        'total_income': {'amount': '6', 'currency': 'RUB'},
                    },
                },
            ],
        }

    response = await taxi_driver_fix.get(
        'v1/internal/status',
        params={
            'park_id': 'dbid',
            'driver_profile_id': 'uuid',
            'language': 'ru',
        },
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    response_body = response.json()

    assert response_body == {
        'time': {'seconds': 912, 'localized': '15'},
        'guaranteed_money': {
            'value': 4.0,
            'currency': 'RUB',
            'localized': '4 ₽',
        },
        'cash_income': {'value': 3.0, 'currency': 'RUB', 'localized': '3 ₽'},
        'payoff': {'value': 1.0, 'currency': 'RUB', 'localized': '1 ₽'},
        'commission': {'value': 2.0, 'currency': 'RUB', 'localized': '2 ₽'},
        'total_income': {'value': 6.0, 'currency': 'RUB', 'localized': '6 ₽'},
    }
