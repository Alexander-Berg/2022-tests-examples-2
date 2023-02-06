# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest


DEFAULT_POSITION: list = [37.590533, 55.733863]
INVALID_POSITION: list = [35, 55]
BLACKLISTED_POSITION: list = [37.55847930908203, 55.43407820181597]
SPB_POSITION: list = [30.322265625000004, 59.94607052743776]
DEFAULT_REQUEST = {'location': DEFAULT_POSITION}
DEFAULT_UA = 'yandex-taxi/3.129.0.110856 Android/9 (samsung; SM-A705FN)'
DEFAULT_YANDEX_UID = 'uuid'
DEFAULT_PHONE_ID = '88005353535'
DEFAULT_USER_ID = 'user_id'
DEFAULT_HEADERS = {
    'User-Agent': DEFAULT_UA,
    'X-Yandex-UID': DEFAULT_YANDEX_UID,
    'X-YaTaxi-PhoneId': DEFAULT_PHONE_ID,
    'X-YaTaxi-UserId': DEFAULT_USER_ID,
}


@pytest.fixture(name='superapp_payment_methods')
def _superapp_payment_methods(experiments3):
    def _inner(payment_methods):
        experiments3.add_config(
            name='superapp_payment_methods',
            consumers=['payment-methods/superapp-available-payment-types'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            default_value=payment_methods,
        )

    return _inner


def make_payment(available=None, disabled_reason=None, **kwargs):
    result = kwargs
    if available is not None:
        result['available'] = available
    if disabled_reason is not None:
        result['availability'] = {
            'available': available,
            'disabled_reason': disabled_reason,
        }
    return result


@pytest.mark.geoareas(filename='db_geoareas.json')
@pytest.mark.experiments3(filename='exp3_available_payment_types.json')
@pytest.mark.parametrize(
    'service, flow, user_agent, request_body, phone_id, yandex_uid, '
    'expected_response',
    [
        (
            'grocery',
            None,
            'yandex-taxi/3.129.0.110856 Android/9 (samsung; SM-A705FN)',
            {'location': INVALID_POSITION},
            DEFAULT_PHONE_ID,
            DEFAULT_YANDEX_UID,
            {
                'payment_types': [
                    'card',
                    'yandex_bank',
                    'applepay',
                    'cibus',
                    'sbp',
                    'sbp_link',
                ],
                'merchant_ids': ['merchant.ru.grocery'],
            },
        ),
        (
            'eats',
            None,
            DEFAULT_UA,
            DEFAULT_REQUEST,
            DEFAULT_PHONE_ID,
            DEFAULT_YANDEX_UID,
            {
                'payment_types': ['card', 'applepay', 'coop_account'],
                'merchant_ids': ['merchant.ru.yandex.ytaxi.trust'],
            },
        ),
        (
            # checking, that destination point can be used as kwarg in exp
            # case than point outside polygon
            'eats',
            None,
            'yandex-taxi/3.129.0.110856 Android/9 (samsung; SM-A705FN)',
            {
                'location': DEFAULT_POSITION,
                'destination_point': DEFAULT_POSITION,
            },
            DEFAULT_PHONE_ID,
            DEFAULT_YANDEX_UID,
            {
                'payment_types': ['card', 'applepay', 'coop_account'],
                'merchant_ids': ['merchant.ru.yandex.ytaxi.trust'],
            },
        ),
        (
            # checking, that destination point can be used as kwarg in exp
            # case than point inside polygon
            'eats',
            None,
            'yandex-taxi/3.129.0.110856 Android/9 (samsung; SM-A705FN)',
            {
                'location': DEFAULT_POSITION,
                # to visualize testcase - paste text from
                # https://paste.yandex-team.ru/1139293 to geojson.io
                'destination_point': BLACKLISTED_POSITION,
            },
            DEFAULT_PHONE_ID,
            DEFAULT_YANDEX_UID,
            {
                'payment_types': [],
                'merchant_ids': ['merchant.ru.yandex.ytaxi.trust'],
            },
        ),
        (
            'pharmacy',
            None,
            DEFAULT_UA,
            DEFAULT_REQUEST,
            DEFAULT_PHONE_ID,
            DEFAULT_YANDEX_UID,
            {'payment_types': ['card'], 'merchant_ids': []},
        ),
        (
            'restaurants',
            None,
            DEFAULT_UA,
            DEFAULT_REQUEST,
            DEFAULT_PHONE_ID,
            DEFAULT_YANDEX_UID,
            {'payment_types': ['card'], 'merchant_ids': []},
        ),
        (
            'shop',
            None,
            DEFAULT_UA,
            DEFAULT_REQUEST,
            DEFAULT_PHONE_ID,
            DEFAULT_YANDEX_UID,
            {'payment_types': ['card'], 'merchant_ids': []},
        ),
        (
            'pickup_points',
            None,
            DEFAULT_UA,
            DEFAULT_REQUEST,
            DEFAULT_PHONE_ID,
            DEFAULT_YANDEX_UID,
            {
                'payment_types': ['card', 'applepay', 'corp'],
                'merchant_ids': [],
            },
        ),
        (
            'scooters',
            None,
            DEFAULT_UA,
            DEFAULT_REQUEST,
            DEFAULT_PHONE_ID,
            DEFAULT_YANDEX_UID,
            {'payment_types': ['card'], 'merchant_ids': []},
        ),
        (
            'scooters',
            'passes',
            DEFAULT_UA,
            DEFAULT_REQUEST,
            DEFAULT_PHONE_ID,
            DEFAULT_YANDEX_UID,
            {'payment_types': ['card'], 'merchant_ids': []},
        ),
    ],
)
async def test_available_payment_types(
        taxi_payment_methods,
        taxi_payment_methods_monitor,
        mockserver,
        taxi_config,
        service,
        flow,
        user_agent,
        request_body,
        phone_id,
        yandex_uid,
        expected_response,
):
    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _protocol(request):
        return {'nearest_zone': 'moscow'}

    async with metrics_helpers.MetricsCollector(
            taxi_payment_methods_monitor,
            sensor='available_payment_types_metrics',
    ) as collector:
        params = {'service': service}
        if flow is not None:
            params['flow'] = flow
        response = await taxi_payment_methods.post(
            '/v1/superapp-available-payment-types',
            params=params,
            json=request_body,
            headers={
                'User-Agent': user_agent,
                'X-Yandex-UID': yandex_uid,
                'X-YaTaxi-PhoneId': phone_id,
                'X-YaTaxi-UserId': DEFAULT_USER_ID,
            },
        )

    assert response.status_code == 200
    response_json = response.json()
    response_json.pop('payments')  # check it in self test
    assert response_json == expected_response

    assert _protocol.times_called == 0

    metrics = sorted(
        collector.collected_metrics, key=lambda it: it.labels['payment_type'],
    )

    expected_metrics = []
    for payment_type in expected_response['payment_types']:
        expected_metrics.append(
            metrics_helpers.Metric(
                labels={
                    'sensor': 'available_payment_types_metrics',
                    'payment_type': payment_type,
                    'service_name': service,
                    'flow': flow if flow is not None else 'order',
                    'country': 'RU',
                    'application_name': 'android',
                },
                value=1,
            ),
        )
    expected_metrics = sorted(
        expected_metrics, key=lambda it: it.labels['payment_type'],
    )

    assert metrics == expected_metrics


@pytest.mark.parametrize(
    'config_payment_type, expected_payment_types',
    [
        ('cash', ['cash']),
        ('card', ['card']),
        ('yandex_bank', ['yandex_bank']),
        ('applepay', ['applepay']),
        ('googlepay', ['googlepay']),
        ('corp', ['corp']),
        ('badge', ['badge']),
        ('personal_wallet', ['personal_wallet']),
        ('coop_account', ['coop_account']),
        ('cibus', ['cibus']),
        ('sbp_link', ['sbp', 'sbp_link']),
        ('sbp_qr', ['sbp', 'sbp_qr']),
    ],
)
@pytest.mark.parametrize('payment_type_available', [True, False])
async def test_check_payment_types(
        taxi_payment_methods,
        superapp_payment_methods,
        config_payment_type,
        expected_payment_types,
        payment_type_available,
):
    config_payments = {
        config_payment_type: {'available': payment_type_available},
    }

    superapp_payment_methods(config_payments)

    response = await taxi_payment_methods.post(
        '/v1/superapp-available-payment-types?service=eats',
        json=DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    if not payment_type_available:
        expected_payment_types = []

    assert response.status_code == 200
    assert response.json()['payment_types'] == expected_payment_types


@pytest.mark.parametrize(
    'config_payments, expected_payments',
    [
        (dict(applepay=dict(available=False)), {}),
        (
            dict(applepay=dict(available=True)),
            dict(applepay=make_payment(type='applepay')),
        ),
        (
            dict(
                applepay=dict(
                    available=False, disabled_reason='payment_method.disabled',
                ),
            ),
            dict(
                applepay=make_payment(
                    type='applepay',
                    available=False,
                    disabled_reason='Выключено',
                ),
            ),
        ),
        (dict(yandex_bank=dict(available=False)), {}),
        (
            dict(yandex_bank=dict(available=True)),
            dict(yandex_bank=make_payment(type='yandex_bank')),
        ),
        (
            dict(
                yandex_bank=dict(
                    available=False, disabled_reason='payment_method.disabled',
                ),
            ),
            dict(
                yandex_bank=make_payment(
                    type='yandex_bank',
                    available=False,
                    disabled_reason='Выключено',
                ),
            ),
        ),
        (
            dict(
                applepay=dict(
                    available=False, disabled_reason='payment_method.unknown',
                ),
            ),
            dict(
                applepay=make_payment(
                    type='applepay',
                    available=False,
                    disabled_reason='payment_method.unknown',
                ),
            ),
        ),
        (
            dict(cibus=dict(available=True)),
            dict(cibus=make_payment(type='cibus', id='cibus')),
        ),
        (
            dict(sbp_qr=dict(available=True)),
            dict(sbp=make_payment(type='sbp', id='sbp_qr')),
        ),
        (
            dict(sbp_link=dict(available=False), sbp_qr=dict(available=True)),
            dict(sbp=make_payment(type='sbp', id='sbp_qr')),
        ),
    ],
)
async def test_check_payments(
        taxi_payment_methods,
        superapp_payment_methods,
        config_payments,
        expected_payments,
):
    superapp_payment_methods(config_payments)

    response = await taxi_payment_methods.post(
        '/v1/superapp-available-payment-types?service=eats',
        json=DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payments'] == expected_payments
