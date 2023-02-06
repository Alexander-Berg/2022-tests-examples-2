import pytest


@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'tag1'),
        ('dbid_uuid', 'dbid0_uuid0', 'tag2'),
        ('dbid_uuid', 'dbid0_uuid1', 'tag3'),
    ],
)
@pytest.mark.config(
    CANDIDATES_FILTER_APP_FAMILY_BLOCKING_TAGS=[
        {'app_family': 'uberdriver', 'tags': ['tag0', 'tag1']},
    ],
    EXTRA_EXAMS_BY_ZONE={},
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
    TAGS_INDEX={'enabled': True},
)
async def test_filter_app_family_blocking_tags(
        taxi_candidates, driver_positions,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'limit': 10,
        'filters': ['efficiency/app_family_blocking_tags'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200
    candidates = [
        candidate['id'] for candidate in response.json()['candidates']
    ]
    assert sorted(candidates) == ['dbid0_uuid1', 'dbid0_uuid2']
