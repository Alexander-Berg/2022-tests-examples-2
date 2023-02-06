# pylint: disable=C0302

import pytest

from tests_driver_fix import common


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.parametrize(
    'subvention_list, expected_time, expected_guarantee, expected_commission,'
    'equal_to_status, no_shifts',
    [
        (
            [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': 'subvention_rule_id',
                    'payoff': {'amount': '10', 'currency': 'RUB'},
                    'period': {
                        'start_time': '2019-01-01T00:00:00+03:00',
                        'end_time': '2019-01-01T23:59:59+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '20',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': 600,
                        'cash_income': {'amount': '30', 'currency': 'RUB'},
                        'guarantee': {'amount': '50', 'currency': 'RUB'},
                        'cash_commission': {'amount': '50', 'currency': 'RUB'},
                        'total_income': {'amount': '60', 'currency': 'RUB'},
                    },
                },
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': 'subvention_rule_id_2',
                    'payoff': {'amount': '60', 'currency': 'RUB'},
                    'period': {
                        'start_time': '2019-01-02T00:00:00+03:00',
                        'end_time': '2019-01-02T23:59:59+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '70',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': 72000,
                        'cash_income': {'amount': '80', 'currency': 'RUB'},
                        'guarantee': {'amount': '100', 'currency': 'RUB'},
                        'cash_commission': {
                            'amount': '100',
                            'currency': 'RUB',
                        },
                        'total_income': {'amount': '120', 'currency': 'RUB'},
                    },
                },
            ],
            72600,
            150,
            90,
            False,
            False,
        ),
        (
            [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': 'subvention_rule_id_2',
                    'payoff': {'amount': '60', 'currency': 'RUB'},
                    'period': {
                        'start_time': '2019-01-02T00:00:00+03:00',
                        'end_time': '2019-01-02T23:59:59+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '70',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': 72000,
                        'cash_income': {'amount': '80', 'currency': 'RUB'},
                        'guarantee': {'amount': '100', 'currency': 'RUB'},
                        'cash_commission': {
                            'amount': '100',
                            'currency': 'RUB',
                        },
                        'total_income': {'amount': '160', 'currency': 'RUB'},
                    },
                },
            ],
            72000,
            100,
            70,
            True,
            False,
        ),
        ([], 0.0, 0.0, 0.0, True, True),
    ],
)
@pytest.mark.now('2019-01-02T02:00:00+0300')
async def test_status_summary(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        subvention_list,
        expected_time,
        expected_guarantee,
        expected_commission,
        equal_to_status,
        no_shifts,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        if subvention_list:
            answer = {'subventions': subvention_list}
        else:
            answer = mockserver.make_response('not found error', 404)
        return answer

    summary_response = await taxi_driver_fix.get(
        'v1/view/status_summary',
        params={'park_id': 'dbid', 'driver_profile_id': 'driver_profile_id_1'},
        headers={'X-Ya-Service-Ticket': common.MOCK_SERVICE_TICKET},
    )

    status_response = await taxi_driver_fix.get(
        'v1/view/status',
        params={'tz': 'Europe/Moscow', 'park_id': 'dbid'},
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )
    assert summary_response.status_code == 200
    assert status_response.status_code == 200
    summary_doc = summary_response.json()
    status_doc = status_response.json()

    assert summary_doc['time'] == expected_time
    assert summary_doc['guaranteed_money'] == expected_guarantee
    assert summary_doc['commission'] == expected_commission
    assert summary_doc['no_shifts'] == no_shifts

    status_subtitle = status_doc['panel_header']['subtitle']
    status_guaranteed_money = int(status_subtitle.split(';')[-1].split()[0])
    if equal_to_status:
        assert summary_doc['guaranteed_money'] == int(status_guaranteed_money)
    else:
        assert summary_doc['guaranteed_money'] != int(status_guaranteed_money)
