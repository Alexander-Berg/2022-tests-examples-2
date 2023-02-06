import pytest


@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid2', 'suitable_for_verybusy_orders'),
        ('dbid_uuid', 'dbid0_uuid1', 'suitable_for_verybusy_orders'),
        ('dbid_uuid', 'dbid0_uuid1', 'dont_disturb'),
    ],
)
@pytest.mark.config(
    EXTRA_EXAMS_BY_ZONE={},
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
    TAGS_INDEX={'enabled': True},
)
async def test_busy_free(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.63, 55.74]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.63, 55.74]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.63, 55.74]},
            {'dbid_uuid': 'dbid0_uuid3', 'position': [37.63, 55.74]},
        ],
    )
    request_body = {
        'limit': 10,
        'point': [37.63, 55.74],
        'metadata': {
            'experiments': [
                {
                    'name': 'add_verybusy_to_dispatch',
                    'value': None,
                    'position': 0,
                    'version': 0,
                    'is_signal': False,
                },
            ],
        },
    }
    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200
    candidates = [
        {
            'dbid_uuid': candidate['id'],
            'metadata': (
                candidate['metadata'] if 'metadata' in candidate else None
            ),
        }
        for candidate in response.json()['candidates']
    ]
    assert sorted(candidates, key=lambda x: x['dbid_uuid']) == [
        {'dbid_uuid': 'dbid0_uuid0', 'metadata': None},
        {'dbid_uuid': 'dbid0_uuid2', 'metadata': {'verybusy_order': True}},
    ]
