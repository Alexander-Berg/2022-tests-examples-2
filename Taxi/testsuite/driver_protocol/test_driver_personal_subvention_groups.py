import pytest

from . import common

HEADERS = {'Accept-Language': 'ru', 'User-Agent': 'Taximeter 8.60 (562)'}
ARGS = {'park_id': 'park'}


@pytest.mark.now('2017-05-25T03:00:00')
@pytest.mark.config(SUBVENTIONS_COUNTRIES_WITH_HIDDEN_PERSONAL=['kaz'])
@pytest.mark.translations(
    taximeter_messages={
        'subventions.for_n_rides': {
            'ru': ['make %(count)s orders get %(sum)s %(currency_sign)s'] * 3,
        },
        'subventions.for_n_rides_with_hours': {
            'ru': [
                (
                    'make %(count)s orders from %(begin_time)s '
                    'to %(end_time)s get %(sum)s %(currency_sign)s '
                    'till %(day)s %(month)s'
                ),
            ] * 3,
        },
        'subventions.n_orders': {'ru': ['%(count)s orders'] * 3},
        'subventions.rule_completed_orders_header': {
            'ru': 'num completed orders',
        },
        'subventions.rule_duration_inclusive': {
            'ru': 'action is for %(day)s %(month)s inclusive',
        },
        'subventions.rule_duration_inclusive_with_hours': {
            'ru': (
                'action is for %(day)s %(month)s inclusive '
                'from %(from)s to %(to)s'
            ),
        },
        'subventions.rules_header': {'ru': 'you get bonuses'},
        'subventions.rule_sum': {'ru': '%(sum)s %(currency_sign)s'},
    },
    notify={
        'helpers.month_5_part': {'ru': 'may'},
        'helpers.month_6_part': {'ru': 'june'},
    },
    tariff={'currency.rub': {'ru': 'rub'}, 'currency_sign.rub': {'ru': 'rub'}},
    geoareas={'moscow': {'ru': 'moscow'}},
)
@common.sv_proxy_decorator(
    experiment_name='subvention_view_personal_status',
    consumer='driver_protocol/driver_personal_subvention_groups',
    url='/subvention_view/v1/personal/status',
    result='expected_response.json',
    expected_args=ARGS,
    expected_headers=HEADERS,
)
def test_subvention_rules(
        taxi_driver_protocol,
        driver_authorizer_service,
        experiments3,
        load_json,
        mockserver,
        proxy_mode,
):
    driver_authorizer_service.set_session('park', 'some_session', 'uuid')

    response = taxi_driver_protocol.get(
        '/driver/personal-subvention-groups',
        params={'session': 'some_session', 'db': 'park', 'locale': 'ru'},
        headers=HEADERS,
    )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_response.json')
    _assert_same_items(response_data, expected_data)


def _assert_same_items(data, expected_data):
    data['items'].sort(key=lambda x: x['id'])
    assert data == expected_data
