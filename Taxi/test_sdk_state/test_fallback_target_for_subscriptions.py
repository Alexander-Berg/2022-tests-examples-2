import pytest

from tests_plus_sweet_home import constants

# pylint: disable=invalid-name
pytestmark = [pytest.mark.experiments3(filename='experiments3_defaults.json')]

HEADERS = {
    'X-SDK-Client-ID': 'taxi.test',
    'X-SDK-Version': '10.10.10',
    'X-Yandex-UID': '111111',
    'X-YaTaxi-Pass-Flags': 'portal,cashback-plus',
    'X-Request-Language': 'ru',
    'X-Remote-IP': '185.15.98.233',
}


@pytest.mark.parametrize(
    'x_remote_ip, subscription_match_fail, is_sub_exist, yandex_uid',
    [
        ('185.15.98.233', 0, True, 'uid_1'),
        ('185.15.98.233', 1, True, 'uid_2'),
        ('5.100.192.37', 1, False, 'uid_2'),
    ],
)
async def test_check_fallback_target_for_subscriptions(
        taxi_plus_sweet_home,
        mockserver,
        taxi_plus_sweet_home_monitor,
        x_remote_ip,
        subscription_match_fail,
        is_sub_exist,
        yandex_uid,
):
    old_metrics_statistics = await taxi_plus_sweet_home_monitor.get_metric(
        'subscription_statistics',
    )

    headers = HEADERS
    headers['X-Remote-IP'] = x_remote_ip
    headers['X-Yandex-UID'] = yandex_uid

    @mockserver.json_handler('/fast-prices/billing/transitions')
    def _mock_fast_prices_billing_transitions(request):
        request_data = request.query
        transitions = []
        if (
                request_data['target'] == 'default_target'
                or request_data['target'] == 'target_1'
        ):
            transitions = [
                {
                    'available': True,
                    'product': {
                        'id': constants.TRIAL_PRODUCT_ID,
                        'vendor': 'YANDEX',
                    },
                    'transitionType': 'SUBMIT',
                },
            ]

        return mockserver.make_response(
            json={'transitions': transitions}, status=200,
        )

    response = await taxi_plus_sweet_home.post(
        '/4.0/sweet-home/v2/sdk-state',
        headers=HEADERS,
        json={'include': ['state']},
    )

    assert response.status_code == 200
    content = response.json()
    subscription = content['state']['subscription']

    if is_sub_exist:
        assert subscription['subscription_id'] == 'ya_plus_rus_v2_trial'
        assert subscription['status'] == 'AVAILABLE'
    else:
        assert subscription['status'] == 'NOT_AVAILABLE'

    metrics_json = await taxi_plus_sweet_home_monitor.get_metric(
        'subscription_statistics',
    )
    assert (
        metrics_json['subscription_match_fail']
        - old_metrics_statistics['subscription_match_fail']
        == subscription_match_fail
    )
