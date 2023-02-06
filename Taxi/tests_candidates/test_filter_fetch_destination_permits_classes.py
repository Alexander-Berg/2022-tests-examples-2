import pytest


@pytest.mark.config(
    CANDIDATES_FILTER_FETCH_DESTINATION_PERMITS_CLASSES={
        '__default__': {'__default__': True},
    },
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
)
@pytest.mark.parametrize(
    # dbid0_uuid0's permission is managed by config
    # dbid0_uuid1 is always permitted by having license
    'classes_without_permit, expected_candidates',
    [
        (
            {'__default__': {}, 'moscow': {'*': ['minivan']}},
            ['dbid0_uuid0', 'dbid0_uuid1'],
        ),
        ({'__default__': {}}, ['dbid0_uuid1']),
    ],
)
async def test_filter_fetch_destination_permits(
        taxi_candidates,
        taxi_config,
        driver_positions,
        classes_without_permit,
        expected_candidates,
):

    taxi_config.set_values(
        dict(CLASSES_WITHOUT_PERMIT_BY_ZONES=classes_without_permit),
    )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [35, 55]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [35, 55]},
        ],
    )
    request_body = {
        'limit': 10,
        'point': [35, 55],
        'zone_id': 'korolev',
        'allowed_classes': ['econom', 'vip', 'minivan'],
        'destination': [37.1946401739712, 55.478983901730004],
    }
    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200
    candidates = [
        candidate['id'] for candidate in response.json()['candidates']
    ]
    assert sorted(candidates) == expected_candidates
