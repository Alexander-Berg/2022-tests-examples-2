import pytest

import common
import const


async def _make_request(taxi_maas):
    headers = {
        'X-YaTaxi-PhoneId': 'phone_id',
        'X-YaTaxi-UserId': 'user_id',
        'X-Yandex-Uid': 'yandex_uid',
        'X-Request-Language': 'ru',
    }
    return await taxi_maas.post(
        '/4.0/maas/v1/user/access-key/status',
        headers=headers,
        params={'operation_id': 'operation_id'},
    )


@pytest.fixture(name='vtb_maas')
def _mock_vtb_maas(mockserver, load_json):
    def _mock(vtb_status):
        @mockserver.json_handler('/vtb-maas/api/0.1/pay/status')
        def _mock_vtb_maas(request):
            common.check_vtb_authorization(request)
            assert request.json['payment_id'] == 'operation_id'

            if vtb_status == 'UNKNOWN ERROR':
                return mockserver.make_response(
                    json=load_json('vtb_unknown_error.json'),
                )

            vtb_response = load_json('vtb_response.json')
            auth_status = vtb_response['payment']['auth']['status']
            auth_status['status'] = vtb_status
            if vtb_status == 'ERROR':
                auth_status['response_code'] = '051'
                auth_status['response_descr'] = 'Known error'
            return mockserver.make_response(json=vtb_response)

    return _mock


@pytest.mark.translations(client_messages=const.PROBLEM_UI_TANKER_KEYS)
@pytest.mark.pgsql('maas', files=['users.sql'])
@pytest.mark.config(
    MAAS_ACCESS_KEY_STATUS_POLLING={'default': 0, 'processing': 2},
    MAAS_PROBLEM_UI_SETTINGS_2={
        'access_key_set': {
            'vtb_client_errors': {},
            'acquiring_errors': {'051': const.KNOWN_PROBLEM_UI},
        },
        'url_to_support': common.URL_TO_SUPPORT,
    },
)
@pytest.mark.parametrize(
    ('vtb_status', 'expected_status', 'expected_delay'),
    (
        ('UNDEFINED', 'processing', 2),
        ('CREATED', 'processing', 2),
        ('PROCESSING', 'processing', 2),
        ('CANCELED', 'canceled', 0),
        ('SUCCESS', 'success', 0),
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
    response = await _make_request(taxi_maas)
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['status'] == expected_status
    assert response.headers['X-Polling-Delay'] == str(expected_delay)
    if vtb_status == 'UNKNOWN ERROR':
        url = response_body['problem_ui']['support_button']['url_to_support']
        common.check_support_url(
            url,
            issue='1',
            redirect_uri='https://m.taxi.yandex.ru/webview/maas/redirect?'
            'page=payment&source=pay',
        )
        del response_body['problem_ui']['support_button']
        del response_body['status']
        assert response_body == load_json('unknown_error_response.json')
        return

    if expected_status == 'failed':
        assert response_body['problem_ui'] == load_json('problem_ui.json')
