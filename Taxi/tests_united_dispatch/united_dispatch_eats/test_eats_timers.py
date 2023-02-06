import pytest


@pytest.mark.parametrize(
    """use_eats_timers, expected_timer_value, timer_exp_value""",
    [
        pytest.param(
            True,
            17,
            {
                'ud_eats': {
                    'calc_eta_from': ['eats-eta-routes', 'candidates'],
                    'return_eta_from': 'eats-eta-routes',
                },
            },
        ),
        pytest.param(
            False,
            15,
            {
                'ud_eats': {
                    'calc_eta_from': ['candidates'],
                    'return_eta_from': 'candidates',
                },
            },
        ),
    ],
)
async def test_eats_timers(
        taxi_united_dispatch_eats,
        state_taxi_order_created,
        get_single_waybill,
        experiments3,
        scoring,
        create_segment,
        make_eats_custom_context,
        use_eats_timers,
        expected_timer_value,
        timer_exp_value,
        mock_eats_eta,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eta_flow',
        consumers=['united-dispatch/eats_timers'],
        clauses=[],
        default_value=timer_exp_value,
    )
    await taxi_united_dispatch_eats.invalidate_caches(
        clean_update=False, cache_names=['experiments3-cache'],
    )

    mock_eats_eta(parking_duration=0, arrival_duration=17)

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 18},
                        {'id': 'dbid1_uuid2', 'score': 17},
                    ],
                },
            ],
        },
    )

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
    assert response.json()['candidate']['id'] == 'dbid1_uuid2'
    assert (
        response.json()['candidate']['route_info']['time']
        == expected_timer_value
    )


async def test_eats_eta_pickup_correctors_applied(
        taxi_united_dispatch_eats,
        experiments3,
        state_taxi_order_created,
        get_single_waybill,
        scoring,
        create_segment,
        make_eats_custom_context,
        mock_eats_eta,
):
    experiments3.add_config(
        name='eats_eta_correctors_pickup',
        consumers=['eats-eta-correctors/pickup'],
        default_value={'multiplier': 0, 'summand': 0},
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'transport_type',
                                    'arg_type': 'string',
                                    'value': 'pedestrian',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'zone_id',
                                    'arg_type': 'string',
                                    'value': 'moscow',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {'arg_name': 'distance'},
                                'type': 'not_null',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {'multiplier': 2, 'summand': 1000},
            },
        ],
    )
    experiments3.add_config(
        name='eats_eta_correctors_dropoff',
        consumers=['eats-eta-correctors/dropoff'],
        default_value={'multiplier': 0, 'summand': 0},
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

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 18},
                        {'id': 'dbid1_uuid2', 'score': 17},
                    ],
                },
            ],
        },
    )

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
    assert response.json()['candidate']['id'] == 'dbid1_uuid2'
    assert response.json()['candidate']['route_info']['time'] == 2 * 17 + 1000


@pytest.mark.parametrize(
    """timer_multiplier, expected_timer_value""",
    [pytest.param(1, 15), pytest.param(1.5, 22), pytest.param(2, 30)],
)
async def test_eats_candidates_pickup_correctors_applied(
        taxi_united_dispatch_eats,
        experiments3,
        state_taxi_order_created,
        get_single_waybill,
        scoring,
        create_segment,
        make_eats_custom_context,
        mock_eats_eta,
        timer_multiplier,
        expected_timer_value,
):
    experiments3.add_config(
        name='united_dispatch_eats_candidates_timer_corrector',
        consumers=['united-dispatch/eats-candidates-timer-kwargs'],
        default_value={'multiplier': 0, 'enabled': False},
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'courier_transport_type',
                                    'arg_type': 'string',
                                    'value': 'pedestrian',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {'multiplier': timer_multiplier, 'enabled': True},
            },
        ],
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eta_flow',
        consumers=['united-dispatch/eats_timers'],
        clauses=[],
        default_value={
            'ud_eats': {
                'calc_eta_from': ['candidates'],
                'return_eta_from': 'candidates',
            },
        },
    )
    await taxi_united_dispatch_eats.invalidate_caches(
        clean_update=False, cache_names=['experiments3-cache'],
    )

    mock_eats_eta()

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 18},
                        {'id': 'dbid1_uuid2', 'score': 17},
                    ],
                },
            ],
        },
    )

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
    assert response.json()['candidate']['id'] == 'dbid1_uuid2'
    assert (
        response.json()['candidate']['route_info']['time']
        == expected_timer_value
    )
