import pytest

import common
import const

HEADERS = {
    'X-YaTaxi-PhoneId': 'phone_id',
    'X-YaTaxi-UserId': 'user_id',
    'X-Yandex-Uid': 'yandex_uid',
    'X-Request-Language': 'ru',
}
VTB_PAY_URL = '/vtb/pay/url'
MAAS_PROBLEM_UI_SETTINGS = {
    'subscription_pay': {
        'acquiring_errors': {'051': const.KNOWN_PROBLEM_UI},
        'vtb_client_errors': {},
    },
    'url_to_support': common.URL_TO_SUPPORT,
}


async def make_request(taxi_maas):
    return await taxi_maas.post(
        '/4.0/maas/v1/subscription/pay/status',
        headers=HEADERS,
        params={'payment_id': 'payment_id'},
    )


@pytest.fixture(name='vtb_maas')
def _mock_vtb_maas(mockserver, load_json):
    def _mock(vtb_status):
        @mockserver.json_handler('/vtb-maas/api/0.1/subscription/pay/status')
        def _mock_vtb_maas(request):
            common.check_vtb_authorization(request)
            assert request.json['payment_id'] == 'payment_id'

            if vtb_status == 'UNKNOWN ERROR':
                return mockserver.make_response(
                    json=load_json('vtb_unknown_error.json'),
                )

            vtb_response = load_json('vtb_response.json')
            auth_status = vtb_response['payment']['auth']['status']
            auth_status['status'] = vtb_status
            if vtb_status == 'CREATED':
                vtb_response['payment']['url'] = VTB_PAY_URL
            elif vtb_status == 'ERROR':
                auth_status['response_code'] = '051'
                auth_status['response_descr'] = 'Known error'
            return mockserver.make_response(json=vtb_response)

    return _mock


@pytest.mark.translations(client_messages=const.PROBLEM_UI_TANKER_KEYS)
@pytest.mark.config(
    MAAS_PAYMENT_STATUS_POLLING={'default': 0, 'pending': 1, 'paying': 2},
    MAAS_PROBLEM_UI_SETTINGS_2=MAAS_PROBLEM_UI_SETTINGS,
)
@pytest.mark.pgsql('maas', files=['users.sql'])
@pytest.mark.parametrize(
    ('vtb_status', 'expected_status', 'expected_delay'),
    (
        ('UNDEFINED', 'pending', 1),
        ('CREATED', 'initiated', 0),
        ('PROCESSING', 'paying', 2),
        ('CANCELED', 'canceled', 0),
        ('SUCCESS', 'paid', 0),
        ('ERROR', 'failed', 0),
        ('UNKNOWN ERROR', 'failed', 0),
    ),
)
async def test_success(
        taxi_maas,
        vtb_maas,
        load_json,
        vtb_status: str,
        expected_status: str,
        expected_delay: int,
):
    vtb_maas(vtb_status=vtb_status)
    response = await make_request(taxi_maas)
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['status'] == expected_status
    assert response.headers['X-Polling-Delay'] == str(expected_delay)

    if vtb_status == 'UNKNOWN ERROR':
        url = response_body['problem_ui']['support_button']['url_to_support']
        common.check_support_url(
            url,
            issue='2',
            redirect_uri='https://m.taxi.yandex.ru/webview/maas/redirect?'
            'page=payment&source=pay',
        )
        del response_body['problem_ui']['support_button']
        del response_body['status']
        assert response_body == load_json('unknown_error_response.json')
        return

    if expected_status == 'initiated':
        assert response_body['url_to_vtb_pay'] == VTB_PAY_URL
    elif expected_status == 'failed':
        assert response_body['problem_ui'] == load_json('problem_ui.json')
