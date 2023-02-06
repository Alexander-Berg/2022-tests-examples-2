import aiohttp
import pytest

ENDPOINT = '/driver/v1/contractor-merch/v1/purchase'
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

TRANSLATIONS = {
    'error.offer_changed_or_expired.text': {
        'en': 'offer_changed_or_expired-tr',
    },
    'error.some_error_occured.text': {'en': 'some_error_occured-tr'},
}


async def test_ok(
        taxi_contractor_merch,
        stq,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_parks,
        mock_parks_replica,
):
    idempotency_token = 'qwerty'
    response = await taxi_contractor_merch.post(
        ENDPOINT,
        headers={**HEADERS, 'X-Idempotency-Token': idempotency_token},
        json={'offer_id': 'feed-id-1'},
    )

    assert response.status_code == 200, response.text

    assert mock_driver_profiles.driver_profiles.times_called == 0

    assert mock_feeds.fetch_by_id.next_call()['request'].json == {
        'channels': [
            'country:rus',
            'city:city1',
            'contractor:park_id_driver_id',
            'tag:bronze',
            'tag:silver',
            'tag:gold',
        ],
        'feed_id': 'feed-id-1',
        'locale': 'en',
        'service': 'contractor-marketplace',
    }

    assert response.json() == {'purchase_id': idempotency_token}
    assert stq.contractor_merch_purchase.has_calls
    task = stq.contractor_merch_purchase.next_call()
    assert task['id'] == f'{PARK_ID}_{DRIVER_ID}_{idempotency_token}'
    assert task['args'] == []
    kwargs = task['kwargs']
    assert kwargs['driver_id'] == 'driver_id'
    assert kwargs['park_id'] == 'park_id'
    assert kwargs['feed_id'] == 'feed-id-1'
    assert kwargs['idempotency_token'] == 'qwerty'
    assert kwargs['feed_payload'] == {
        'feeds_admin_id': 'feeds-admin-id-1',
        'price': '200.0000',
        'category': 'tire',
        'balance_payment': True,
        'title': 'Gift card (tire)',
        'name': 'RRRR',
        'partner': {'name': 'Apple'},
        'meta_info': {
            'display_on_main_screen': True,
            'daily_per_driver_limit': 1,
            'total_per_driver_limit': 2,
            'total_per_unique_driver_limit': 3,
            'barcode_params': {'is_send_enabled': True, 'type': 'ean13'},
            'priority_params': {'tag_name': 'gold', 'duration_minutes': 60},
        },
        'actions': [
            {'data': 'https://media.5ka.ru/', 'text': 'Медиа', 'type': 'link'},
        ],
        'place_id': 1,
        'imageUrl': 'yandex.ru',
        'categories': ['tire'],
        'offer_id': 'metric',
    }


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
async def test_expired_offer(
        taxi_contractor_merch,
        mockserver,
        stq,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_parks,
        mock_parks_replica,
):
    @mockserver.json_handler('/feeds/v1/fetch_by_id')
    async def _feed(request):
        return aiohttp.web.json_response(
            status=404, data={'code': '', 'message': ''},
        )

    idempotency_token = 'qwerty'
    response = await taxi_contractor_merch.post(
        ENDPOINT,
        headers={**HEADERS, 'X-Idempotency-Token': idempotency_token},
        json={'offer_id': 'feed-id-1'},
    )

    assert mock_driver_profiles.driver_profiles.times_called == 0

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': '400',
        'problem_description': {
            'code': 'offer_changed_or_expired',
            'localized_message': 'offer_changed_or_expired-tr',
        },
    }
