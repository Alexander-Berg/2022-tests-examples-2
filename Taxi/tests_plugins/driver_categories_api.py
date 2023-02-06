import json

import pytest
import werkzeug


INTERNAL_V2_CATEGORIES_RESPONSE = {
    'categories': [
        {
            'name': 'business',
            'taximeter_name': 'comfort',
            'db_cars_name': 'comfort',
        },
        {
            'name': 'business2',
            'taximeter_name': 'comfortplus',
            'db_cars_name': 'comfort_plus',
        },
        {'name': 'cargo'},
        {'name': 'child_tariff'},
        {
            'name': 'comfortplus',
            'taximeter_name': 'comfortplus',
            'db_cars_name': 'comfort_plus',
        },
        {'name': 'courier'},
        {'name': 'demostand'},
        {'name': 'econom'},
        {'name': 'eda'},
        {'name': 'express'},
        {'name': 'lavka'},
        {'name': 'limousine'},
        {'name': 'maybach'},
        {'name': 'minibus'},
        {'name': 'minivan'},
        {'name': 'mkk'},
        {'name': 'mkk_antifraud'},
        {'name': 'night'},
        {'name': 'park_vip', 'taximeter_name': 'vip', 'db_cars_name': 'vip'},
        {'name': 'personal_driver'},
        {'name': 'pool'},
        {'name': 'premium_suv'},
        {'name': 'premium_van'},
        {'name': 'promo'},
        {'name': 'selfdriving'},
        {'name': 'standart', 'taximeter_name': 'standard'},
        {'name': 'start'},
        {'name': 'suv'},
        {'name': 'trucking'},
        {'name': 'ultimate'},
        {
            'name': 'universal',
            'taximeter_name': 'wagon',
            'db_cars_name': 'wagon',
        },
        {
            'name': 'vip',
            'taximeter_name': 'business',
            'db_cars_name': 'business',
        },
    ],
    'updated_at': '2020-01-01T00:00:00.000Z',
}


@pytest.fixture(autouse=True)
def driver_categories_api_services(request, mockserver):
    marker = request.node.get_marker('driver_categories_api')

    @mockserver.handler('/driver-categories-api/v1/drivers/categories/bulk')
    def v1_drivers_categories_bulk(request):
        if not marker:
            return werkzeug.Response('', 200)
        categories_mock = marker.kwargs.get('categories_mock')
        return werkzeug.Response(categories_mock, 200)

    @mockserver.handler('/driver-categories-api/internal/v2/categories')
    def internal_v2_categories(request):
        assert request.headers['Content-Type'] == 'application/json'
        return werkzeug.Response(
            json.dumps(INTERNAL_V2_CATEGORIES_RESPONSE), 200,
        )
