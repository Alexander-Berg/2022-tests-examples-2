import pytest


@pytest.fixture(name='eats_smart_prices_applicator_cache', autouse=True)
def mock_smart_prices(mockserver, request):
    smart_price_settings = dict()

    marker = request.node.get_closest_marker('smart_prices_cache')
    if marker:
        smart_price_settings = marker.args[0]

    @mockserver.json_handler(
        'eats-smart-prices/internal/eats-smart-prices/v1/get_places_settings',
    )
    def _mock_get_places_settings(json_request):
        places = []
        for place_id, max_percent in smart_price_settings.items():
            places.append(
                {
                    'place_id': place_id,
                    'values_wiht_intervals': [
                        {
                            'max_percent': str(max_percent),
                            'starts': '2020-01-01T00:00:00Z',
                        },
                    ],
                },
            )
        return {'places': places}

    smart_price_items = dict()
    marker = request.node.get_closest_marker('smart_prices_items')
    if marker:
        smart_price_items = marker.args[0]

    @mockserver.json_handler(
        'eats-smart-prices/internal/eats-smart-prices/v1/get_items_settings',
    )
    def _mock_get_items_settings(json_request):
        places = []
        for place_id, place in smart_price_items.items():
            items = []
            for item_id, item in place['items'].items():
                items.append(
                    {
                        'item_id': item_id,
                        'values_wiht_intervals': [
                            {'value': item, 'starts': '2020-01-01T00:00:00Z'},
                        ],
                    },
                )
            places.append(
                {
                    'place_id': place_id,
                    'updated_at': place['updated_at'],
                    'items': items,
                },
            )
        return {'places': places}
