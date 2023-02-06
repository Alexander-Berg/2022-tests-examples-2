import pytest

import testsuite

import tests_eats_brands.common as common

BRANDS_DATA = [
    common.extend_brand_without_slug({common.NAME: 'Brand1'}),
    common.extend_brand_without_slug({common.NAME: 'Brand2'}),
    common.extend_brand_without_slug({common.NAME: 'Brand Qwerty'}),
    common.extend_brand_without_slug({common.NAME: 'Subway'}),
    common.extend_brand_without_slug({common.NAME: 'Dodo Pizza'}),
    common.extend_brand_without_slug({common.NAME: 'Brand Pizza'}),
]

CASES = [
    (
        BRANDS_DATA,
        {common.NAME: 'Brand', common.MODE: common.SUGGESTIONS},
        ['Brand Pizza', 'Brand Qwerty', 'Brand1', 'Brand2'],
    ),
    (BRANDS_DATA, {common.NAME: 'Brand'}, ['Brand1', 'Brand2']),
    (
        BRANDS_DATA,
        {common.NAME: 'rand', common.MODE: common.SUGGESTIONS},
        ['Brand1', 'Brand2'],
    ),
    (
        BRANDS_DATA,
        {common.NAME: 'Brand Asdfgh', common.MODE: common.SUGGESTIONS},
        [],
    ),
    (BRANDS_DATA, {common.NAME: 'Sunway'}, ['Subway']),
    (
        BRANDS_DATA,
        {common.NAME: 'sub', common.MODE: common.SUGGESTIONS},
        ['Subway'],
    ),
    (
        BRANDS_DATA,
        {common.NAME: 'sub', common.MODE: common.SIMILARITY},
        ['Subway'],
    ),
    (BRANDS_DATA, {common.NAME: 'Su', common.MODE: common.SIMILARITY}, []),
    (
        BRANDS_DATA,
        {common.NAME: 'Su', common.MODE: common.SUGGESTIONS},
        ['Subway'],
    ),
    (
        BRANDS_DATA,
        {common.NAME: 'Dodo', common.MODE: common.SUGGESTIONS},
        ['Dodo Pizza'],
    ),
    (BRANDS_DATA, {common.NAME: 'Dodo', common.MODE: common.SIMILARITY}, []),
    (BRANDS_DATA, {common.NAME: 'Dodo'}, []),
    (
        BRANDS_DATA,
        {common.NAME: '', common.MODE: common.SUGGESTIONS},
        [
            'Brand Pizza',
            'Dodo Pizza',
            'Subway',
            'Brand Qwerty',
            'Brand2',
            'Brand1',
        ],
    ),
    (
        BRANDS_DATA,
        {common.NAME: 'izz', common.MODE: common.SUBSTRING_SEARCH},
        ['Brand Pizza', 'Dodo Pizza'],
    ),
]


def id_format(val):
    if common.NAME in val:
        return val[common.NAME]
    return ''


@pytest.mark.parametrize(
    'brands,request_data,expected_data', CASES, ids=id_format,
)
async def test_200(taxi_eats_brands, brands, request_data, expected_data):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    # now search
    response = await taxi_eats_brands.post(
        'brands/v1/search', json=request_data,
    )
    assert response.status_code == 200

    response_json = response.json()
    if 'items' not in response_json:
        assert not expected_data
    else:
        response_names = list(x['name'] for x in response_json['items'])
        assert len(response_names) == len(expected_data)
        for given, expected in zip(response_names, expected_data):
            assert given == expected


DELETE_CASES = [
    (
        BRANDS_DATA,
        {common.NAME: 'Brand', common.MODE: common.SUGGESTIONS},
        ['Brand Pizza', 'Brand Qwerty'],
    ),
    (
        BRANDS_DATA,
        {
            common.NAME: 'Brand',
            common.MODE: common.SUGGESTIONS,
            common.SHOW_DELETED: True,
        },
        ['Brand Pizza', 'Brand Qwerty', 'Brand1', 'Brand2'],
    ),
    (BRANDS_DATA, {common.NAME: 'sub', common.MODE: common.SIMILARITY}, []),
    (
        BRANDS_DATA,
        {
            common.NAME: 'sub',
            common.MODE: common.SIMILARITY,
            common.SHOW_DELETED: True,
        },
        ['Subway'],
    ),
    (BRANDS_DATA, {common.NAME: ''}, ['Brand Pizza', 'Brand Qwerty']),
    (
        BRANDS_DATA,
        {common.NAME: '', common.SHOW_DELETED: True},
        [
            'Brand Pizza',
            'Dodo Pizza',
            'Subway',
            'Brand Qwerty',
            'Brand2',
            'Brand1',
        ],
    ),
    (
        BRANDS_DATA,
        {common.NAME: 'izz', common.MODE: common.SUBSTRING_SEARCH},
        ['Brand Pizza'],
    ),
    (
        BRANDS_DATA,
        {
            common.NAME: 'izz',
            common.MODE: common.SUBSTRING_SEARCH,
            common.SHOW_DELETED: True,
        },
        ['Brand Pizza', 'Dodo Pizza'],
    ),
]


@pytest.mark.parametrize(
    'brands,request_data,expected_data', DELETE_CASES, ids=id_format,
)
async def test_search_show_deleted_200(
        taxi_eats_brands, brands, request_data, expected_data,
):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    # remove few brands
    response = await taxi_eats_brands.post(
        'brands/v1/delete', json={'id': 1},
    )  # Brand1
    assert response.status_code == 200
    response = await taxi_eats_brands.post(
        'brands/v1/delete', json={'id': 2},
    )  # Brand2
    assert response.status_code == 200
    response = await taxi_eats_brands.post(
        'brands/v1/delete', json={'id': 4},
    )  # Subway
    assert response.status_code == 200
    response = await taxi_eats_brands.post(
        'brands/v1/delete', json={'id': 5},
    )  # Dodo Pizza
    assert response.status_code == 200

    # now search
    response = await taxi_eats_brands.post(
        'brands/v1/search', json=request_data,
    )
    assert response.status_code == 200

    response_json = response.json()
    if 'items' not in response_json:
        assert not expected_data
    else:
        response_names = list(x['name'] for x in response_json['items'])
        assert len(response_names) == len(expected_data)
        for given, expected in zip(response_names, expected_data):
            assert given == expected


MERGE_CASES = [
    (
        BRANDS_DATA,
        {
            common.NAME: 'Brand',
            common.MODE: common.SUGGESTIONS,
            common.SHOW_DELETED: True,
        },
        ['Brand1'],
        {common.ACTUAL_ID: 1, common.IDS_TO_MERGE: [2, 3, 6]},
    ),
    (
        BRANDS_DATA,
        {
            common.NAME: 'Brand',
            common.MODE: common.SIMILARITY,
            common.SHOW_DELETED: True,
        },
        ['Brand1'],
        {common.ACTUAL_ID: 1, common.IDS_TO_MERGE: [2, 3, 6]},
    ),
    (
        BRANDS_DATA,
        {common.NAME: 'Brand', common.SHOW_DELETED: True},
        ['Brand1'],
        {common.ACTUAL_ID: 1, common.IDS_TO_MERGE: [2, 3, 6]},
    ),
]


@pytest.mark.parametrize(
    'brands,request_data,expected_data,merge_request',
    MERGE_CASES,
    ids=id_format,
)
async def test_search_without_merged(
        taxi_eats_brands, brands, request_data, expected_data, merge_request,
):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    # remove few brands
    response = await taxi_eats_brands.post(
        'brands/v1/merge-brands', json=merge_request,
    )  # Brand1
    assert response.status_code == 200

    # now search
    response = await taxi_eats_brands.post(
        'brands/v1/search', json=request_data,
    )
    assert response.status_code == 200

    response_json = response.json()
    if 'items' not in response_json:
        assert not expected_data
    else:
        response_names = list(x['name'] for x in response_json['items'])
        assert len(response_names) == len(expected_data)
        for given, expected in zip(response_names, expected_data):
            assert given == expected


PAGINATION_CASES = [
    (
        BRANDS_DATA,
        {
            common.NAME: 'Brand',
            common.MODE: common.SUGGESTIONS,
            common.PAGINATION: {common.PAGE_SIZE: 3, common.PAGE_NUMBER: 1},
        },
        ['Brand Pizza', 'Brand Qwerty', 'Brand1'],
        3,  # expected_items
        3,  # expected_page_size
        1,  # expected_page_number
        2,  # expected_page_count
        4,  # expected_total_items
    ),
    (
        BRANDS_DATA,
        {
            common.NAME: 'Brand',
            common.MODE: common.SUGGESTIONS,
            common.PAGINATION: {common.PAGE_SIZE: 3, common.PAGE_NUMBER: 2},
        },
        ['Brand2'],
        1,  # expected_items
        3,  # expected_page_size
        2,  # expected_page_number
        2,  # expected_page_count
        4,  # expected_total_items
    ),
    (  # page number more than page count
        BRANDS_DATA,
        {
            common.NAME: 'Brand',
            common.MODE: common.SUGGESTIONS,
            common.PAGINATION: {common.PAGE_SIZE: 3, common.PAGE_NUMBER: 9},
        },
        [],
        0,  # expected_items
        3,  # expected_page_size
        9,  # expected_page_number
        2,  # expected_page_count
        4,  # expected_total_items
    ),
]


@pytest.mark.parametrize(
    'brands,request_data,expected_data,expected_items,expected_page_size,'
    'expected_page_number,expected_page_count,expected_total_items',
    PAGINATION_CASES,
)
async def test_pagination_200(
        taxi_eats_brands,
        brands,
        request_data,
        expected_data,
        expected_items,
        expected_page_size,
        expected_page_number,
        expected_page_count,
        expected_total_items,
):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    # now search
    response = await taxi_eats_brands.post(
        'brands/v1/search', json=request_data,
    )
    assert response.status_code == 200

    response_json = response.json()
    if not response_json['items']:
        assert not expected_data
    else:
        response_names = list(x['name'] for x in response_json['items'])
        assert len(response_names) == len(expected_data)
        for given, expected in zip(response_names, expected_data):
            assert given == expected

        response_pagination = response_json[common.PAGINATION]
        assert response_pagination[common.ITEMS] == expected_items
        assert response_pagination[common.PAGE_SIZE] == expected_page_size
        assert response_pagination[common.PAGE_NUMBER] == expected_page_number
        assert response_pagination[common.PAGE_COUNT] == expected_page_count
        assert response_pagination[common.TOTAL_ITEMS] == expected_total_items


async def test_incorrect_config(taxi_eats_brands, taxi_config):
    taxi_config.set_values({'EATS_BRANDS_SEARCH_DEFAULT_PAGE_SIZE': -1})
    try:
        await taxi_eats_brands.invalidate_caches()
        assert False, 'Service is not in a broken state'
    except testsuite.utils.http.HttpResponseError:
        pass

    taxi_config.set_values({'EATS_BRANDS_SEARCH_DEFAULT_PAGE_SIZE': 9999})
    try:
        await taxi_eats_brands.invalidate_caches()
        assert False, 'Service is not in a broken state'
    except testsuite.utils.http.HttpResponseError:
        pass


INCORRECT_PAGINATION_CASES = [
    (  # negative page number
        BRANDS_DATA,
        {
            common.NAME: 'Brand',
            common.MODE: common.SUGGESTIONS,
            common.PAGINATION: {common.PAGE_SIZE: 3, common.PAGE_NUMBER: -1},
        },
    ),
    (  # negative page size
        BRANDS_DATA,
        {
            common.NAME: 'Brand',
            common.MODE: common.SUGGESTIONS,
            common.PAGINATION: {common.PAGE_SIZE: -1},
        },
    ),
    (  # page size more than kMaxPageSize
        BRANDS_DATA,
        {
            common.NAME: 'Brand',
            common.MODE: common.SUGGESTIONS,
            common.PAGINATION: {common.PAGE_SIZE: 9999},
        },
    ),
]


@pytest.mark.parametrize('brands,request_data', INCORRECT_PAGINATION_CASES)
async def test_incorrect_pagination_request(
        taxi_eats_brands, brands, request_data,
):
    # we need to create brands first
    for brand in brands:
        response = await taxi_eats_brands.post('brands/v1/create', json=brand)
        assert response.status_code == 200

    # now search
    response = await taxi_eats_brands.post(
        'brands/v1/search', json=request_data,
    )
    assert response.status_code == 400
