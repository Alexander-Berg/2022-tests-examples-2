import pytest


@pytest.mark.parametrize(
    'request_override, expected_candidates, config_override',
    [
        (
            {'order': {'calc': {'alternative_type': ''}}},
            [{'dbid_uuid': 'dbid0_uuid0'}, {'dbid_uuid': 'dbid0_uuid1'}],
            {'__default__': {'enabled': True}},
        ),
        (
            {'order': {'calc': {}}},
            [{'dbid_uuid': 'dbid0_uuid0'}, {'dbid_uuid': 'dbid0_uuid1'}],
            {'__default__': {'enabled': False}},
        ),
        (
            {'order': {}},
            [{'dbid_uuid': 'dbid0_uuid0'}, {'dbid_uuid': 'dbid0_uuid1'}],
            {'__default__': {'enabled': True}},
        ),
        (
            {'order': {'calc': {'alternative_type': 'combo_order'}}},
            [{'dbid_uuid': 'dbid0_uuid1'}],
            {'__default__': {'enabled': True}},
        ),
        (
            {'order': {'calc': {'alternative_type': 'combo_order'}}},
            [{'dbid_uuid': 'dbid0_uuid0'}, {'dbid_uuid': 'dbid0_uuid1'}],
            {'__default__': {'enabled': True}, 'moscow': {'enabled': False}},
        ),
    ],
)
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
async def test_filter_block_combo_order_chain(
        taxi_candidates,
        taxi_config,
        driver_positions,
        chain_busy_drivers,
        request_override,
        expected_candidates,
        config_override,
):
    taxi_config.set_values(
        {'CANDIDATES_FILTER_BLOCK_COMBO_ORDER_CHAIN': config_override},
    )

    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid0',
                'destination': [37.625344, 55.755430],
                'left_distance': 100,
                'left_time': 10,
            },
        ],
    )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625129, 55.757644]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625129, 55.757644]},
        ],
    )

    request_body = {
        'limit': 10,
        'point': [37.625129, 55.757644],
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'vip'],
    }
    request_body.update(request_override)

    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200

    candidates = [
        {'dbid_uuid': candidate['id']}
        for candidate in response.json()['candidates']
    ]

    assert (
        sorted(candidates, key=lambda x: x['dbid_uuid']) == expected_candidates
    )
