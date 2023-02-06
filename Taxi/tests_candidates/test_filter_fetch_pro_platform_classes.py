import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='filter_performers_by_pro_platform',
    consumers=['candidates/user'],
    clauses=[
        {
            'title': '1',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'tariff_zone',
                                'arg_type': 'string',
                                'value': 'moscow',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'arg_name': 'phone_id',
                                'arg_type': 'string',
                                'value': 'some_user_phone_id',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'enabled': True,
                'platforms_to_filter': [{'platform': 'ios'}],
                'classes_to_filter': ['econom', 'express'],
            },
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)
@pytest.mark.config(CANDIDATES_ORDER_SEARCH_USE_GRAPH={'use_graph': True})
async def test_filter(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid3', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'allowed_classes': ['econom', 'express'],
        'filters': ['infra/class'],
        'point': [55, 35],
        'zone_id': 'moscow',
        'order': {'user_phone_id': 'some_user_phone_id'},
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()

    assert len(json['drivers']) == 1
    assert json['drivers'][0]['uuid'] == 'uuid0'
