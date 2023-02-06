import pytest

from tests_cargo_corp import utils


RESPONSE_FIELDS = [
    'card_id',
    'expiration_month',
    'expiration_year',
    'number',
    'system',
]


def _get_headers(x_b2b_client_id, x_yandex_uid):
    return {'X-B2B-Client-Id': x_b2b_client_id, 'X-Yandex-Uid': x_yandex_uid}


@pytest.mark.parametrize(
    'cardstorage_code, expected_code', ((200, 200), (400, 500), (500, 500)),
)
@pytest.mark.parametrize(
    ('x_b2b_client_id', 'x_yandex_uid'),
    [(utils.CORP_CLIENT_ID, utils.YANDEX_UID)],
)
async def test_card_to_bound_list(
        taxi_cargo_corp,
        load_json,
        mockserver,
        x_b2b_client_id,
        x_yandex_uid,
        cardstorage_code,
        expected_code,
):
    cardstorage_response_json = (
        load_json('cardstorage_response.json')
        if cardstorage_code == 200
        else {'code': 'fail', 'message': 'big fail'}
    )

    @mockserver.json_handler('/cardstorage/v1/payment_methods')
    def _cardstorage_handler(request):
        assert request.json['yandex_uid'] == x_yandex_uid

        return mockserver.make_response(
            status=cardstorage_code, json=cardstorage_response_json,
        )

    response = await taxi_cargo_corp.post(
        '/v1/client/employee/card-to-bound/list',
        headers=_get_headers(x_b2b_client_id, x_yandex_uid),
    )

    assert response.status_code == expected_code
    if expected_code != 200:
        return

    response_json_available_cards = response.json()['available_cards']
    assert len(response_json_available_cards) == 1

    for field_name in RESPONSE_FIELDS:
        assert (
            response_json_available_cards[0][field_name]
            == cardstorage_response_json['available_cards'][0][field_name]
        )

    assert len(response_json_available_cards[0]) == len(RESPONSE_FIELDS)
