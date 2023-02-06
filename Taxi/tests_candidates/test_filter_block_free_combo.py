import pytest


@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['linear-fallback']}],
    CANDIDATES_FILTER_COMBO_FREE_ENABLED={
        '__default__': {'__default__': True},
    },
)
async def test_filter_block_free_combo(
        taxi_candidates, driver_positions, combo_contractors,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625129, 55.757644]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625129, 55.757644]},
        ],
    )

    combo_contractors([{'dbid_uuid': 'dbid0_uuid1'}])

    request_body = {
        'limit': 10,
        'point': [37.625129, 55.757644],
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'vip'],
    }

    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200

    candidates = [
        {'dbid_uuid': candidate['id']}
        for candidate in response.json()['candidates']
    ]

    assert candidates == [{'dbid_uuid': 'dbid0_uuid0'}]
