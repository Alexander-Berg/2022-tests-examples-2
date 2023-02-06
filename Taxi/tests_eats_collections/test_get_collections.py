import copy

import pytest

COMMON_PARAMS = {
    'longitude': 37.596947,
    'latitude': 55.694901,
    'showTime': '2020-04-01T05:00:00Z',
}
HEADERS = {
    'X-Device-Id': 'device-id',
    'X-Platform': 'ios_app',
    'X-App-Version': '2.1.2',
}

USE_EATS_CATALOG = pytest.mark.experiments3(
    name='eats_collections_use_eats_catalog_places',
    consumers=['eats-collections/places'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)


@pytest.mark.now('2020-04-01T14:00:00Z')
async def test_get_collections(taxi_eats_collections):
    response = await taxi_eats_collections.get(
        '/eats-collections/v1/collections',
        headers=HEADERS,
        params=COMMON_PARAMS,
    )
    assert response.status_code == 200
    assert response.json() == {'payload': {'collections': []}}


@pytest.mark.now('2020-04-01T14:00:00Z')
@pytest.mark.experiments3(filename='experiments.json')
async def test_get_collection_200(
        taxi_eats_collections, load_json, mockserver,
):
    @mockserver.json_handler('/eda-catalog/v1/collections/search')
    def _catalog_search(request):
        return load_json('catalog_response.json')

    response = await taxi_eats_collections.get(
        '/eats-collections/v1/collections/test_collection',
        headers=HEADERS,
        params=COMMON_PARAMS,
    )
    assert response.status_code == 200
    assert response.json() == {'payload': load_json('test_collection.json')}, [
        item['place']['place']['slug']
        for item in response.json()['payload']['items']
    ]


@pytest.mark.now('2020-09-28T11:10:00Z')
@pytest.mark.experiments3(filename='experiments_no_suitable_by_prefix.json')
async def test_get_collections_no_suitable_by_prefix(
        taxi_eats_collections, mockserver,
):
    response = await taxi_eats_collections.get(
        '/eats-collections/v1/collections',
        headers=HEADERS,
        params=COMMON_PARAMS,
    )
    assert response.status_code == 200
    assert response.json() == {'payload': {'collections': []}}


@pytest.mark.parametrize(
    'catalog_url, catalog_response',
    [
        pytest.param(
            '/eda-catalog/v1/collections/search',
            'catalog_response.json',
            id='eda-catalog',
        ),
        pytest.param(
            '/eats-catalog/internal/v1/places',
            'eats_catalog_response.json',
            marks=USE_EATS_CATALOG,
            id='eats-catalog',
        ),
    ],
)
@pytest.mark.now('2020-04-01T14:00:00Z')
@pytest.mark.experiments3(filename='experiments_prefix_match.json')
async def test_get_collections_prefix_match(
        taxi_eats_collections,
        load_json,
        mockserver,
        catalog_url,
        catalog_response,
):
    @mockserver.json_handler(catalog_url)
    def _catalog_search(request):
        return load_json(catalog_response)

    response = await taxi_eats_collections.post(
        '/internal/v1/collections/',
        json={
            'longitude': 37.596947,
            'latitude': 55.694901,
            'show_time': '2020-04-01T05:00:00Z',
            'device_id': 'device-id',
            'platform': 'ios_app',
            'app_version': '2.1.2',
        },
    )
    assert response.status_code == 200

    body = response.json()
    assert body.get('payload') is not None

    payload = body.get('payload')
    assert payload.get('collections') is not None

    collections = payload['collections']
    assert len(collections) == 1
    assert collections[0]['slug'] == 'has_prefix'


@pytest.mark.now('2020-04-01T14:00:00Z')
@pytest.mark.experiments3(filename='experiments.json')
async def test_get_collection_200_unavailable(
        taxi_eats_collections, mockserver,
):
    @mockserver.json_handler('/eda-catalog/v1/collections/search')
    def _catalog_search(request):
        return {'payload': {'strategyPlaces': [{'id': 0, 'places': []}]}}

    response = await taxi_eats_collections.get(
        '/eats-collections/v1/collections/test_collection',
        headers=HEADERS,
        params={
            'longitude': 55.694901,
            'latitude': 37.296947,
            'showTime': '2020-04-01T15:00:00Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'payload': {
            'badgeImageUrl': None,
            'collectionType': 'collection',
            'description': 'Длинное описание этой коллекции',
            'heroPhotoUrl': None,
            'isAvailable': False,
            'items': [],
            'slug': 'test_collection',
            'title': 'Тестовая коллекция',
        },
    }


@pytest.mark.now('2020-04-01T14:00:00Z')
@pytest.mark.experiments3(filename='experiments.json')
async def test_get_collection_200_catalog_unavailable(
        taxi_eats_collections, mockserver,
):
    @mockserver.json_handler('/eda-catalog/v1/collections/search')
    def _catalog_search(request):
        return mockserver.make_response(
            'Internal error of some sort', status=500,
        )

    response = await taxi_eats_collections.get(
        '/eats-collections/v1/collections/test_collection',
        headers=HEADERS,
        params=COMMON_PARAMS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'payload': {
            'badgeImageUrl': (
                '/images/1387779/093b79ca99e372db744c94966a4d2937.png'
            ),
            'collectionType': 'collection',
            'description': 'Длинное описание этой коллекции',
            'heroPhotoUrl': (
                '/images/1387779/00cca90c2f39ec1f7f8465bdd8c9027d-{w}x{h}.jpg'
            ),
            'isAvailable': False,
            'items': [],
            'slug': 'test_collection',
            'title': 'Тестовая коллекция',
        },
    }


async def test_get_collection_404(taxi_eats_collections):
    response = await taxi_eats_collections.get(
        '/eats-collections/v1/collections/non_existent_collection',
        params=COMMON_PARAMS,
        headers=HEADERS,
    )
    assert response.status_code == 404
    assert response.json() == [
        {
            'title': 'Collection non_existent_collection not found',
            'code': '404',
            'source': None,
            'meta': None,
        },
    ]


@pytest.mark.now('2020-04-01T14:00:00Z')
@pytest.mark.experiments3(filename='experiments.json')
async def test_get_collection_500_no_catalog(taxi_eats_collections):
    response = await taxi_eats_collections.get(
        '/eats-collections/v1/collections/test_collection_2',
        params=COMMON_PARAMS,
        headers=HEADERS,
    )
    assert response.status_code == 500
    assert response.json() == [
        {
            'title': (
                'Experiment eats_collections_test_collection_2 found by '
                'prefix, but slug value doesn\'t match: test_collection'
            ),
            'code': '500',
            'source': None,
            'meta': None,
        },
    ]


@pytest.mark.parametrize(
    'catalog_url, catalog_response',
    [
        pytest.param(
            '/eda-catalog/v1/collections/search',
            'catalog_response_2_searches.json',
            id='eda-catalog',
        ),
        pytest.param(
            '/eats-catalog/internal/v1/places',
            'eats_catalog_response_2_blocks.json',
            marks=USE_EATS_CATALOG,
            id='eats-catalog',
        ),
    ],
)
@pytest.mark.now('2020-04-01T14:00:00Z')
@pytest.mark.experiments3(filename='experiments.json')
async def test_get_collections_internal(
        taxi_eats_collections,
        load_json,
        mockserver,
        catalog_url,
        catalog_response,
):
    @mockserver.json_handler(catalog_url)
    def _catalog_search(request):
        return load_json(catalog_response)

    response = await taxi_eats_collections.post(
        '/internal/v1/collections/',
        json={
            'longitude': 37.596947,
            'latitude': 55.694901,
            'show_time': '2020-04-01T05:00:00Z',
            'device_id': 'device-id',
            'platform': 'ios_app',
            'app_version': '2.1.2',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'payload': {
            'collections': [
                {
                    'description': 'Длинное описание этой коллекции',
                    'slug': 'test_collection',
                    'title': 'Тестовая коллекция',
                    'items_count': 2,
                },
            ],
        },
    }


@pytest.mark.parametrize(
    'catalog_url, catalog_response',
    [
        pytest.param(
            '/eda-catalog/v1/collections/search',
            'catalog_response_invalid_id.json',
            id='eda-catalog',
        ),
        pytest.param(
            '/eats-catalog/internal/v1/places',
            'eats_catalog_response_invalid_id.json',
            marks=USE_EATS_CATALOG,
            id='eats-catalog',
        ),
    ],
)
@pytest.mark.now('2020-04-01T14:00:00Z')
@pytest.mark.experiments3(filename='experiments.json')
async def test_get_collections_internal_empty(
        taxi_eats_collections,
        load_json,
        mockserver,
        catalog_url,
        catalog_response,
):
    @mockserver.json_handler(catalog_url)
    def _catalog_search(request):
        return load_json(catalog_response)

    response = await taxi_eats_collections.post(
        '/internal/v1/collections/',
        json={
            'longitude': 37.596947,
            'latitude': 55.694901,
            'show_time': '2020-04-01T05:00:00Z',
            'device_id': 'device-id',
            'platform': 'ios_app',
            'app_version': '2.1.2',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'payload': {'collections': []}}


@pytest.mark.now('2020-04-01T14:00:00Z')
@pytest.mark.experiments3(filename='experiments.json')
async def test_get_collections_internal_no_matched(taxi_eats_collections):
    response = await taxi_eats_collections.post(
        '/internal/v1/collections/',
        json={
            'longitude': 55.596947,
            'latitude': 55.694901,
            'show_time': '2020-04-01T05:00:00Z',
            'device_id': 'device-id',
            'platform': 'ios_app',
            'app_version': '2.1.2',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'payload': {'collections': []}}


@pytest.mark.parametrize(
    'positions,expected_slugs_order',
    [
        ([None, None], ['coffeemania_1', 'coffeemania_2']),
        (
            [3, 1, None, None],
            [
                'coffeemania_2',
                'coffeemania_3',
                'coffeemania_1',
                'coffeemania_4',
            ],
        ),
        (
            [None, None, None, 1, None, None],
            [
                'coffeemania_4',
                'coffeemania_1',
                'coffeemania_2',
                'coffeemania_3',
                'coffeemania_5',
                'coffeemania_6',
            ],
        ),
        (
            [None, None, 1, 1],
            [
                'coffeemania_3',
                'coffeemania_4',
                'coffeemania_1',
                'coffeemania_2',
            ],
        ),
        (
            [None, None, 100, 1],
            [
                'coffeemania_4',
                'coffeemania_1',
                'coffeemania_2',
                'coffeemania_3',
            ],
        ),
    ],
)
@pytest.mark.now('2020-04-01T14:00:00Z')
async def test_get_collections_item_positions(
        taxi_eats_collections,
        load_json,
        mockserver,
        experiments3,
        positions,
        expected_slugs_order,
):
    experiments_json = load_json('experiments_item_positions.json')
    catalog_response_json = {
        'payload': {'strategyPlaces': [{'id': 0, 'places': []}]},
    }
    catalog_response_place_raw = load_json(
        'catalog_response_place_item_positions.json',
    )
    for i, position in enumerate(positions, start=1):
        item = {
            'meta': {
                'description': 'Тут текст о том, чем хороша кофемания',
                'informationBlocks': [],
            },
            'place_id': i,
        }
        if position is not None:
            item['position'] = position
        experiments_json['experiments'][0]['clauses'][0]['value']['actions'][
            'addMetaToPlace'
        ].append(item)
        experiments_json['experiments'][0]['clauses'][0]['value'][
            'searchConditions'
        ]['arguments']['place_ids'].append(i)
        catalog_response_place = copy.deepcopy(catalog_response_place_raw)
        catalog_response_place['place']['slug'] = f'coffeemania_{i}'
        catalog_response_place['place']['id'] = i
        catalog_response_json['payload']['strategyPlaces'][0]['places'].append(
            catalog_response_place,
        )

    experiments3.add_experiments_json(experiments_json)

    @mockserver.json_handler('/eda-catalog/v1/collections/search')
    def _catalog_search(request):
        return catalog_response_json

    response = await taxi_eats_collections.get(
        '/eats-collections/v1/collections/test_collection',
        headers=HEADERS,
        params=COMMON_PARAMS,
    )
    assert response.status_code == 200
    slugs = [
        item['place']['place']['slug']
        for item in response.json()['payload']['items']
    ]
    assert slugs == expected_slugs_order


@pytest.mark.now('2020-04-01T14:00:00Z')
@pytest.mark.experiments3(filename='experiments.json')
@pytest.mark.parametrize(
    'request_language, collections_count',
    (
        pytest.param('', 1, id='fallback'),
        pytest.param('ru', 1, id='match'),
        pytest.param('en', 0, id='mismatch'),
        pytest.param(None, 1, id='none'),
    ),
)
async def test_get_collections_locale_missmatch(
        taxi_eats_collections,
        mockserver,
        load_json,
        request_language,
        collections_count,
):
    """
    Проверяем что если коллекция не матчится в запрошенную локаль,
    она будет отфильтрована
    """

    @mockserver.json_handler('/eda-catalog/v1/collections/search')
    def _catalog_search(request):
        return load_json('catalog_response.json')

    response = await taxi_eats_collections.post(
        '/internal/v1/collections/',
        json={
            'longitude': 37.596947,
            'latitude': 55.694901,
            'show_time': '2020-04-01T05:00:00Z',
            'device_id': 'device-id',
            'platform': 'ios_app',
            'app_version': '2.1.2',
        },
        headers={'x-request-language': request_language},
    )
    assert response.status_code == 200
    collections = response.json()['payload']['collections']
    assert len(collections) == collections_count


@pytest.mark.now('2020-04-01T14:00:00Z')
@pytest.mark.experiments3(filename='experiments-no-locale.json')
@pytest.mark.parametrize(
    'request_language, collections_count',
    (
        pytest.param('', 1, id='fallback'),
        pytest.param('ru', 1, id='match'),
        pytest.param('en', 1, id='mismatch'),
        pytest.param(None, 1, id='none'),
    ),
)
async def test_get_collections_no_locale_missmatch(
        taxi_eats_collections,
        mockserver,
        load_json,
        request_language,
        collections_count,
):
    """
    Проверяем что если коллекция не матчится в запрошенную локаль,
    она будет отфильтрована
    """

    @mockserver.json_handler('/eda-catalog/v1/collections/search')
    def _catalog_search(request):
        return load_json('catalog_response.json')

    response = await taxi_eats_collections.post(
        '/internal/v1/collections/',
        json={
            'longitude': 37.596947,
            'latitude': 55.694901,
            'show_time': '2020-04-01T05:00:00Z',
            'device_id': 'device-id',
            'platform': 'ios_app',
            'app_version': '2.1.2',
        },
        headers={'x-request-language': request_language},
    )
    assert response.status_code == 200
    collections = response.json()['payload']['collections']
    assert len(collections) == collections_count
