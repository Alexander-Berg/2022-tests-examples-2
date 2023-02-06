import pytest


async def test_should_return404_if_cannot_find(
        taxi_eats_place_groups_replica_web,
):
    response = await taxi_eats_place_groups_replica_web.get(
        '/v1/parser_info', params={'place_id': 'not_existed'},
    )
    assert response.status == 404


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
async def test_should_correct_return(
        projection,
        expected_items,
        load_json,
        taxi_eats_place_groups_replica_web,
):
    params = {'place_id': 'id1'}
    if projection:
        params['projection'] = ','.join(projection)

    response = await taxi_eats_place_groups_replica_web.get(
        '/v1/parser_info', params=params,
    )
    assert response.status == 200
    response_json = await response.json()

    expected_data = load_json('projection_result.json')[expected_items]
    assert response_json == expected_data
