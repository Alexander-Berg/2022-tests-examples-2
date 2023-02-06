import pytest

DEFAULT_LIMIT = 50
DEFAULT_PAGE = 1


@pytest.mark.parametrize(
    'projection, expected_items',
    [
        [[], 'with_full_elems'],
        [['external_id'], 'with_external_id'],
        [['place_id'], 'with_place_id'],
        [['created_at'], 'with_created_at'],
        [['updated_at'], 'with_updated_at'],
        [['external_id', 'place_id'], 'with_external_id_and_place_id'],
        [
            ['external_id', 'place_id', 'created_at', 'updated_at'],
            'with_full_elems',
        ],
    ],
)
@pytest.mark.pgsql(
    'eats_place_groups_replica', files=['place_items_projection.sql'],
)
async def test_should_return_correct_projection(
        projection,
        expected_items,
        load_json,
        taxi_eats_place_groups_replica_web,
):
    response = await taxi_eats_place_groups_replica_web.get(
        '/v1/place_items', params=_get_params(projection=projection),
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
    'eats_place_groups_replica', files=['place_items_pagination.sql'],
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
        '/v1/place_items',
        params=_get_params(
            limit=limit, page=page, projection=['place_item_id'],
        ),
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
    (
        'place_id',
        'place_item_ids',
        'created_at_before',
        'created_at_after',
        'updated_at_before',
        'updated_at_after',
        'external_ids',
        'expected_elements_data',
    ),
    [
        ['place_id1', None, None, None, None, None, None, 'place_id1'],
        [None, ['id1', 'id2'], None, None, None, None, None, 'id1_id2'],
        [
            None,
            None,
            '2021-06-21',
            None,
            None,
            None,
            None,
            'created_at_before_2021_06_21',
        ],
        [
            None,
            None,
            '2021-06-21',
            '2021-06-20',
            None,
            None,
            None,
            'created_at_before_2021_06_21_after_2021_06_20',
        ],
        [
            None,
            None,
            None,
            '2021-06-20',
            None,
            None,
            None,
            'created_at_after_2021_06_20',
        ],
        [
            None,
            None,
            None,
            None,
            '2021-06-21',
            None,
            None,
            'updated_at_before_2021_06_21',
        ],
        [
            None,
            None,
            None,
            None,
            '2021-06-21',
            '2021-06-20',
            None,
            'updated_at_before_2021_06_21_after_2021_06_20',
        ],
        [
            None,
            None,
            None,
            None,
            None,
            '2021-06-20',
            None,
            'updated_at_after_2021_06_20',
        ],
        [
            None,
            None,
            None,
            None,
            None,
            None,
            ['external_id1', 'external_id2'],
            'external_id1_external_id2',
        ],
    ],
)
@pytest.mark.pgsql(
    'eats_place_groups_replica', files=['place_items_filter.sql'],
)
async def test_should_correct_filter(
        place_id,
        place_item_ids,
        created_at_before,
        created_at_after,
        updated_at_before,
        updated_at_after,
        external_ids,
        expected_elements_data,
        load_json,
        taxi_eats_place_groups_replica_web,
):
    response = await taxi_eats_place_groups_replica_web.get(
        '/v1/place_items',
        params=_get_params(
            place_id=place_id,
            place_item_ids=place_item_ids,
            created_at_before=created_at_before,
            created_at_after=created_at_after,
            updated_at_before=updated_at_before,
            updated_at_after=updated_at_after,
            external_ids=external_ids,
            projection=['place_item_id'],
        ),
    )
    assert response.status == 200
    response_json = await response.json()

    expected_elements = load_json('filter_result.json')[expected_elements_data]

    assert response_json['items'] == expected_elements


def _get_params(
        place_id=None,
        place_item_ids=None,
        external_ids=None,
        created_at_after=None,
        created_at_before=None,
        limit=None,
        page=None,
        updated_at_after=None,
        updated_at_before=None,
        projection=None,
):
    result = {}

    if place_item_ids:
        result['place_item_ids'] = ','.join(place_item_ids)
    if external_ids:
        result['external_ids'] = ','.join(external_ids)
    if projection:
        result['projection'] = ','.join(projection)
    if place_id:
        result['place_id'] = place_id
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
