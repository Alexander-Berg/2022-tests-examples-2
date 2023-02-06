import pytest

from . import utils as test_utils

CODEGEN_HANDLER_URL = 'driver/v1/loyalty/v1/cards'


@pytest.mark.parametrize(
    'position,expected_code,expected_response',
    [
        ([37.590533, 55.733863], 200, 'expected_response1.json'),
        ([39.590533, 55.733863], 200, 'expected_response2.json'),
        ([33.590533, 55.733863], 200, 'expected_response3.json'),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.now('2019-03-10T08:35:00+0300')
async def test_driver_loyalty_cards(
        taxi_loyalty, load_json, position, expected_code, expected_response,
):
    response = await taxi_loyalty.post(
        CODEGEN_HANDLER_URL,
        json={'position': position, 'timezone': 'Europe/Moscow'},
        headers=test_utils.get_auth_headers(
            'driver_db_id1', 'driver_uuid1', 'Taximeter 8.80 (562)',
        ),
    )

    assert response.status_code == expected_code
    assert response.json() == load_json('response/' + expected_response)


@pytest.mark.config(TVM_ENABLED=True)
async def test_driver_loyalty_cards_points_button(taxi_loyalty, load_json):
    response = await taxi_loyalty.post(
        CODEGEN_HANDLER_URL,
        json={'position': [37.590533, 55.733863], 'timezone': 'Europe/Moscow'},
        headers=test_utils.get_auth_headers(
            'driver_db_id1', 'driver_uuid1', 'Taximeter 9.70 (562)',
        ),
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'response/expected_response_points_button.json',
    )


@pytest.mark.config(
    LOYALTY_CARDS={
        'tinkoff': {
            'id': 'tinkoff_id',
            'title': 'loyalty.cards.tinkoff_card_title',
            'subtitle': 'loyalty.cards.tinkoff_card_subtitle',
            'image': 'http://',
            'description': 'loyalty.cards.tinkoff_card_description',
            'details': [
                {
                    'title': 'loyalty.cards.cashback_title',
                    'detail': 'loyalty.cards.cashback_detail',
                },
                {
                    'title': 'loyalty.cards.bonus_title',
                    'detail': 'loyalty.cards.bonus_detail',
                    'subtitle': 'loyalty.cards.bonus_subdetail',
                },
            ],
            'button': {
                'title': 'loyalty.cards.tinkoff_button_title',
                'payload': {
                    'type': 'navigate_to_bank_url_with_extra',
                    'data': {
                        'url': 'http://some_nice_url',
                        'javascript': 'some code, lol',
                        'bank_id': 'tinkoff',
                    },
                    'metadata': 'tinkoff_metadata',
                },
            },
        },
    },
    LOYALTY_CARDS_LOCATIONS={'moscow': {'tinkoff': []}},
    TVM_ENABLED=True,
)
@pytest.mark.now('2019-03-10T08:35:00+0300')
async def test_driver_loyalty_card_with_url(taxi_loyalty, load_json):
    response = await taxi_loyalty.post(
        CODEGEN_HANDLER_URL,
        json={'position': [37.590533, 55.733863], 'timezone': 'Europe/Moscow'},
        headers=test_utils.get_auth_headers(
            'driver_db_id1', 'driver_uuid1', 'Taximeter 9.70 (562)',
        ),
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'response/expected_response_url_button.json',
    )


@pytest.mark.parametrize(
    'version, expected_response',
    (
        (
            'Taximeter 9.80 (562)',
            'response/expected_response_multiple_buttons.json',
        ),
        ('Taximeter 9.60 (562)', 'response/expected_response_url_button.json'),
    ),
)
@pytest.mark.config(
    LOYALTY_CARDS={
        'tinkoff': {
            'id': 'tinkoff_id',
            'title': 'loyalty.cards.tinkoff_card_title',
            'subtitle': 'loyalty.cards.tinkoff_card_subtitle',
            'image': 'http://',
            'description': 'loyalty.cards.tinkoff_card_description',
            'details': [
                {
                    'title': 'loyalty.cards.cashback_title',
                    'detail': 'loyalty.cards.cashback_detail',
                },
                {
                    'title': 'loyalty.cards.bonus_title',
                    'detail': 'loyalty.cards.bonus_detail',
                    'subtitle': 'loyalty.cards.bonus_subdetail',
                },
            ],
            'button': {
                'title': 'loyalty.cards.tinkoff_button_title',
                'accent': True,
                'payload': {
                    'type': 'navigate_to_bank_url_with_extra',
                    'data': {
                        'url': 'http://some_nice_url',
                        'javascript': 'some code, lol',
                        'bank_id': 'tinkoff',
                    },
                    'metadata': 'tinkoff_metadata',
                },
            },
            'button_alternative': {
                'title': 'loyalty.cards.tinkoff_button_bind_title',
                'accent': False,
                'payload': {
                    'type': 'navigate_to_bank_form_to_link_card',
                    'data': {
                        'url': 'http://other_nice_url',
                        'javascript': 'other code',
                        'bank_id': 'tinkoff',
                    },
                    'metadata': 'tinkoff_metadata',
                },
            },
        },
    },
    LOYALTY_CARDS_LOCATIONS={'moscow': {'tinkoff': []}},
    TVM_ENABLED=True,
)
@pytest.mark.now('2019-03-10T08:35:00+0300')
async def test_driver_loyalty_card_binding(
        taxi_loyalty, load_json, version, expected_response,
):
    response = await taxi_loyalty.post(
        CODEGEN_HANDLER_URL,
        json={'position': [37.590533, 55.733863], 'timezone': 'Europe/Moscow'},
        headers=test_utils.get_auth_headers(
            'driver_db_id1', 'driver_uuid1', version,
        ),
    )

    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
