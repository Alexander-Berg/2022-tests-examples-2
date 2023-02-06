import pytest


DEFAULT_LIMIT = 50
DEFAULT_PAGE = 1


@pytest.mark.parametrize(
    'projection, expected_items',
    [
        [[], 'with_full_elems'],
        [['place_id'], 'with_place_id'],
        [['brand_id'], 'with_brand_id'],
        [['place_group_id'], 'with_place_group_id'],
        [['external_id'], 'with_external_id'],
        [['parser_name'], 'with_parser_name'],
        [['stock_reset_limit'], 'with_stock_reset_limit'],
        [['dev_filter'], 'with_dev_filter'],
        [['parser_options'], 'with_parser_options'],
        [['created_at'], 'with_created_at'],
        [['updated_at'], 'with_updated_at'],
        [['external_id', 'parser_name'], 'with_external_id_and_parser_name'],
        [
            [
                'brand_id',
                'place_group_id',
                'external_id',
                'parser_name',
                'stock_reset_limit',
                'dev_filter',
                'parser_options',
                'created_at',
                'updated_at',
            ],
            'with_full_elems',
        ],
    ],
)
@pytest.mark.pgsql(
    'eats_place_groups_replica', files=['parser_infos_projection.sql'],
)
async def test_should_return_correct_projection(
        projection,
        expected_items,
        load_json,
        taxi_eats_place_groups_replica_web,
):
    response = await taxi_eats_place_groups_replica_web.get(
        '/v1/parser_infos', params=_get_params(projection=projection),
    )
    assert response.status == 200
    response_json = await response.json()

    expected_elements = load_json('projection_result.json')[expected_items]
    assert response_json['items'] == expected_elements


@pytest.mark.parametrize(
    (
        'limit',
        'page',
        'expected_page_count',
        'expected_element_count',
        'expected_elements_data',
    ),
    [
        [None, None, 1, 10, 'all'],
        [None, 2, 1, 0, 'none_data'],
        [2, None, 5, 2, 'limit2_page1'],
        [2, 2, 5, 2, 'limit2_page2'],
        [2, 8, 5, 0, 'none_data'],
    ],
)
@pytest.mark.pgsql(
    'eats_place_groups_replica', files=['parser_info_pagination.sql'],
)
async def test_should_return_correct_page(
        limit,
        page,
        expected_page_count,
        expected_element_count,
        expected_elements_data,
        load_json,
        taxi_eats_place_groups_replica_web,
):
    response = await taxi_eats_place_groups_replica_web.get(
        '/v1/parser_infos',
        params=_get_params(limit=limit, page=page, projection=['place_id']),
    )
    assert response.status == 200
    response_json = await response.json()

    expected_limit = limit if limit else DEFAULT_LIMIT
    expected_page = page if page else DEFAULT_PAGE

    assert response_json['meta']['limit'] == expected_limit
    assert response_json['meta']['page'] == expected_page
    assert response_json['meta']['max_pages'] == expected_page_count

    assert len(response_json['items']) == expected_element_count
    expected_elements = load_json('pagination_result.json')[
        expected_elements_data
    ]

    assert response_json['items'] == expected_elements


@pytest.mark.parametrize(
    'testcase',
    [
        'place_ids',
        'brand_ids',
        'place_group_ids',
        'external_ids',
        'parser_names',
        'parser_name_contains',
        'stock_reset_limit',
        'stock_reset_limit_lesser',
        'stock_reset_limit_greater',
        'created_at_before',
        'created_at_after',
        'created_at_before_2021_06_21_after_2021_06_20',
        'updated_at_before',
        'updated_at_after',
        'updated_at_before_2021_06_21_after_2021_06_20',
        'parser_name_contains_and_stock_reset_limit',
        'without_filter',
    ],
)
@pytest.mark.pgsql(
    'eats_place_groups_replica', files=['parser_infos_filter.sql'],
)
async def test_should_correct_filter(
        testcase, load_json, taxi_eats_place_groups_replica_web,
):
    request_data = load_json('parser_info_filter_request.json')[testcase]

    response = await taxi_eats_place_groups_replica_web.get(
        '/v1/parser_infos',
        params=_get_params(**request_data, projection=['place_item_id']),
    )
    assert response.status == 200
    response_json = await response.json()

    expected_elements = load_json('filter_result.json')[testcase]

    assert response_json['items'] == expected_elements


def _get_params(
        place_ids=None,
        brand_ids=None,
        place_group_ids=None,
        external_ids=None,
        parser_names=None,
        parser_name_contains=None,
        stock_reset_limit=None,
        stock_reset_limit_lesser=None,
        stock_reset_limit_greater=None,
        created_at_after=None,
        created_at_before=None,
        limit=None,
        page=None,
        updated_at_after=None,
        updated_at_before=None,
        projection=None,
):
    result = {}

    if place_ids:
        result['place_ids'] = ','.join(place_ids)
    if brand_ids:
        result['brand_ids'] = ','.join(brand_ids)
    if place_group_ids:
        result['place_group_ids'] = ','.join(place_group_ids)
    if external_ids:
        result['external_ids'] = ','.join(external_ids)
    if parser_names:
        result['parser_names'] = ','.join(parser_names)
    if projection:
        result['projection'] = ','.join(projection)
    if parser_name_contains:
        result['parser_name_contains'] = parser_name_contains
    if stock_reset_limit:
        result['stock_reset_limit'] = stock_reset_limit
    if stock_reset_limit_lesser:
        result['stock_reset_limit_lesser'] = stock_reset_limit_lesser
    if stock_reset_limit_greater:
        result['stock_reset_limit_greater'] = stock_reset_limit_greater
    if created_at_before:
        result['created_at_before'] = created_at_before
    if created_at_after:
        result['created_at_after'] = created_at_after
    if updated_at_before:
        result['updated_at_before'] = updated_at_before
    if updated_at_after:
        result['updated_at_after'] = updated_at_after
    if limit:
        result['limit'] = limit
    if page:
        result['page'] = page

    return result
