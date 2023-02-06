import pytest

from tests_eats_products import conftest
from tests_eats_products import experiments
from tests_eats_products import utils

EATER_ID = '123'
HEADERS = {
    'X-Eats-User': f'user_id={EATER_ID}',
    'X-AppMetrica-DeviceId': 'device_id',
}

BASIC_REQUEST = {
    'available_places': [{'place_slug': 'slug', 'brand_name': 'name'}],
}


@pytest.fixture(name='mock_retail_categories_brand_default_history')
def _mock_retail_categories_brand_default_history(
        mock_retail_categories_brand_orders_history,
):
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', 5,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', 3,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', 7,
    )
    return mock_retail_categories_brand_orders_history


def make_informer(text):
    return {'enabled': True, 'text': text}


@pytest.mark.parametrize(
    'shops',
    [
        pytest.param([], id='empty'),
        pytest.param(
            [
                {'place_slug': 'unknown1', 'brand_name': 'name'},
                {'place_slug': 'unknown2', 'brand_name': 'name2'},
            ],
            id='unknown shops',
        ),
    ],
)
@experiments.cross_brand_history()
async def test_404_places_not_found(taxi_eats_products, shops):
    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PLACES,
        json={'available_places': shops},
        headers=HEADERS,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'place_not_found',
        'message': 'No requested places found in cache',
    }


async def test_no_cross_brand_history_config(taxi_eats_products):
    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PLACES,
        json=BASIC_REQUEST,
        headers=HEADERS,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'other',
        'message': 'Cross brand history config not found',
    }


@experiments.cross_brand_history()
@pytest.mark.parametrize('headers', [{}, {'X-Eats-User': 'user_id='}])
async def test_401_no_eater_id(taxi_eats_products, headers):
    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PLACES,
        json=BASIC_REQUEST,
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


@pytest.mark.parametrize(
    ['requested_places', 'expected_places'],
    [
        pytest.param(
            ['slug', 'slug2'],
            ['slug2', 'slug'],
            id='both places requested and returned',
        ),
        pytest.param(
            ['slug'], ['slug'], id='one place requested and returned',
        ),
    ],
)
@experiments.cross_brand_history()
async def test_requested_shops_returned(
        taxi_eats_products,
        add_place_products_mapping,
        sql_add_brand,
        sql_add_place,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mockserver,
        requested_places,
        expected_places,
        make_public_by_sku_id_response,
        mock_retail_categories_brand_orders_history,
):
    sql_add_brand(2, 'brand2')
    sql_add_place(2, 'slug2', 2)
    public_ids = [
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b008',
    ]
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1', core_id=1, public_id=public_ids[0],
            ),
            conftest.ProductMapping(
                origin_id='item_id_2', core_id=2, public_id=public_ids[1],
            ),
            conftest.ProductMapping(
                origin_id='item_id_3', core_id=3, public_id=public_ids[2],
            ),
        ],
        1,
        1,
    )
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_4', core_id=4, public_id=public_ids[3],
            ),
            conftest.ProductMapping(
                origin_id='item_id_5', core_id=5, public_id=public_ids[4],
            ),
            conftest.ProductMapping(
                origin_id='item_id_6', core_id=6, public_id=public_ids[5],
            ),
            conftest.ProductMapping(
                origin_id='item_id_8', core_id=3, public_id=public_ids[6],
            ),
        ],
        2,
        2,
    )
    place_sku_to_public_ids = {
        '1': {'1': [public_ids[0]], '2': [public_ids[1]]},
        '2': {'1': [public_ids[3]], '3': [public_ids[4]]},
    }

    mock_retail_categories_brand_orders_history.add_brand_product(
        1, public_ids[0], 5,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, public_ids[1], 3,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        1, public_ids[2], 7,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        2, public_ids[3], 7,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        2, public_ids[4], 8,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        2, public_ids[5], 8,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        2, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007', 9,
    )
    mock_retail_categories_brand_orders_history.add_brand_product(
        2, public_ids[6], 8,
    )

    sku_id = 1
    for public_id in public_ids:
        mock_nomenclature_static_info_context.add_product(
            public_id, sku_id=str(sku_id),
        )
        mock_nomenclature_dynamic_info_context.add_product(public_id)
        sku_id += 1

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, place_sku_to_public_ids)

    request = {'available_places': []}
    for place in requested_places:
        request['available_places'].append(
            {'place_slug': place, 'brand_name': 'name'},
        )
    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PLACES,
        json=request,
        headers=HEADERS,
    )
    assert mock_public_id_by_sku_id.times_called == len(requested_places)
    assert response.status_code == 200
    result_places = [
        place['place_slug'] for place in response.json()['places']
    ]
    assert result_places == expected_places
    assert mock_retail_categories_brand_orders_history.times_called == (
        len(requested_places)
    )


@pytest.mark.parametrize(
    'expected_places',
    [
        pytest.param(
            ['slug', 'slug2'],
            marks=experiments.cross_brand_history(new_min_total=2),
            id='slug, slug2 total products >= 2',
        ),
        pytest.param(
            ['slug'],
            marks=experiments.cross_brand_history(new_min_total=4),
            id='slug2 total products < 4',
        ),
        pytest.param(
            ['slug'],
            marks=experiments.cross_brand_history(new_min_available=4),
            id='slug2 available products < 4',
        ),
        pytest.param(
            ['slug2'],
            marks=experiments.cross_brand_history(
                old_min_available=3, new_min_total=2,
            ),
            id='slug available products < 3',
        ),
        pytest.param(
            [],
            marks=experiments.cross_brand_history(
                old_min_available=3, new_min_available=4,
            ),
            id='both unavailable',
        ),
    ],
)
async def test_config_mins(
        taxi_eats_products,
        add_place_products_mapping,
        sql_add_brand,
        sql_add_place,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mockserver,
        expected_places,
        make_public_by_sku_id_response,
        mock_retail_categories_brand_default_history,
):
    sql_add_brand(2, 'brand2')
    sql_add_place(2, 'slug2', 2)
    public_ids = [
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
    ]
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1', core_id=1, public_id=public_ids[0],
            ),
            conftest.ProductMapping(
                origin_id='item_id_2', core_id=2, public_id=public_ids[1],
            ),
        ],
        1,
        1,
    )
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_3', core_id=3, public_id=public_ids[2],
            ),
            conftest.ProductMapping(
                origin_id='item_id_4', core_id=4, public_id=public_ids[3],
            ),
            conftest.ProductMapping(
                origin_id='item_id_5', core_id=5, public_id=public_ids[4],
            ),
        ],
        2,
        2,
    )
    place_sku_to_public_ids = {
        '1': {'1': [public_ids[0]], '2': [public_ids[1]]},
        '2': {'1': [public_ids[3]], '2': [public_ids[2], public_ids[4]]},
    }
    sku_ids = [1, 2, 2, 1, 2]
    for i in range(0, 5):
        mock_nomenclature_static_info_context.add_product(
            public_ids[i], sku_id=str(sku_ids[i]),
        )
        mock_nomenclature_dynamic_info_context.add_product(public_ids[i])

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, place_sku_to_public_ids)

    request = {
        'available_places': [
            {'place_slug': 'slug', 'brand_name': 'name'},
            {'place_slug': 'slug2', 'brand_name': 'name2'},
        ],
    }
    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PLACES,
        json=request,
        headers=HEADERS,
    )
    assert mock_public_id_by_sku_id.times_called == 2
    assert response.status_code == 200
    result_places = [
        place['place_slug'] for place in response.json()['places']
    ]
    assert result_places == expected_places
    assert mock_retail_categories_brand_default_history.times_called == 2


@pytest.mark.parametrize(
    'has_override',
    [
        pytest.param(True, marks=experiments.CATALOG_OVERRIDES),
        pytest.param(False),
    ],
)
@experiments.cross_brand_history(old_min_available=1)
async def test_place_overrides(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mockserver,
        has_override,
        make_public_by_sku_id_response,
        mock_retail_categories_brand_default_history,
):
    public_id = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'

    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1', core_id=1, public_id=public_id,
            ),
        ],
    )
    place_sku_to_public_ids = {'1': {'1': [public_id]}}
    mock_nomenclature_static_info_context.add_product(public_id, sku_id='1')
    mock_nomenclature_dynamic_info_context.add_product(public_id)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, place_sku_to_public_ids)

    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PLACES,
        json=BASIC_REQUEST,
        headers=HEADERS,
    )
    assert mock_public_id_by_sku_id.times_called == 1
    assert response.status_code == 200
    place = response.json()['places'][0]
    if has_override:
        assert place['place_overrides'] == {
            'color': [
                {'theme': 'light', 'value': '#000000'},
                {'theme': 'dark', 'value': '#FFFFFF'},
            ],
            'logo_url': [
                {'theme': 'light', 'size': 'small', 'url': 'light_url'},
                {'theme': 'dark', 'size': 'small', 'url': 'dark_url'},
            ],
        }
    else:
        assert place['place_overrides'] == {'color': [], 'logo_url': []}
    assert mock_retail_categories_brand_default_history.times_called == 1


@pytest.mark.parametrize(
    'informer_text',
    [
        pytest.param(
            'Brand Magnit',
            marks=experiments.cross_brand_history(
                old_min_available=3,
                new_min_total=2,
                informer=make_informer('Brand {}'),
            ),
            id='test informer with brand name shown',
        ),
        pytest.param(
            'some_text',
            marks=experiments.cross_brand_history(
                old_min_available=3,
                new_min_total=2,
                informer=make_informer('some_text'),
            ),
            id='test informer with brand name shown',
        ),
    ],
)
async def test_informer(
        taxi_eats_products,
        add_place_products_mapping,
        sql_add_brand,
        sql_add_place,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mockserver,
        informer_text,
        make_public_by_sku_id_response,
        mock_retail_categories_brand_default_history,
):
    sql_add_brand(2, 'brand2')
    sql_add_place(2, 'slug2', 2)
    public_ids = [
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
    ]
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1', core_id=1, public_id=public_ids[0],
            ),
            conftest.ProductMapping(
                origin_id='item_id_2', core_id=2, public_id=public_ids[1],
            ),
        ],
        1,
        1,
    )
    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_3', core_id=3, public_id=public_ids[2],
            ),
            conftest.ProductMapping(
                origin_id='item_id_4', core_id=4, public_id=public_ids[3],
            ),
        ],
        2,
        2,
    )
    place_sku_to_public_ids = {
        '1': {'1': [public_ids[0]], '2': [public_ids[1]]},
        '2': {'1': [public_ids[3]], '2': [public_ids[2]]},
    }
    sku_ids = [1, 2, 2, 1]
    for i in range(0, 4):
        mock_nomenclature_static_info_context.add_product(
            public_ids[i], sku_id=str(sku_ids[i]),
        )
        mock_nomenclature_dynamic_info_context.add_product(public_ids[i])

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def mock_public_id_by_sku_id(request):
        return make_public_by_sku_id_response(request, place_sku_to_public_ids)

    request = {
        'available_places': [
            {'place_slug': 'slug', 'brand_name': 'Diski'},
            {'place_slug': 'slug2', 'brand_name': 'Magnit'},
        ],
    }
    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PLACES,
        json=request,
        headers=HEADERS,
    )
    assert mock_public_id_by_sku_id.times_called == 2
    assert response.status_code == 200
    places = response.json()['places']
    assert len(places) == 1
    assert places[0]['place_slug'] == 'slug2'
    assert places[0]['informers'] == [make_informer(informer_text)]
    assert mock_retail_categories_brand_default_history.times_called == 2


@pytest.mark.parametrize('handler_404', ['dynamic', 'static', 'sku'])
@experiments.cross_brand_history()
async def test_404_nomenclature(
        taxi_eats_products,
        add_place_products_mapping,
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mockserver,
        handler_404,
        make_public_by_sku_id_response,
        mock_retail_categories_brand_default_history,
):
    public_id = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'

    add_place_products_mapping(
        [
            conftest.ProductMapping(
                origin_id='item_id_1', core_id=1, public_id=public_id,
            ),
        ],
    )
    if handler_404 == 'static':
        mock_nomenclature_static_info_context.set_status(status_code=404)
    else:
        mock_nomenclature_static_info_context.add_product(
            public_id, sku_id='1',
        )
    if handler_404 == 'dynamic':
        mock_nomenclature_dynamic_info_context.set_status(status_code=404)
    else:
        mock_nomenclature_dynamic_info_context.add_product(public_id)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_public_id_by_sku_id(request):
        if handler_404 == 'sku':
            return mockserver.make_response(
                json={'status': 404, 'message': 'bad response'}, status=404,
            )
        return make_public_by_sku_id_response(request, {'1': {}})

    response = await taxi_eats_products.post(
        utils.Handlers.CROSS_BRAND_HISTORY_PLACES,
        json={
            'available_places': [
                {'place_slug': 'slug', 'brand_name': 'Diski'},
            ],
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert mock_retail_categories_brand_default_history.times_called == 1
