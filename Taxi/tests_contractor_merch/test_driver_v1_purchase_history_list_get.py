import dateutil
import pytest

from tests_contractor_merch import util


TRANSLATIONS = util.STQ_TRANSLATIONS

ENDPOINT = '/driver/v1/contractor-merch/v1/purchase_history/list'

PARK_ID = 'park_id'
DRIVER_ID = 'driver_id'
HEADERS = {
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.50',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'Accept-Language': 'en_GB',
}

EXPECTED_PURCHASE_1 = {
    'info': {
        'barcode_type': 'ean13',
        'created_at': '2021-07-02T14:00:00+0000',
        'promocode': 'Very_good_promocode',
        'status': 'fulfilled',
    },
    'offer': {
        'category_id': 'tire',
        'category_ids': ['tire'],
        'offer_data': {
            'offer_id': 'metric',
            'balance_payment': True,
            'category': 'tire',
            'name': 'RRRR',
            'partner': {'name': 'Apple'},
            'price': '123.0000',
            'price_with_currency': {
                'value': '123',
                'currency': 'RUB',
                'formatted': '123 ₽',
            },
            'title': 'Gift card (tire)',
            'categories': ['tire'],
            'actions': [
                {
                    'data': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    'text': 'Rick Astley',
                    'type': 'link',
                },
            ],
            'place_id': 1,
        },
        'offer_id': 'feed-id-2',
        'immutable_offer_id': 'feeds-admin-id-2',
        'price': '123.0000',
        'price_with_currency': {
            'value': '123',
            'currency': 'RUB',
            'formatted': '123 ₽',
        },
    },
}
EXPECTED_PURCHASE_2 = {
    'info': {
        'barcode_type': 'ean13',
        'created_at': '2021-07-01T14:00:00+0000',
        'promocode': '100/500',
        'status': 'fulfilled',
    },
    'offer': {
        'category_id': 'tire',
        'category_ids': ['tire'],
        'offer_data': {
            'offer_id': 'metric',
            'balance_payment': True,
            'category': 'tire',
            'name': 'RRRR',
            'partner': {'name': 'Apple'},
            'price': '200.0000',
            'price_with_currency': {
                'value': '200',
                'currency': 'RUB',
                'formatted': '200 ₽',
            },
            'title': 'Gift card (tire)',
            'categories': ['tire'],
            'actions': [
                {
                    'data': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    'text': 'Rick Astley',
                    'type': 'link',
                },
            ],
            'place_id': 1,
        },
        'offer_id': 'feed-id-1',
        'immutable_offer_id': 'feeds-admin-id-1',
        'price': '200.0000',
        'price_with_currency': {
            'value': '200',
            'currency': 'RUB',
            'formatted': '200 ₽',
        },
    },
}
EXPECTED_RESPONSE = {'purchases': [EXPECTED_PURCHASE_1, EXPECTED_PURCHASE_2]}


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.config(
    CONTRACTOR_MERCH_SUPPORTED_BARCODES={
        'ean13': {
            'render_url_template': 'https://ean13?barcode={promocode_number}',
            'url_text_tanker_key': (
                'notification_v1.success.linear_barcode_url_text'
            ),
        },
    },
)
@pytest.mark.pgsql('contractor_merch', files=['purchase_1.sql'])
@pytest.mark.pgsql('contractor_merch', files=['purchase_2.sql'])
async def test_ok(taxi_contractor_merch):
    response = await taxi_contractor_merch.post(
        ENDPOINT, headers={**HEADERS}, json={},
    )
    assert response.status == 200
    assert response.json() == EXPECTED_RESPONSE


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.config(
    CONTRACTOR_MERCH_SUPPORTED_BARCODES={
        'ean13': {
            'render_url_template': 'https://ean13?barcode={promocode_number}',
            'url_text_tanker_key': (
                'notification_v1.success.linear_barcode_url_text'
            ),
        },
    },
)
@pytest.mark.pgsql('contractor_merch', files=['purchase_1.sql'])
@pytest.mark.pgsql('contractor_merch', files=['purchase_2.sql'])
async def test_pagination_and_order(taxi_contractor_merch):
    created_at_1 = dateutil.parser.isoparse(
        EXPECTED_PURCHASE_1['info']['created_at'],
    )
    created_at_2 = dateutil.parser.isoparse(
        EXPECTED_PURCHASE_2['info']['created_at'],
    )
    assert (
        created_at_1 > created_at_2
    ), 'next response must contain older records!'

    response = await taxi_contractor_merch.post(
        ENDPOINT, headers={**HEADERS}, json={'limit': 1},
    )
    assert response.status == 200
    response_json = response.json()
    assert response_json == {
        'purchases': [EXPECTED_PURCHASE_1],
        'next_cursor': (
            '{\"created_at\":\"2021-07-02T14:00:00+0000\",'
            '\"vouchers_id\":\"idemp2\"}'
        ),
    }

    response = await taxi_contractor_merch.post(
        ENDPOINT,
        headers={**HEADERS},
        json={'limit': 1, 'cursor': response_json['next_cursor']},
    )
    assert response.status == 200
    response_json = response.json()
    assert response_json == {'purchases': [EXPECTED_PURCHASE_2]}


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.pgsql('contractor_merch', files=['few_promocodes_purchase.sql'])
async def test_offer_with_few_promocodes(taxi_contractor_merch, load_json):
    response = await taxi_contractor_merch.post(
        ENDPOINT, headers={**HEADERS}, json={},
    )

    assert response.status == 200
    assert response.json() == load_json('few_promocodes_response.json')


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.pgsql(
    'contractor_merch', files=['hyperlinked_promocode_purchase.sql'],
)
async def test_offer_with_hyperlinked_promocode(
        taxi_contractor_merch, load_json,
):
    response = await taxi_contractor_merch.post(
        ENDPOINT, headers={**HEADERS}, json={},
    )

    assert response.status == 200
    assert response.json() == load_json('hyperlinked_promocode_response.json')


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.pgsql(
    'contractor_merch', files=['priority_promocode_purchase.sql'],
)
async def test_offer_with_priority_params(taxi_contractor_merch, load_json):
    response = await taxi_contractor_merch.post(
        ENDPOINT, headers={**HEADERS}, json={},
    )

    assert response.status == 200
    assert response.json() == {
        'purchases': [
            {
                'info': {
                    'barcode_type': 'ean13',
                    'created_at': '2021-07-02T14:00:00+0000',
                    'promocode': 'Very_good_promocode',
                    'status': 'fulfilled',
                },
                'offer': {
                    'category_id': 'tire',
                    'category_ids': ['tire'],
                    'offer_data': {
                        'offer_id': 'metric',
                        'balance_payment': True,
                        'category': 'tire',
                        'name': 'RRRR',
                        'partner': {'name': 'Apple'},
                        'price': '123.0000',
                        'price_with_currency': {
                            'value': '123',
                            'currency': 'RUB',
                            'formatted': '123 ₽',
                        },
                        'title': 'Gift card (tire)',
                        'categories': ['tire'],
                        'actions': [
                            {
                                'data': (
                                    'https://www.youtube.com/'
                                    'watch?v=dQw4w9WgXcQ'
                                ),
                                'text': 'Rick Astley',
                                'type': 'link',
                            },
                        ],
                        'place_id': 1,
                    },
                    'offer_id': 'feed-id-2',
                    'immutable_offer_id': 'feeds-admin-id-2',
                    'price': '123.0000',
                    'price_with_currency': {
                        'value': '123',
                        'currency': 'RUB',
                        'formatted': '123 ₽',
                    },
                },
            },
        ],
    }
