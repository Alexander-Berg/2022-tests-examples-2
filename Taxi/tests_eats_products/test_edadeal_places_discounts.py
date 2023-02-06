import pytest

from tests_eats_products import experiments
from tests_eats_products import utils


PLACES_LIMIT = 3
REQUEST_BODY = {
    'device_id': 'XXX',
    'location': {'latitude': 55.725326, 'longitude': 37.567051},
    'places_limit': PLACES_LIMIT,
}

CATALOG_REQUEST_ALL = {
    'blocks': [
        {
            'condition': {
                'init': {
                    'arg_name': 'business',
                    'arg_type': 'string',
                    'value': 'shop',
                },
                'type': 'eq',
            },
            'disable_filters': False,
            'round_eta_to_hours': False,
            'id': 'EDADEAL_SHOPS_ONLY',
            'limit': 3,
            'low': 0,
            'min_count': 0,
            'no_data': False,
            'type': 'open',
        },
    ],
    'location': {'latitude': 55.725326, 'longitude': 37.567051},
}

CATALOG_REQUEST_ONLY_SHOPS = {
    'blocks': [
        {
            'condition': {
                'init': {
                    'arg_name': 'business',
                    'arg_type': 'string',
                    'value': 'shop',
                },
                'type': 'eq',
            },
            'disable_filters': False,
            'round_eta_to_hours': False,
            'id': 'EDADEAL_SHOPS_ONLY',
            'limit': 3,
            'low': 0,
            'min_count': 0,
            'no_data': False,
            'type': 'open',
        },
    ],
    'condition': {
        'init': {
            'arg_name': 'business',
            'arg_type': 'string',
            'value': 'shop',
        },
        'type': 'eq',
    },
    'location': {'latitude': 55.725326, 'longitude': 37.567051},
}

EDADEAL_CONFIG = {
    'place_link_template': '',
    'exclude_alcohol_shops': True,
    'brands_to_exclude': [86579],
}


EATS_RETAIL_ALCOHOL_SHOPS = {
    '111219': {
        'rules': 'text.alcohol_shops.rules',
        'licenses': 'text.alcohol_shops.licenses',
        'rules_with_storage_info': {'full': {}},
        'storage_time': 48,
    },
}


@pytest.mark.parametrize(
    'expected_catalog_request',
    [
        pytest.param(CATALOG_REQUEST_ALL, id='request all'),
        pytest.param(
            CATALOG_REQUEST_ONLY_SHOPS,
            marks=experiments.REQUEST_SHOPS_ONLY_FROM_CATALOG,
            id='request only shops',
        ),
    ],
)
async def test_edadeal_places(
        load_json, mockserver, taxi_eats_products, expected_catalog_request,
):
    @mockserver.json_handler(utils.Handlers.CATALOG_FOR_LAYOUT)
    def _mock_eats_catalog(request):
        assert request.json == expected_catalog_request
        return load_json('catalog_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.EDADEAL_PLACES, json=REQUEST_BODY,
    )

    assert response.status_code == 200
    assert len(response.json()['places_block']['places']) == PLACES_LIMIT
    assert response.json() == load_json(
        'products_edadeal_places_response.json',
    )


async def test_edadeal_places_no_places(
        load_json, mockserver, taxi_eats_products,
):
    @mockserver.json_handler(utils.Handlers.CATALOG_FOR_LAYOUT)
    def _mock_eats_catalog(request):
        return load_json('catalog_response_no_places.json')

    response = await taxi_eats_products.post(
        utils.Handlers.EDADEAL_PLACES, json=REQUEST_BODY,
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'products_edadeal_places_response_no_places.json',
    )


async def test_edadeal_places_no_blocks(
        load_json, mockserver, taxi_eats_products,
):
    """
    Test that if no places are found in catalog, we return an empty
    result.
    """

    @mockserver.json_handler(utils.Handlers.CATALOG_FOR_LAYOUT)
    def _mock_eats_catalog(request):
        return load_json('catalog_response_no_blocks.json')

    response = await taxi_eats_products.post(
        utils.Handlers.EDADEAL_PLACES, json=REQUEST_BODY,
    )

    assert response.status_code == 200
    assert response.json()['places_block']['places'] == []


async def test_edadeal_places_cat_500(mockserver, taxi_eats_products):
    @mockserver.json_handler(utils.Handlers.CATALOG_FOR_LAYOUT)
    def _mock_eats_catalog(request):
        return mockserver.make_response(status=500)

    response = await taxi_eats_products.post(
        utils.Handlers.EDADEAL_PLACES, json=REQUEST_BODY,
    )

    assert response.status_code == 500


@pytest.mark.config(
    EATS_PRODUCTS_EDADEAL_INTEGRATION=EDADEAL_CONFIG,
    EATS_RETAIL_ALCOHOL_SHOPS=EATS_RETAIL_ALCOHOL_SHOPS,
)
async def test_edadeal_exclude_places(
        load_json, mockserver, taxi_eats_products,
):
    @mockserver.json_handler(utils.Handlers.CATALOG_FOR_LAYOUT)
    def _mock_eats_catalog(request):
        return load_json('catalog_response.json')

    response = await taxi_eats_products.post(
        utils.Handlers.EDADEAL_PLACES, json=REQUEST_BODY,
    )

    assert response.status_code == 200
    assert len(response.json()['places_block']['places']) == 1

    place = response.json()['places_block']['places'][0]
    assert place['brand_slug'] == 'picker_only'
