import pytest


@pytest.mark.parametrize(
    'projection',
    [
        [],
        ['brand_id'],
        ['parser_name'],
        ['stock_reset_limit'],
        ['dev_filter'],
        ['created_at'],
        ['updated_at'],
        ['brand_id', 'parser_name'],
        [
            'brand_id',
            'parser_name',
            'stock_reset_limit',
            'dev_filter',
            'created_at',
            'updated_at',
        ],
    ],
)
async def test_should_return_empty_if_none_in_database(
        projection, taxi_eats_place_groups_replica_web,
):
    response = await taxi_eats_place_groups_replica_web.get(
        '/v1/place_groups', params=_get_params(projection),
    )
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['items']


@pytest.mark.parametrize(
    'projection, expected_items',
    [
        [[], 'with_full_elems'],
        [['brand_id'], 'with_brand_id'],
        [['parser_name'], 'with_parser_name'],
        [['stock_reset_limit'], 'with_stock_reset_limit'],
        [['dev_filter'], 'with_dev_filter'],
        [['parser_options'], 'with_parser_options'],
        [['created_at'], 'with_created_at'],
        [['updated_at'], 'with_updated_at'],
        [['brand_id', 'parser_name'], 'with_brand_id_and_parser_name'],
        [
            [
                'brand_id',
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
@pytest.mark.pgsql('eats_place_groups_replica', files=['place_groups.sql'])
async def test_should_return_items(
        projection,
        expected_items,
        load_json,
        taxi_eats_place_groups_replica_web,
):
    response = await taxi_eats_place_groups_replica_web.get(
        '/v1/place_groups', params=_get_params(projection),
    )
    assert response.status == 200
    response_json = await response.json()

    expected_elements = load_json('result.json')[expected_items]
    assert response_json['items'] == expected_elements


def _get_params(projection):
    result = {}
    if projection:
        result['projection'] = (','.join(projection),)

    return result
