import pytest

import common
import const

HEADERS = {
    'X-YaTaxi-PhoneId': 'phone_id',
    'X-YaTaxi-UserId': 'user_id',
    'X-Yandex-Uid': 'yandex_uid',
    'X-Idempotency-Token': 'idempotency',
    'X-Request-Language': 'ru',
}


async def make_request(taxi_maas):
    request = {
        'chosen_tariff_id': 'tariff_m',
        'method_type': 'googlepay',
        'method_id': 'qwertyasdf',
    }
    return await taxi_maas.post(
        '/4.0/maas/v1/subscription/pay/start', headers=HEADERS, json=request,
    )


def mock_services(mockserver, load_json, vtb_start_response_path: str):
    @mockserver.json_handler('/user-api/v2/user_phones/get')
    def _mock_user_api(request):
        assert request.json['id'] == 'phone_id'
        assert request.json['fields'] == ['personal_phone_id']

        response = load_json('user_api_response.json')
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal(request):
        assert request.json['id'] == 'personal-phone-id'

        return mockserver.make_response(
            json={'id': 'personal-phone-id', 'value': '+71234567890'},
        )

    @mockserver.json_handler('/vtb-maas/api/0.1/user/register')
    def _mock_vtb_maas_user_register(request):
        common.check_vtb_authorization(request)
        assert request.json['phone'] == '71234567890'

        return mockserver.make_response(json={'maas_user_id': 'maas-user-id'})

    @mockserver.json_handler('/vtb-maas/api/0.1/subscription/pay/start')
    def _mock_vtb_maas_pay_start(request):
        common.check_vtb_authorization(request)
        assert request.json == load_json('vtb_pay_start_request.json')

        return mockserver.make_response(
            json=load_json(vtb_start_response_path),
        )


@pytest.mark.config(
    MAAS_PAYMENT_REDIRECT_URLS=const.REDIRECT_URLS,
    MAAS_TARIFFS=common.get_maas_tariffs(),
)
@pytest.mark.parametrize(
    (),
    (
        pytest.param(id='Not user'),
        pytest.param(
            id='User already exists',
            marks=pytest.mark.pgsql('maas', files=['users.sql']),
        ),
    ),
)
async def test_success(taxi_maas, mockserver, load_json):
    mock_services(mockserver, load_json, 'vtb_pay_start_success.json')
    response = await make_request(taxi_maas)
    assert response.status_code == 200
    assert response.json() == {'payment_id': 'some_payment_id'}


@pytest.mark.translations(client_messages=const.PROBLEM_UI_TANKER_KEYS)
@pytest.mark.config(
    MAAS_PROBLEM_UI_SETTINGS_2={
        'subscription_pay': {
            'vtb_client_errors': {'42': const.KNOWN_PROBLEM_UI},
            'acquiring_errors': {},
        },
        'url_to_support': common.URL_TO_SUPPORT,
    },
    MAAS_PAYMENT_REDIRECT_URLS=const.REDIRECT_URLS,
    MAAS_TARIFFS=common.get_maas_tariffs(),
)
@pytest.mark.parametrize(
    ('vtb_error_response', 'response_path'),
    (
        pytest.param(
            'vtb_start_known_error.json',
            'known_error_response.json',
            id='Known error',
        ),
        pytest.param(
            'vtb_unknown_error.json',
            'unknown_error_response.json',
            id='Unknown error',
        ),
    ),
)
async def test_fail(
        taxi_maas,
        mockserver,
        load_json,
        vtb_error_response: str,
        response_path: str,
):
    mock_services(mockserver, load_json, vtb_error_response)
    response = await make_request(taxi_maas)
    assert response.status_code == 200
    response_json = response.json()

    try:
        url = response_json['problem_ui']['support_button']['url_to_support']
        common.check_support_url(url, issue='2')
        del response_json['problem_ui']['support_button']
    except KeyError:
        pass
    assert response_json == load_json(response_path)
