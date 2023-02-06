import copy

import pytest


CORP_EXP = {
    '01234567890123456789012345678912': {
        'experiment_name': 'cargo_eda_orders_special_requirements',
    },
}

_EXPERIMENTS_MERGE_BY_TAG = [
    {
        'consumer': 'cargo-claims/special-requirements',
        'merge_method': 'dicts_recursive_merge',
        'tag': 'claims_special_requirements',
    },
]


@pytest.fixture(name='exp_cargo_post_payment_special_requirements')
async def _exp_cargo_post_payment_special_requirements(
        experiments3, taxi_cargo_claims,
):
    async def wrapper():
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_post_payment_special_requirements',
            consumers=['cargo-claims/special-requirements'],
            clauses=[
                {
                    'title': 'post_payment',
                    'predicate': {
                        'init': {'arg_name': 'is_post_payment'},
                        'type': 'bool',
                    },
                    'value': {
                        'post_payment': {
                            'special_requirements': [
                                'post_payment_special_req',
                            ],
                        },
                    },
                },
            ],
            default_value={},
            merge_values_by=_EXPERIMENTS_MERGE_BY_TAG,
        )
        await taxi_cargo_claims.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_max_point_weight_special_req')
async def _exp_cargo_max_point_weight_special_req(
        experiments3, taxi_cargo_claims,
):
    async def wrapper(max_point_weight: float = 35):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_max_point_weight_special_requirements',
            consumers=['cargo-claims/special-requirements'],
            clauses=[
                {
                    'title': 'post_payment',
                    'predicate': {
                        'init': {
                            'value': max_point_weight,
                            'arg_name': 'max_point_weight',
                            'arg_type': 'double',
                        },
                        'type': 'gte',
                    },
                    'value': {
                        'max_point_weight': {
                            'special_requirements': [
                                'max_point_weight_requirement',
                                'too_heavy_no_walking_courier',
                            ],
                        },
                    },
                },
            ],
            default_value={},
            merge_values_by=_EXPERIMENTS_MERGE_BY_TAG,
        )
        await taxi_cargo_claims.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_expensive_special_requirements')
async def _exp_cargo_expensive_special_requirements(
        experiments3, taxi_cargo_claims,
):
    async def wrapper(cost=30):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_expensive_package_special_requirements',
            consumers=['cargo-claims/special-requirements'],
            clauses=[
                {
                    'title': 'high cost',
                    'predicate': {
                        'init': {
                            'value': cost,
                            'arg_name': 'summary_items_cost',
                            'arg_type': 'double',
                        },
                        'type': 'gte',
                    },
                    'value': {
                        'expensive_package': {
                            'special_requirements': ['expensive_package'],
                        },
                    },
                },
            ],
            default_value={},
            merge_values_by=_EXPERIMENTS_MERGE_BY_TAG,
        )
        await taxi_cargo_claims.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_short_order_special_requirements')
async def _exp_cargo_short_order_special_requirements(
        experiments3, taxi_cargo_claims,
):
    async def wrapper(total_distance=1000.0):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_short_order_special_requirements',
            consumers=['cargo-claims/special-requirements'],
            clauses=[
                {
                    'title': 'high cost',
                    'predicate': {
                        'init': {
                            'value': total_distance,
                            'arg_name': 'estimated_total_distance_meters',
                            'arg_type': 'double',
                        },
                        'type': 'lte',
                    },
                    'value': {
                        'short_order': {
                            'special_requirements': ['short_order'],
                        },
                    },
                },
            ],
            default_value={},
            merge_values_by=_EXPERIMENTS_MERGE_BY_TAG,
        )
        await taxi_cargo_claims.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_brand_id_special_requirements')
async def _exp_cargo_brand_id_special_requirements(
        experiments3, taxi_cargo_claims, default_brand_id,
):
    async def wrapper(total_distance=1000.0, brand_id=str(default_brand_id)):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_short_order_special_requirements',
            consumers=['cargo-claims/special-requirements'],
            clauses=[
                {
                    'title': 'high cost',
                    'predicate': {
                        'init': {
                            'predicates': [
                                {
                                    'init': {
                                        'value': brand_id,
                                        'arg_name': 'brand_id',
                                        'arg_type': 'string',
                                    },
                                    'type': 'eq',
                                },
                                {
                                    'init': {
                                        'value': total_distance,
                                        'arg_name': (
                                            'estimated_total_distance_meters'
                                        ),
                                        'arg_type': 'double',
                                    },
                                    'type': 'lte',
                                },
                            ],
                        },
                        'type': 'all_of',
                    },
                    'value': {
                        'short_order': {
                            'special_requirements': ['short_order'],
                        },
                    },
                },
            ],
            default_value={},
            merge_values_by=_EXPERIMENTS_MERGE_BY_TAG,
        )
        await taxi_cargo_claims.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.mark.config(
    CARGO_CLAIMS_SPECIAL_REQUIREMENTS_MAP={
        '__default__': {
            '__default__': {
                'eds': 'cargo_eds',
                'multipoints': 'cargo_multipoints',
            },
        },
    },
    CARGO_CORP_CLIENTS_CUSTOM_REQUIREMENTS=CORP_EXP,
)
@pytest.mark.experiments3(filename='exp.json')
async def test_get_special_requirements_eds(
        taxi_cargo_claims, create_claim_with_performer,
):
    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'cargo'}],
            'cargo_ref_id': create_claim_with_performer.claim_id,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'virtual_tariffs': [
            {
                'class': 'cargo',
                'special_requirements': [
                    {'id': 'cargo_eds'},
                    {'id': 'some_req'},
                ],
            },
        ],
    }


@pytest.mark.config(
    CARGO_CLAIMS_SPECIAL_REQUIREMENTS_MAP={'__default__': {'__default__': {}}},
    CARGO_CORP_CLIENTS_CUSTOM_REQUIREMENTS=CORP_EXP,
)
@pytest.mark.experiments3(filename='exp.json')
async def test_get_special_requirements_experiment_only(
        taxi_cargo_claims, create_claim_with_performer,
):
    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'express'}],
            'cargo_ref_id': create_claim_with_performer.claim_id,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'virtual_tariffs': [
            {'class': 'cargo', 'special_requirements': [{'id': 'some_req'}]},
            {'class': 'express', 'special_requirements': [{'id': 'some_req'}]},
        ],
    }


@pytest.mark.config(
    CARGO_CLAIMS_SPECIAL_REQUIREMENTS_MAP={
        '__default__': {
            '__default__': {
                'eds': 'cargo_eds',
                'multipoints': 'cargo_multipoints',
            },
        },
    },
    CARGO_CORP_CLIENTS_CUSTOM_REQUIREMENTS=CORP_EXP,
)
@pytest.mark.experiments3(filename='exp.json')
async def test_get_special_requirements_multipoints(
        taxi_cargo_claims, state_controller,
):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={'classes': [{'id': 'cargo'}], 'cargo_ref_id': claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'virtual_tariffs': [
            {
                'class': 'cargo',
                'special_requirements': [
                    {'id': 'cargo_eds'},
                    {'id': 'cargo_multipoints'},
                    {'id': 'some_req'},
                ],
            },
        ],
    }


@pytest.mark.config(
    CARGO_CORP_CLIENTS_CUSTOM_REQUIREMENTS=CORP_EXP,
    CARGO_CLAIMS_CORP_CLIENTS_FEATURES={
        '01234567890123456789012345678912': ['partial_delivery'],
    },
)
@pytest.mark.experiments3(filename='exp.json')
async def test_get_special_requirements_features(
        taxi_cargo_claims, state_controller, get_create_request_v2,
):
    create_request = copy.deepcopy(get_create_request_v2())
    create_request['features'] = [{'id': 'partial_delivery'}]
    state_controller.use_create_version('v2')
    state_controller.handlers().create.request = create_request
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id
    assert claim_info.claim_full_response['features'] == [
        {'id': 'partial_delivery'},
    ]

    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={'classes': [{'id': 'cargo'}], 'cargo_ref_id': claim_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'virtual_tariffs': [
            {
                'class': 'cargo',
                'special_requirements': [
                    {'id': 'cargo_eds'},
                    {'id': 'cargo_multipoints'},
                    {'id': 'partial_delivery_req'},
                ],
            },
        ],
    }


@pytest.mark.config(
    CARGO_CLAIMS_SPECIAL_REQUIREMENTS_MAP={
        '__default__': {
            '__default__': {
                'eds': 'cargo_eds',
                'multipoints': 'cargo_multipoints',
            },
            'cargo': {
                'eds': 'cargo_eds_cargo_class',
                'multipoints': 'cargo_multipoints_cargo_class',
            },
        },
        'moscow': {
            '__default__': {
                'eds': 'cargo_eds_moscow',
                'multipoints': 'cargo_multipoints_moscow',
            },
            'cargo': {
                'eds': 'cargo_eds_cargo_class_moscow',
                'multipoints': 'cargo_multipoints_cargo_class_moscow',
            },
        },
    },
    CARGO_CORP_CLIENTS_CUSTOM_REQUIREMENTS=CORP_EXP,
)
@pytest.mark.experiments3(filename='exp.json')
@pytest.mark.parametrize(
    'zone_id,taxi_classes,expected_virtual_tariffs',
    [
        # TODO: fix in CARGODEV-11356
        # pytest.param(
        #     None,
        #     ['express', 'cargo'],
        #     [
        #         {
        #             'class': 'cargo',
        #             'special_requirements': [
        #                 {'id': 'cargo_eds_cargo_class'},
        #                 {'id': 'cargo_multipoints_cargo_class'},
        #                 {'id': 'some_req'},
        #             ],
        #         },
        #         {
        #             'class': 'express',
        #             'special_requirements': [
        #                 {'id': 'cargo_eds'},
        #                 {'id': 'cargo_multipoints'},
        #                 {'id': 'some_req'},
        #             ],
        #         },
        #     ],
        #     id='no_zone_id',
        # ),
        pytest.param(
            'moscow',
            ['express', 'cargo'],
            [
                {
                    'class': 'cargo',
                    'special_requirements': [
                        {'id': 'cargo_eds_cargo_class_moscow'},
                        {'id': 'cargo_multipoints_cargo_class_moscow'},
                        {'id': 'some_req'},
                    ],
                },
                {
                    'class': 'express',
                    'special_requirements': [
                        {'id': 'cargo_eds_moscow'},
                        {'id': 'cargo_multipoints_moscow'},
                        {'id': 'some_req'},
                    ],
                },
            ],
            id='moscow',
        ),
        pytest.param(
            'spb',
            ['express', 'cargo'],
            [
                {
                    'class': 'cargo',
                    'special_requirements': [
                        {'id': 'cargo_eds_cargo_class'},
                        {'id': 'cargo_multipoints_cargo_class'},
                        {'id': 'some_req'},
                    ],
                },
                {
                    'class': 'express',
                    'special_requirements': [
                        {'id': 'cargo_eds'},
                        {'id': 'cargo_multipoints'},
                        {'id': 'some_req'},
                    ],
                },
            ],
            id='spb',
        ),
    ],
)
async def test_special_requirements_map_config(
        taxi_cargo_claims,
        state_controller,
        zone_id,
        taxi_classes,
        expected_virtual_tariffs,
):
    def update_taxi_class_and_zone(request):
        request['zone_id'] = zone_id

    state_controller.use_create_version('v2')
    state_controller.handlers().finish_estimate.update_request = (
        update_taxi_class_and_zone
    )
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': class_name} for class_name in taxi_classes],
            'cargo_ref_id': claim_id,
        },
    )
    assert response.status_code == 200
    assert response.json() == {'virtual_tariffs': expected_virtual_tariffs}


async def test_dragon_order(taxi_cargo_claims, create_segment_with_performer):
    segment = await create_segment_with_performer()
    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'express'}],
            'cargo_ref_id': f'order/{segment.cargo_order_id}',
        },
    )
    assert response.status_code == 200


@pytest.mark.config(
    CARGO_CLAIMS_CARGO_OPTION_TO_SPECIAL_REQUIREMENTS_EXPERIMENT_CONFIGS={
        'thermal_bag': 'thermal_bag_option_experiment',
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='thermal_bag_option_experiment',
    consumers=['cargo-claims/special-requirements'],
    clauses=[
        {
            'title': 'courier and express set tag',
            'value': {'tags': ['thermal_bag_tag']},
            'predicate': {
                'init': {
                    'set': ['courier', 'express'],
                    'arg_name': 'taxi_class',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
    ],
    is_config=True,
    default_value={'tags': []},
)
async def test_get_special_requirements_additional_option(
        taxi_cargo_claims, create_claim_with_performer,
):
    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'express'}, {'id': 'courier'}],
            'cargo_ref_id': create_claim_with_performer.claim_id,
        },
    )

    assert response.status_code == 200
    assert response.json()['virtual_tariffs'] == [
        # exists because it is claim tariff_class
        {'class': 'cargo', 'special_requirements': [{'id': 'cargo_eds'}]},
        {
            'class': 'courier',
            'special_requirements': [
                {'id': 'cargo_eds'},
                {'id': 'thermal_bag_tag'},
            ],
        },
        {
            'class': 'express',
            'special_requirements': [
                {'id': 'cargo_eds'},
                {'id': 'thermal_bag_tag'},
            ],
        },
    ]


@pytest.mark.config(CARGO_CORP_CLIENTS_CUSTOM_REQUIREMENTS=CORP_EXP)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_eda_orders_special_requirements',
    consumers=['cargo-claims/client-custom-requirements'],
    clauses=[
        {
            'title': 'courier and express set tag',
            'value': {'special_requirements': ['thermal_bag_tag']},
            'predicate': {'init': {}, 'type': 'true'},
        },
    ],
    is_config=True,
    default_value={'special_requirements': []},
)
async def test_client_requirements_for_all_classes(
        taxi_cargo_claims, create_claim_with_performer,
):
    """
    Test special requirements exists for both 'courier' and 'express' classes
    """

    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'express'}, {'id': 'courier'}],
            'cargo_ref_id': create_claim_with_performer.claim_id,
        },
    )

    assert response.status_code == 200
    assert response.json()['virtual_tariffs'] == [
        # exists because it is claim tariff_class
        {
            'class': 'cargo',
            'special_requirements': [
                {'id': 'cargo_eds'},
                {'id': 'thermal_bag_tag'},
            ],
        },
        {
            'class': 'courier',
            'special_requirements': [
                {'id': 'cargo_eds'},
                {'id': 'thermal_bag_tag'},
            ],
        },
        {
            'class': 'express',
            'special_requirements': [
                {'id': 'cargo_eds'},
                {'id': 'thermal_bag_tag'},
            ],
        },
    ]


async def test_post_payment_only_special_requirement(
        taxi_cargo_claims,
        create_segment_with_payment,
        exp_cargo_post_payment_special_requirements,
        exp_cargo_max_point_weight_special_req,
        mock_payment_create,
):
    """
        Check post_payment in special_req and max_point_weight is not.
    """
    # weight is 2*10.2 = 20.4, defined in utils_v2/get_request_items
    segment = await create_segment_with_payment(payment_method='card')

    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={'classes': [{'id': 'cargo'}], 'cargo_ref_id': segment.claim_id},
    )
    assert response.status_code == 200
    tariff = response.json()['virtual_tariffs'][0]
    assert tariff['class'] == 'cargo'
    assert {'id': 'post_payment_special_req'} in tariff['special_requirements']
    assert {'id': 'max_point_weight_requirement'} not in tariff[
        'special_requirements'
    ]


async def test_max_weight_special_requirement(
        taxi_cargo_claims,
        create_claim_with_performer,
        exp_cargo_max_point_weight_special_req,
):
    # weight is 3*10.2+5 = 35.6, defined in conftest/get_default_request
    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'cargo'}],
            'cargo_ref_id': create_claim_with_performer.claim_id,
        },
    )
    assert response.status_code == 200
    tariff = response.json()['virtual_tariffs'][0]
    assert tariff['class'] == 'cargo'
    assert {'id': 'max_point_weight_requirement'} in tariff[
        'special_requirements'
    ]
    assert {'id': 'too_heavy_no_walking_courier'} in tariff[
        'special_requirements'
    ]


@pytest.mark.parametrize('clause_cost, req_exists', [[30, True], [40, False]])
async def test_expensive_package_special_requirement(
        taxi_cargo_claims,
        create_claim_with_performer,
        exp_cargo_expensive_special_requirements,
        clause_cost,
        req_exists,
):
    # cost_sum is 10.4 * 3 + 0.2 * 1 = 31.4
    await exp_cargo_expensive_special_requirements(cost=clause_cost)
    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'cargo'}],
            'cargo_ref_id': create_claim_with_performer.claim_id,
        },
    )
    assert response.status_code == 200
    tariff = response.json()['virtual_tariffs'][0]
    assert tariff['class'] == 'cargo'
    if req_exists:
        assert {'id': 'expensive_package'} in tariff['special_requirements']
    else:
        assert {'id': 'expensive_package'} not in tariff[
            'special_requirements'
        ]


@pytest.mark.parametrize(
    'clause_distance, req_exists', [[500, False], [4000, True]],
)
async def test_short_order_special_requirement(
        taxi_cargo_claims,
        create_claim_with_performer,
        exp_cargo_short_order_special_requirements,
        clause_distance,
        req_exists,
):
    await exp_cargo_short_order_special_requirements(
        total_distance=clause_distance,
    )
    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'cargo'}],
            'cargo_ref_id': create_claim_with_performer.claim_id,
        },
    )
    assert response.status_code == 200
    tariff = response.json()['virtual_tariffs'][0]
    assert tariff['class'] == 'cargo'
    if req_exists:
        assert {'id': 'short_order'} in tariff['special_requirements']
    else:
        assert {'id': 'short_order'} not in tariff['special_requirements']


@pytest.mark.parametrize(
    'clause_distance, req_exists', [[500, False], [4000, True]],
)
async def test_brand_id_special_requirement(
        taxi_cargo_claims,
        create_claim_with_performer,
        exp_cargo_brand_id_special_requirements,
        clause_distance,
        req_exists,
):
    await exp_cargo_brand_id_special_requirements(
        total_distance=clause_distance,
    )
    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'cargo'}],
            'cargo_ref_id': create_claim_with_performer.claim_id,
        },
    )
    assert response.status_code == 200
    tariff = response.json()['virtual_tariffs'][0]
    assert tariff['class'] == 'cargo'
    if req_exists:
        assert tariff['special_requirements'] == [
            {'id': 'cargo_eds'},
            {'id': 'short_order'},
        ]
    else:
        assert tariff['special_requirements'] == [{'id': 'cargo_eds'}]


async def test_merged_special_requirements(
        taxi_cargo_claims,
        create_segment_with_payment,
        exp_cargo_post_payment_special_requirements,
        exp_cargo_max_point_weight_special_req,
        exp_cargo_expensive_special_requirements,
        mock_payment_create,
):
    """
        Check post_payment, max_point_weight
        and expensive_package requirements in response
    """
    # weight is 2*10.2 = 20.4, defined in utils_v2/get_request_items
    await exp_cargo_max_point_weight_special_req(max_point_weight=20)
    segment = await create_segment_with_payment(payment_method='card')

    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={'classes': [{'id': 'cargo'}], 'cargo_ref_id': segment.claim_id},
    )
    assert response.status_code == 200
    tariff = response.json()['virtual_tariffs'][0]
    assert tariff['class'] == 'cargo'
    assert {'id': 'post_payment_special_req'} in tariff['special_requirements']
    assert {'id': 'max_point_weight_requirement'} in tariff[
        'special_requirements'
    ]
    assert {'id': 'too_heavy_no_walking_courier'} in tariff[
        'special_requirements'
    ]
    assert {'id': 'expensive_package'} in tariff['special_requirements']


@pytest.mark.config(
    CARGO_CLAIMS_REQUIREMENTS_TO_SPECIAL_REQUIREMENT_LISTS_MAP={
        'cargo': {'pro_courier': ['pro_courier_spec1', 'pro_courier_spec2']},
    },
)
async def test_get_multi_special_requirements_pro_courier(
        taxi_cargo_claims, state_controller, get_default_request,
):
    create_request = copy.deepcopy(get_default_request(pro_courier=True))
    state_controller.handlers().create.request = create_request
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'cargo'}, {'id': 'express'}],
            'cargo_ref_id': claim_id,
        },
    )
    assert response.status_code == 200
    assert response.json()['virtual_tariffs'] == [
        {
            'class': 'cargo',
            'special_requirements': [
                {'id': 'cargo_eds'},
                {'id': 'pro_courier_spec1'},
                {'id': 'pro_courier_spec2'},
            ],
        },
        {'class': 'express', 'special_requirements': [{'id': 'cargo_eds'}]},
    ]


@pytest.mark.config(
    CARGO_CLAIMS_REQUIREMENTS_TO_SPECIAL_REQUIREMENT_LISTS_MAP={
        'cargo': {'extra_requirement': ['extra_requirement_spec1']},
    },
)
async def test_get_special_requirements_by_extra_requirements(
        taxi_cargo_claims, prepare_state, get_segment,
):
    segment_id = await prepare_state(
        visit_order=3,
        cargo_pricing_flow=True,
        client_extra_requirement=17,
        finish_estimate_extra_requirement=18,
    )
    claim_id = (await get_segment(segment_id))['diagnostics']['claim_id']

    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'cargo'}, {'id': 'express'}],
            'cargo_ref_id': claim_id,
        },
    )
    assert response.status_code == 200
    assert response.json()['virtual_tariffs'] == [
        {
            'class': 'cargo',
            'special_requirements': [
                {'id': 'cargo_eds'},
                {'id': 'extra_requirement_spec1'},
            ],
        },
        {'class': 'express', 'special_requirements': [{'id': 'cargo_eds'}]},
    ]


@pytest.mark.config(
    CARGO_CLAIMS_REQUIREMENTS_TO_SPECIAL_REQUIREMENT_LISTS_MAP={
        'cargo': {'extra_requirement': ['extra_requirement_spec1']},
    },
)
async def test_get_special_requirements_by_false_extra_requirements(
        taxi_cargo_claims, prepare_state, get_segment,
):
    segment_id = await prepare_state(
        visit_order=3,
        cargo_pricing_flow=True,
        client_extra_requirement=17,
        finish_estimate_extra_requirement=False,
    )
    claim_id = (await get_segment(segment_id))['diagnostics']['claim_id']

    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'cargo'}, {'id': 'express'}],
            'cargo_ref_id': claim_id,
        },
    )
    assert response.status_code == 200
    assert response.json()['virtual_tariffs'] == [
        {'class': 'cargo', 'special_requirements': [{'id': 'cargo_eds'}]},
        {'class': 'express', 'special_requirements': [{'id': 'cargo_eds'}]},
    ]


@pytest.mark.config(
    CARGO_CLAIMS_REQUIREMENTS_TO_SPECIAL_REQUIREMENT_LISTS_MAP={
        'cargo': {'thermobag_covid': ['thermobag_confirmed']},
    },
)
async def test_get_special_requirements_thermobag_covid(
        taxi_cargo_claims,
        state_controller,
        create_default_cargo_c2c_order,
        mock_create_event,
):
    mock_create_event()
    claim = await create_default_cargo_c2c_order(cargo=True)
    claim_id = claim.claim_id

    response = await taxi_cargo_claims.post(
        '/v2/claims/special-requirements',
        json={
            'classes': [{'id': 'cargo'}, {'id': 'express'}],
            'cargo_ref_id': claim_id,
        },
    )
    assert response.status_code == 200
    assert response.json()['virtual_tariffs'] == [
        {
            'class': 'cargo',
            'special_requirements': [
                {'id': 'cargo_eds'},
                {'id': 'cargo_multipoints'},
                {'id': 'thermobag_confirmed'},
            ],
        },
        {
            'class': 'express',
            'special_requirements': [
                {'id': 'cargo_eds'},
                {'id': 'cargo_multipoints'},
            ],
        },
    ]
