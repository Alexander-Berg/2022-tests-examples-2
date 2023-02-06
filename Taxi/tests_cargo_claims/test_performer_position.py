import pytest


@pytest.mark.parametrize(
    'link_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                CARGO_PERFORMER_POSITION_LINK_ENABLED=True,
            ),
        ),
        # pytest.param(False),
    ],
)
@pytest.mark.experiments3(
    name='control_claims_processing',
    consumers=['cargo-claims/c2c-clients-orders'],
    default_value={'enabled': True},
    is_config=True,
    clauses=[],
)
async def test_performer_position(
        taxi_cargo_claims,
        create_claim_with_performer,
        get_default_headers,
        mockserver,
        get_sharing_keys,
        link_enabled,
):
    position = {
        'direction': 0,
        'lat': 37.5783920288086,
        'lon': -55.7350642053194,
        'speed': 0,
        'timestamp': 100,
    }

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        assert request.json == {'driver_id': 'park_id1_driver_id1'}
        return mockserver.make_response(
            json={'position': position, 'type': 'raw'}, status=200,
        )

    @mockserver.json_handler('/cargo-c2c/v1/clients-orders')
    def mock_c2c_orders(request):
        assert request.json == {
            'order_id': create_claim_with_performer.claim_id,
            'order_provider_id': 'cargo-claims',
        }
        order_id = request.json['order_id']
        return mockserver.make_response(
            json={
                'orders': [
                    {
                        'id': {
                            'order_id': order_id,
                            'order_provider_id': 'cargo-c2c',
                            'phone_pd_id': '+72222222222_id',
                        },
                        'roles': ['initiator'],
                        'sharing_key': 'sharing_key_3',
                        'sharing_url': 'http://test/sharing_key_1',
                        'additional_delivery_description': {},
                    },
                    {
                        'id': {
                            'order_id': order_id,
                            'order_provider_id': 'cargo-c2c',
                            'phone_pd_id': '+79999999999_id',
                        },
                        'roles': ['recipient'],
                        'sharing_key': 'sharing_key_3',
                        'sharing_url': 'http://test/sharing_key_2',
                        'additional_delivery_description': {},
                    },
                ],
            },
        )

    response = await taxi_cargo_claims.get(
        '/api/integration/v1/claims/performer-position',
        params={'claim_id': create_claim_with_performer.claim_id},
        headers=get_default_headers(),
    )

    expected_response = {'position': position}
    if link_enabled:
        assert mock_c2c_orders.times_called == 1
        expected_response['route_points'] = [
            {'id': 1, 'type': 'source', 'visit_order': 1},
            {'id': 2, 'type': 'destination', 'visit_order': 2},
            {
                'id': 3,
                'type': 'return',
                'visit_order': 3,
                'sharing_link': 'http://test/sharing_key_2',
            },
        ]

    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.experiments3(
    name='control_claims_processing',
    consumers=['cargo-claims/c2c-clients-orders'],
    default_value={'enabled': True},
    is_config=True,
    clauses=[],
)
@pytest.mark.config(CARGO_PERFORMER_POSITION_LINK_ENABLED=True)
async def test_multipoints(
        taxi_cargo_claims,
        create_claim_with_performer,
        get_default_headers,
        mockserver,
        get_sharing_keys,
):
    # Test no sharing_link in response (because of multipoints order)

    position = {
        'direction': 0,
        'lat': 37.5783920288086,
        'lon': -55.7350642053194,
        'speed': 0,
        'timestamp': 100,
    }

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        assert request.json == {'driver_id': 'park_id1_driver_id1'}
        return mockserver.make_response(
            json={'position': position, 'type': 'raw'}, status=200,
        )

    @mockserver.json_handler('/cargo-c2c/v1/clients-orders')
    def mock_c2c_orders(request):
        assert request.json == {
            'order_id': create_claim_with_performer.claim_id,
            'order_provider_id': 'cargo-claims',
        }
        order_id = request.json['order_id']
        return mockserver.make_response(
            json={
                'orders': [
                    {
                        'id': {
                            'order_id': order_id,
                            'order_provider_id': 'cargo-c2c',
                            'phone_pd_id': '+72222222222_id',
                        },
                        'roles': ['recipient'],
                        'sharing_key': 'sharing_key_3',
                        'sharing_url': 'http://test/sharing_key_1',
                        'additional_delivery_description': {},
                    },
                    {
                        'id': {
                            'order_id': order_id,
                            'order_provider_id': 'cargo-c2c',
                            'phone_pd_id': '+79999999999_id',
                        },
                        'roles': ['recipient'],
                        'sharing_key': 'sharing_key_3',
                        'sharing_url': 'http://test/sharing_key_2',
                        'additional_delivery_description': {},
                    },
                ],
            },
        )

    response = await taxi_cargo_claims.get(
        '/api/integration/v1/claims/performer-position',
        params={'claim_id': create_claim_with_performer.claim_id},
        headers=get_default_headers(),
    )

    assert mock_c2c_orders.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'position': position,
        'route_points': [
            {'id': 1, 'type': 'source', 'visit_order': 1},
            {
                'id': 2,
                'type': 'destination',
                'visit_order': 2,
                'sharing_link': 'http://test/sharing_key_1',
            },
            {
                'id': 3,
                'type': 'return',
                'visit_order': 3,
                'sharing_link': 'http://test/sharing_key_2',
            },
        ],
    }


@pytest.mark.experiments3(
    name='control_claims_processing',
    consumers=['cargo-claims/c2c-clients-orders'],
    default_value={'enabled': True},
    is_config=True,
    clauses=[],
)
@pytest.mark.config(CARGO_PERFORMER_POSITION_LINK_ENABLED=True)
async def test_performer_position_skip_client_notify(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_default_headers,
        mockserver,
):
    position = {
        'direction': 0,
        'lat': 37.5783920288086,
        'lon': -55.7350642053194,
        'speed': 0,
        'timestamp': 100,
    }

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        position = {
            'direction': 0,
            'lat': 37.5783920288086,
            'lon': -55.7350642053194,
            'speed': 0,
            'timestamp': 100,
        }

        assert request.json == {'driver_id': 'park_id1_driver_id1'}
        return mockserver.make_response(
            json={'position': position, 'type': 'raw'}, status=200,
        )

    @mockserver.json_handler('/cargo-c2c/v1/clients-orders')
    def _mock_c2c_orders(request):
        assert request.json == {
            'order_id': claim_info.claim_id,
            'order_provider_id': 'cargo-claims',
        }
        order_id = request.json['order_id']
        return mockserver.make_response(
            json={
                'orders': [
                    {
                        'id': {
                            'order_id': order_id,
                            'order_provider_id': 'cargo-c2c',
                            'phone_pd_id': '+72222222222_id',
                        },
                        'roles': ['initiator'],
                        'sharing_key': 'sharing_key_3',
                        'sharing_url': 'http://test/sharing_key_1',
                        'additional_delivery_description': {},
                    },
                    {
                        'id': {
                            'order_id': order_id,
                            'order_provider_id': 'cargo-c2c',
                            'phone_pd_id': '+79999999999_id',
                        },
                        'roles': ['recipient'],
                        'sharing_key': 'sharing_key_3',
                        'sharing_url': 'http://test/sharing_key_2',
                        'additional_delivery_description': {},
                    },
                ],
            },
        )

    claim_info = await create_segment_with_performer(skip_client_notify=True)
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.get(
        '/api/integration/v1/claims/performer-position',
        params={'claim_id': claim_id},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'position': position,
        'route_points': [
            {'id': 1, 'type': 'source', 'visit_order': 1},
            {'id': 2, 'type': 'destination', 'visit_order': 2},
            {
                'id': 3,
                'type': 'return',
                'visit_order': 3,
                'sharing_link': 'http://test/sharing_key_2',
            },
        ],
    }


@pytest.mark.experiments3(
    name='control_claims_processing',
    consumers=['cargo-claims/c2c-clients-orders'],
    default_value={'enabled': True},
    is_config=True,
    clauses=[],
)
async def test_performer_position404(
        taxi_cargo_claims, create_default_claim, get_default_headers,
):
    response = await taxi_cargo_claims.get(
        '/api/integration/v1/claims/performer-position',
        params={'claim_id': create_default_claim.claim_id},
        headers=get_default_headers(),
    )
    assert response.status_code == 404


@pytest.mark.experiments3(
    name='control_claims_processing',
    consumers=['cargo-claims/c2c-clients-orders'],
    default_value={'enabled': True},
    is_config=True,
    clauses=[],
)
async def test_performer_position409(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    claim_info = await state_controller.apply(target_status='delivered_finish')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.get(
        '/api/integration/v1/claims/performer-position',
        params={'claim_id': claim_id},
        headers=get_default_headers(),
    )
    assert response.status_code == 409
