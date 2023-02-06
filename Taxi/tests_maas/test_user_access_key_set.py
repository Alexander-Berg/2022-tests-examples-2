import pytest

import common
import const

REDIRECT_URLS = {
    'succeed': 'https://succeed-access-key-set',
    'declined': 'https://failed-access-key-set',
    'canceled': 'https://canceled-access-key-set',
}

CARD = 'card'
GOOGLEPAY = 'googlepay'


async def _make_request(taxi_maas, method):
    headers = {
        'X-YaTaxi-PhoneId': 'phone_id',
        'X-YaTaxi-UserId': 'user_id',
        'X-Yandex-Uid': 'yandex_uid',
        'X-Request-Language': 'ru',
        'X-Idempotency-Token': 'idempotency',
    }
    request = {'method_type': method}
    if method != CARD:
        request['method_id'] = 'qwertyasdf'
    return await taxi_maas.post(
        '/4.0/maas/v1/user/access-key/set', headers=headers, json=request,
    )


@pytest.mark.config(
    MAAS_PROBLEM_UI_SETTINGS_2={
        'access_key_set': {
            'vtb_client_errors': {'42': const.KNOWN_PROBLEM_UI},
            'acquiring_errors': {},
        },
        'url_to_support': common.URL_TO_SUPPORT,
    },
    MAAS_ACCESS_KEY_REDIRECT_URLS=REDIRECT_URLS,
)
@pytest.mark.translations(client_messages=const.PROBLEM_UI_TANKER_KEYS)
@pytest.mark.pgsql('maas', files=['users.sql'])
@pytest.mark.parametrize(
    'vtb_response_id, maas_response_id, method',
    (
        ('success', 'success', CARD),
        ('success_without_url', 'success_without_url', GOOGLEPAY),
        ('success_without_url', 'unknown_error', CARD),
        ('known_error', 'known_error', CARD),
        ('unknown_error', 'unknown_error', CARD),
    ),
)
async def test_full(
        taxi_maas,
        mockserver,
        load_json,
        vtb_response_id: str,
        maas_response_id: str,
        method: str,
):
    @mockserver.json_handler('/vtb-maas/api/0.1/user/key')
    def _mock_vtb_maas(request):
        common.check_vtb_authorization(request)
        expected_vtb_request = load_json('expected_vtb_request.json')
        if method == CARD:
            del expected_vtb_request['pay_data']['payment_token']
            expected_vtb_request['pay_data']['payment_method'] = 'CARD'
        assert request.json == expected_vtb_request

        return mockserver.make_response(
            json=load_json(f'vtb_responses/{vtb_response_id}.json'),
        )

    response = await _make_request(taxi_maas, method)
    assert response.status_code == 200
    expected_response = load_json(
        f'expected_responses/{maas_response_id}.json',
    )
    response_body = response.json()
    if maas_response_id == 'unknown_error':
        url = response_body['problem_ui']['support_button']['url_to_support']
        common.check_support_url(
            url,
            issue='1',
            redirect_uri='https://m.taxi.yandex.ru/webview/maas/redirect?'
            'page=payment&source=pay',
        )
        del response_body['problem_ui']['support_button']
    assert response_body == expected_response
