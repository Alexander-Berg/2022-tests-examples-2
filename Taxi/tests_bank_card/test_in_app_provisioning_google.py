import pytest

from tests_bank_card import common


@pytest.mark.parametrize('core_card_status_code', [200, 400, 404, 500])
async def test_get_prepared_data_http_statuses_google(
        taxi_bank_card, mockserver, core_card_mock, core_card_status_code,
):
    core_card_mock.set_http_status_code(core_card_status_code)
    if core_card_status_code != 200:
        core_card_mock.set_prepared_google_data(
            {'code': 'some code', 'message': 'some message'},
        )

    headers = common.default_headers()
    headers['X-Idempotency-Token'] = '1742D6DC-1D7D-49B7-A736-4E971226B56B'

    response = await taxi_bank_card.post(
        'v1/card/v1/googlepay/get_prepared_data',
        headers=headers,
        json={
            'card_id': 'cn',
            'wallet_id': 'wi',
            'device_id': 'di',
            'app_id': 'ai',
        },
    )

    assert response.status_code == core_card_status_code


@pytest.mark.parametrize(
    'locale,localized_text',
    [('ru', 'Яндекс Карта'), ('en', 'Yandex Card'), ('ch', 'Яндекс Карта')],
)
async def test_get_prepared_google_data_locale_google(
        taxi_bank_card, mockserver, core_card_mock, locale, localized_text,
):
    headers = common.default_headers()
    headers['X-Request-Language'] = locale
    headers['X-Idempotency-Token'] = '1742D6DC-1D7D-49B7-A736-4E971226B56B'

    response = await taxi_bank_card.post(
        'v1/card/v1/googlepay/get_prepared_data',
        headers=headers,
        json={
            'card_id': 'cn',
            'wallet_id': 'wi',
            'device_id': 'di',
            'app_id': 'ai',
        },
    )

    assert response.status_code == 200
    assert response.json()['display_name'] == localized_text


async def test_get_prepared_data_valid_proxy_google(
        taxi_bank_card, mockserver, core_card_mock,
):

    headers = common.default_headers()
    headers['X-Idempotency-Token'] = '1742D6DC-1D7D-49B7-A736-4E971226B56B'
    headers['X-Request-Language'] = 'en'

    response = await taxi_bank_card.post(
        'v1/card/v1/googlepay/get_prepared_data',
        headers=headers,
        json={
            'card_id': 'cn',
            'wallet_id': 'wi',
            'device_id': 'di',
            'app_id': 'ai',
        },
    )

    assert response.status_code == 200

    prepared_data = core_card_mock.prepared_google_data
    prepared_data['display_name'] = 'Yandex Card'

    assert response.json() == prepared_data


@pytest.mark.parametrize(
    'request_body',
    [
        {'card_id': '', 'wallet_id': '4', 'device_id': '4', 'app_id': '44'},
        {'card_id': '1', 'wallet_id': '', 'device_id': '1', 'app_id': '11'},
        {'card_id': '2', 'wallet_id': 'cb', 'device_id': '', 'app_id': '22'},
        {'card_id': '3', 'wallet_id': '3', 'device_id': '3', 'app_id': ''},
    ],
)
async def test_get_prepared_data_invalid_input_google(
        taxi_bank_card, mockserver, core_card_mock, request_body,
):
    headers = common.default_headers()
    headers['X-Idempotency-Token'] = '1742D6DC-1D7D-49B7-A736-4E971226B56B'

    response = await taxi_bank_card.post(
        'v1/card/v1/googlepay/get_prepared_data',
        headers=headers,
        json=request_body,
    )

    assert response.status_code == 400
