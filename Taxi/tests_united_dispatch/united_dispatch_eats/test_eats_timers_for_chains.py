import pytest


@pytest.mark.experiments3(
    name='eta_flow',
    consumers=['united-dispatch/eats_timers'],
    default_value={
        'ud_eats': {
            'calc_eta_from': ['eats-eta-routes'],
            'return_eta_from': 'eats-eta-routes',
        },
    },
    is_config=True,
)
async def test_due_for_chains_contains_x_b_a(
        taxi_united_dispatch_eats,
        state_taxi_order_created,
        get_single_waybill,
        create_segment,
        make_eats_custom_context,
        mock_eats_eta,
):
    mock_eats_eta(parking_duration=0, arrival_duration=17)

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        pickup_coordinates=[37.0, 55.0002],
        dropoff_coordinates=[37.0, 55.0],
    )

    await state_taxi_order_created()

    waybill = get_single_waybill()

    response = await taxi_united_dispatch_eats.post(
        '/performer-for-order',
        json={
            'order_id': waybill['waybill']['taxi_order_id'],
            'allowed_classes': ['eda'],
            'lookup': {'generation': 1, 'version': 1, 'wave': 1},
            'order': {'created': 1584378627.69, 'nearest_zone': 'moscow'},
        },
    )

    assert response.status_code == 200
    assert response.json()['candidate']['id'] == 'dbid1_uuid1'
    # 117 = arrival_duration + chain_info.left_time,
    # see static/test_eats_timers_for_chains/candidates.json
    assert response.json()['candidate']['route_info']['time'] == 117


async def test_pickup_correctors_applied_only_to_b_a(
        taxi_united_dispatch_eats,
        experiments3,
        state_taxi_order_created,
        get_single_waybill,
        create_segment,
        make_eats_custom_context,
        mock_eats_eta,
):
    experiments3.add_config(
        name='eats_eta_correctors_pickup',
        consumers=['eats-eta-correctors/pickup'],
        default_value={'multiplier': 2, 'summand': 0},
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eta_flow',
        consumers=['united-dispatch/eats_timers'],
        clauses=[],
        default_value={
            'ud_eats': {
                'calc_eta_from': ['eats-eta-routes'],
                'return_eta_from': 'eats-eta-routes',
            },
        },
    )
    await taxi_united_dispatch_eats.invalidate_caches(
        clean_update=False, cache_names=['experiments3-cache'],
    )

    mock_eats_eta(parking_duration=0, arrival_duration=17)

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        pickup_coordinates=[37.0, 55.0002],
        dropoff_coordinates=[37.0, 55.0],
    )

    await state_taxi_order_created()

    waybill = get_single_waybill()

    response = await taxi_united_dispatch_eats.post(
        '/performer-for-order',
        json={
            'order_id': waybill['waybill']['taxi_order_id'],
            'allowed_classes': ['eda'],
            'lookup': {'generation': 1, 'version': 1, 'wave': 1},
            'order': {'created': 1584378627.69, 'nearest_zone': 'moscow'},
        },
    )

    assert response.status_code == 200
    assert response.json()['candidate']['id'] == 'dbid1_uuid1'
    # 100 - chain_info.left_time, 17 - arrival_duration, 2 and 0 -
    # multiplier and summand respectively
    assert (
        response.json()['candidate']['route_info']['time'] == 100 + 17 * 2 + 0
    )
