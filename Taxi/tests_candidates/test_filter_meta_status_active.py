async def test_status_active(
        taxi_candidates,
        driver_positions,
        mockserver,
        load_binary,
        mock_reposition_index,
):
    mock_reposition_index.set_response(
        drivers=[
            {
                'driver_id': 'uuid2',
                'park_db_id': 'dbid0',
                'can_take_orders': False,
                'can_take_orders_when_busy': True,
                'reposition_check_required': False,
            },
        ],
    )

    # dbid0_uuid2 has taximeter status Busy for this test, so should be
    # disallowed by status_active, but allowed by reposition
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/meta_status_active'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert len(response.json()['drivers']) == 2
