import pytest

from tests_bank_card_pcidss import common


@pytest.mark.parametrize('response_status', [200, 400, 404])
async def test_set_pin(
        taxi_bank_card_pcidss, core_card_mock, response_status, mockserver,
):
    headers = common.default_headers()
    headers['X-Idempotency-Token'] = '0F8E6294-3F6D-4118-B343-FAF84706654B'

    core_card_mock.set_http_status_code(response_status)

    if response_status != 200:
        core_card_mock.set_pin_set_body(
            {'code': 'some_code', 'message': 'some_message'},
        )

    response = await taxi_bank_card_pcidss.post(
        '/v1/card/v1/set_pin',
        headers=headers,
        json={'card_id': '123', 'pin': '1234'},
    )

    assert response.status_code == response_status


@pytest.mark.parametrize('response_status', [200, 400, 404])
async def test_details_get(
        taxi_bank_card_pcidss, core_card_mock, response_status, mockserver,
):
    core_card_mock.set_http_status_code(response_status)

    if response_status != 200:
        core_card_mock.set_get_details_body(
            {'code': 'some_code', 'message': 'some_message'},
        )

    response = await taxi_bank_card_pcidss.post(
        '/v1/card/v1/get_details',
        headers=common.default_headers(),
        json={'card_id': '123'},
    )

    assert response.status_code == response_status


async def test_set_pin_hp(taxi_bank_card_pcidss, core_card_mock, mockserver):
    headers = common.default_headers()
    headers['X-Idempotency-Token'] = '0F8E6294-3F6D-4118-B343-FAF84706654B'

    response = await taxi_bank_card_pcidss.post(
        '/v1/card/v1/set_pin',
        headers=headers,
        json={'card_id': '123', 'pin': '1234'},
    )

    assert response.status_code == 200
    assert response.json() == core_card_mock.pin_set_body


async def test_get_details_hp(
        taxi_bank_card_pcidss, core_card_mock, mockserver,
):
    headers = common.default_headers()

    response = await taxi_bank_card_pcidss.post(
        '/v1/card/v1/get_details', headers=headers, json={'card_id': '123'},
    )

    assert response.status_code == 200
    assert response.json() == core_card_mock.details_get_body
