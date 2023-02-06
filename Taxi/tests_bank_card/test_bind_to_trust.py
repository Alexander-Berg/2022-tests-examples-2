import pytest

from tests_bank_card import common


@pytest.mark.parametrize('core_code', [200, 400, 404])
async def test_trust(taxi_bank_card, mockserver, core_card_mock, core_code):
    headers = common.headers_with_idemp_token()

    core_card_mock.http_status_code = core_code

    response = await taxi_bank_card.post(
        'v1/card/v1/bind_to_trust',
        headers=headers,
        json={'card_id': common.CARD_ID},
    )

    assert response.status_code == core_code
    assert core_card_mock.bind_to_trust_handler.times_called == 1


@pytest.mark.parametrize(
    'missing_header, code',
    [
        ('X-Yandex-BUID', 401),
        ('X-YaBank-SessionUUID', 401),
        ('X-Idempotency-Token', 400),
    ],
)
async def test_trust_missing_headers(
        taxi_bank_card, mockserver, core_card_mock, missing_header, code,
):
    headers = common.headers_with_idemp_token()

    headers.pop(missing_header)

    core_card_mock.http_status_code = 200

    response = await taxi_bank_card.post(
        'v1/card/v1/bind_to_trust',
        headers=headers,
        json={'card_id': common.CARD_ID},
    )

    assert response.status_code == code
    assert core_card_mock.bind_to_trust_handler.times_called == 0
