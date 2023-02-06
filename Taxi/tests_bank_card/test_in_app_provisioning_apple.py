import pytest

from tests_bank_card import common


@pytest.mark.parametrize('core_card_status_code', [200, 404, 500])
async def test_get_init_info_http_statuses(
        taxi_bank_card, mockserver, core_card_mock, core_card_status_code,
):
    core_card_mock.set_http_status_code(core_card_status_code)
    if core_card_status_code != 200:
        core_card_mock.set_card_info(
            {'code': 'some code', 'message': 'some message'},
        )

    response = await taxi_bank_card.post(
        'v1/card/v1/applepay/get_init_info',
        headers=common.default_headers(),
        json={'card_id': '1'},
    )

    assert response.status_code == core_card_status_code


@pytest.mark.parametrize('core_card_status_code', [200, 400, 404, 500])
async def test_get_prepared_data_http_statuses(
        taxi_bank_card, mockserver, core_card_mock, core_card_status_code,
):
    core_card_mock.set_http_status_code(core_card_status_code)
    if core_card_status_code != 200:
        core_card_mock.set_prepared_apple_data(
            {'code': 'some code', 'message': 'some message'},
        )

    headers = common.default_headers()
    headers['X-Idempotency-Token'] = '1742D6DC-1D7D-49B7-A736-4E971226B56B'

    response = await taxi_bank_card.post(
        'v1/card/v1/applepay/get_prepared_data',
        headers=headers,
        json={
            'card_id': '1',
            'certificates': ['ca', 'cb'],
            'nonce': 'n',
            'nonce_signature': 'nb',
        },
    )

    assert response.status_code == core_card_status_code


@pytest.mark.parametrize('payment_system', ['VISA', 'MIR', 'AMERICAN_EXPRESS'])
async def test_get_init_info_payment_system(
        taxi_bank_card, mockserver, core_card_mock, payment_system,
):
    core_card_mock.set_card_info_field('payment_system', payment_system)
    response = await taxi_bank_card.post(
        'v1/card/v1/applepay/get_init_info',
        headers=common.default_headers(),
        json={'card_id': '1'},
    )

    assert response.status_code == 200

    if payment_system in common.ACCEPTABLE_PAYMENT_SYSTEMS:
        assert response.json()['payment_system'] == payment_system
    else:
        assert 'payment_system' not in response.json()


@pytest.mark.parametrize(
    'locale,localized_text',
    [('ru', 'Яндекс Карта'), ('en', 'Yandex Card'), ('ch', 'Яндекс Карта')],
)
async def test_get_init_info_locale(
        taxi_bank_card, mockserver, core_card_mock, locale, localized_text,
):
    headers = common.default_headers()
    headers['X-Request-Language'] = locale

    response = await taxi_bank_card.post(
        'v1/card/v1/applepay/get_init_info',
        headers=headers,
        json={'card_id': '1'},
    )

    assert response.status_code == 200
    assert response.json()['localized_card_description'] == localized_text


async def test_get_init_info_valid_proxy(
        taxi_bank_card, mockserver, core_card_mock,
):
    response = await taxi_bank_card.post(
        'v1/card/v1/applepay/get_init_info',
        headers=common.default_headers(),
        json={'card_id': '1'},
    )

    assert response.status_code == 200

    assert response.json() == {
        'cardholder_name': core_card_mock.card_info['cardholder_name'],
        'primary_account_suffix': core_card_mock.card_info['last_pan_digits'],
        'localized_card_description': 'Яндекс Карта',
        'payment_system': 'VISA',
        'card_details': [],
    }


async def test_get_prepared_data_valid_proxy(
        taxi_bank_card, mockserver, core_card_mock,
):

    headers = common.default_headers()
    headers['X-Idempotency-Token'] = '1742D6DC-1D7D-49B7-A736-4E971226B56B'

    response = await taxi_bank_card.post(
        'v1/card/v1/applepay/get_prepared_data',
        headers=headers,
        json={
            'card_id': '1',
            'certificates': ['ca', 'cb'],
            'nonce': 'n',
            'nonce_signature': 'nb',
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        'cryptographic_otp': core_card_mock.prepared_apple_data[
            'cryptographic_otp'
        ],
        'ciphertext': core_card_mock.prepared_apple_data['ciphertext'],
        'ephemeral_public_key': core_card_mock.prepared_apple_data[
            'ephemeral_public_key'
        ],
    }


@pytest.mark.parametrize(
    'request_body',
    [
        {
            'card_id': '1',
            'certificates': ['ca', ''],
            'nonce': 'n',
            'nonce_signature': 'nb',
        },
        {
            'card_id': '1',
            'certificates': ['ca', 'cb'],
            'nonce': '',
            'nonce_signature': 'nb',
        },
        {
            'card_id': '1',
            'certificates': ['ca', 'cb'],
            'nonce': 'n',
            'nonce_signature': '',
        },
    ],
)
async def test_get_prepared_data_invalid_input(
        taxi_bank_card, mockserver, core_card_mock, request_body,
):
    headers = common.default_headers()
    headers['X-Idempotency-Token'] = '1742D6DC-1D7D-49B7-A736-4E971226B56B'

    response = await taxi_bank_card.post(
        'v1/card/v1/applepay/get_prepared_data',
        headers=headers,
        json=request_body,
    )

    assert response.status_code == 400
