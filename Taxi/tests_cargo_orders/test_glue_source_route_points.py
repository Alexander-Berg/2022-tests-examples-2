import pytest


@pytest.mark.parametrize('exp_enabled', [True, False])
@pytest.mark.parametrize('policy_enabled', [True, False])
@pytest.mark.parametrize('other_place_id', [True, False])
async def test_glue_source_route_points(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_glue_route_points,
        experiments3,
        exp_enabled,
        policy_enabled,
        other_place_id,
        mock_driver_tags_v1_match_profile,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_taximeter_route_points',
        consumers=['cargo-orders/taximeter-route-points'],
        clauses=[],
        default_value={
            'enabled': exp_enabled,
            'source_points_glue_policies': [
                {'enabled': policy_enabled, 'type': 'place_id'},
            ],
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    if other_place_id:
        waybill_info_glue_route_points['segments'][0]['custom_context'][
            'place_id'
        ] = 2
    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    expected_current_route_pts = [
        'source',
        'destination',
        'destination',
        'destination',
        'destination',
    ]
    if not exp_enabled or not policy_enabled or other_place_id:
        expected_current_route_pts = ['source', *expected_current_route_pts]
    assert expected_current_route_pts == [
        pt['type'] for pt in response.json()['current_route']
    ]
