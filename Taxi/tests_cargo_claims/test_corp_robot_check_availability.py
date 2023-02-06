import pytest


@pytest.mark.parametrize(
    'rover_response_code, expected_availability',
    [(200, True), (404, False), (500, False)],
)
async def test_happy_path(
        taxi_cargo_claims,
        get_default_headers,
        get_default_corp_client_id,
        prepare_state,
        mock_robot_points_search,
        rover_response_code,
        expected_availability,
):
    await prepare_state(
        visit_order=1, last_exchange_init=False, transport_type='rover',
    )

    mock_robot_points_search.status_code = rover_response_code

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/robot/check-availability',
        json={
            'route_points': [
                {'type': 'source', 'coordinates': [1, 2]},
                {'type': 'destination', 'coordinates': [3, 4]},
            ],
        },
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {'available': expected_availability}

    if rover_response_code != 500:
        assert mock_robot_points_search.handler.times_called == 2

        requests = [
            sorted(
                mock_robot_points_search.handler.next_call()[
                    'request'
                ].query.items(),
            )
            for _ in range(mock_robot_points_search.handler.times_called)
        ]
        expected_requests = [
            {
                'ext_id': 'cargo:' + get_default_corp_client_id,
                'latitude': '2.000000',
                'longitude': '1.000000',
            }.items(),
            {'latitude': '4.000000', 'longitude': '3.000000'}.items(),
        ]
        assert sorted(requests) == sorted(map(list, expected_requests))


async def test_different_robot_location(
        taxi_cargo_claims,
        get_default_headers,
        get_default_corp_client_id,
        prepare_state,
        mock_robot_points_search,
):
    await prepare_state(
        visit_order=1, last_exchange_init=False, transport_type='rover',
    )

    mock_robot_points_search.status_code = 200
    mock_robot_points_search.response_body_iter = iter(
        ({'location': 1}, {'location': 2}),
    )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/robot/check-availability',
        json={
            'route_points': [
                {'type': 'source', 'coordinates': [1, 2]},
                {'type': 'destination', 'coordinates': [3, 4]},
            ],
        },
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {'available': False}

    assert mock_robot_points_search.handler.times_called == 2

    requests = [
        sorted(
            mock_robot_points_search.handler.next_call()[
                'request'
            ].query.items(),
        )
        for _ in range(mock_robot_points_search.handler.times_called)
    ]
    expected_requests = [
        {
            'ext_id': 'cargo:' + get_default_corp_client_id,
            'latitude': '2.000000',
            'longitude': '1.000000',
        }.items(),
        {'latitude': '4.000000', 'longitude': '3.000000'}.items(),
    ]
    assert sorted(requests) == sorted(map(list, expected_requests))
