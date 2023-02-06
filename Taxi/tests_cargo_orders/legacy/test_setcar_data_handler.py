import copy


import pytest


async def test_setcar_data_by_claim_uuid(call_v1_setcar_data):
    response = await call_v1_setcar_data(
        request={'cargo_ref_id': 'cc0431b859b94324bb388d55a129a78e'},
    )
    assert response.status_code == 500


async def test_dragon_batch_order(
        call_v1_setcar_data, default_order_id, my_batch_waybill_info,
):
    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['is_batch_order']
    assert resp_body['points_count'] == 3


async def test_dragon_not_batch_order(
        call_v1_setcar_data,
        default_order_id,
        my_waybill_info,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('claim_full.json')

    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert not resp_body['is_batch_order']
    assert resp_body['points_count'] == 1

    assert _claims_full.times_called == 0


@pytest.mark.config(CARGO_ORDERS_SET_TAXIMETER_IS_BATCH_FLAG=True)
async def test_force_set_batch_order(
        call_v1_setcar_data, default_order_id, my_waybill_info,
):
    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    assert response.json()['is_batch_order']


async def test_dragon_eta_max(
        call_v1_setcar_data, default_order_id, my_batch_waybill_info,
):
    my_batch_waybill_info['execution']['segments'][0]['eta'] = 2
    my_batch_waybill_info['execution']['segments'][1]['eta'] = 3

    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    assert response.json()['eta'] == 3


async def test_dragon_order_base(
        call_v1_setcar_data, default_order_id, my_waybill_info,
):
    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'claim_id': 'claim_uuid_1',
        'claim_ids': ['claim_uuid_1'],
        'comment': 'Заказ с подтверждением по СМС.',
        'is_batch_order': False,
        'is_picker_order': False,
        'points_count': 1,
        'comment_overwrites': [],
        'corp_client_ids': ['5e36732e2bc54e088b1466e08e31c486'],
        'taximeter_tylers': [],
    }


async def test_eda_order_base(
        call_v1_setcar_data,
        default_order_id,
        waybill_info_pull_dispatch,
        mock_blackbox_info,
        experiments3,
):
    segments = waybill_info_pull_dispatch['execution']['segments']
    courier_demand_multiplier = 1.5
    # pylint: disable=invalid-name
    claims_courier_demand_multiplier = [
        {
            'claim_id': segments[0]['claim_id'],
            'courier_demand_multiplier': 1.4,
        },
        {
            'claim_id': segments[1]['claim_id'],
            'courier_demand_multiplier': 1.6,
        },
    ]
    mock_blackbox_info(
        courier_demand_multiplier=courier_demand_multiplier,
        claims_courier_demand_multiplier=claims_courier_demand_multiplier,
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_enable_eats_courier_by_region',
        consumers=['cargo-orders/fetch-courier-demand-info'],
        clauses=[
            {
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'value': '213',
                        'arg_name': 'region_id',
                        'arg_type': 'string',
                    },
                },
                'value': {'enabled': True},
            },
        ],
        default_value={'enabled': False},
    )
    response = await call_v1_setcar_data(
        request={
            'cargo_ref_id': f'order/{default_order_id}',
            'tariff_class': 'eda',
        },
    )
    assert response.status_code == 200
    assert response.json()['custom_context'] == {
        'depot_id': '23456',
        'dispatch_type': 'pull-dispatch',
        'region_id': 213,
        'courier_demand_level': courier_demand_multiplier,
        'claims_courier_demand_level': claims_courier_demand_multiplier,
    }


def add_items_with_overweight(waybill):
    special_requirements = waybill['waybill']['special_requirements']
    tariff = special_requirements['virtual_tariffs'][0]
    tariff['special_requirements'].append(
        {'id': 'max_point_weight_requirement'},
    )

    def append_points(point_id):
        point = copy.deepcopy(waybill['execution']['points'][0])
        point['type'] = 'destination'
        point['point_id'] = point_id
        waybill['execution']['points'].append(point)

    append_points('new_id1')
    append_points('new_id2')
    append_points('new_id3')

    def append_items(dropoff_id, quantity, weight=None):
        pickup_id = waybill['execution']['points'][0]['point_id']
        return_id = waybill['execution']['points'][2]['point_id']
        item = {
            'dropoff_point': dropoff_id,
            'quantity': quantity,
            'title': 'some_item',
            'item_id': '',
            'pickup_point': pickup_id,
            'return_point': return_id,
        }
        if weight is not None:
            item['weight'] = weight
        waybill['waybill']['items'].append(item)

    append_items(dropoff_id='new_id3', quantity=2, weight=3.0)
    append_items(dropoff_id='new_id1', quantity=3, weight=7.0)
    append_items(dropoff_id='new_id2', quantity=2, weight=14.0)
    append_items(dropoff_id='new_id2', quantity=1, weight=7.0)
    append_items(dropoff_id='new_id1', quantity=2, weight=3.0)
    append_items(dropoff_id='new_id1', quantity=1, weight=None)


@pytest.mark.config(CARGO_ORDERS_ITEMS_OVERWEIGHT_CONFIG={'cargo': 20.0})
async def test_dragon_order_with_overweight(
        call_v1_setcar_data, default_order_id, my_waybill_info,
):
    add_items_with_overweight(my_waybill_info)

    response = await call_v1_setcar_data(
        request={
            'cargo_ref_id': f'order/{default_order_id}',
            'tariff_class': 'cargo',
        },
    )
    assert response.status_code == 200
    # (7*3 + 3*2)-20 + (14*2 + 7*1)-20 = 22
    expected_comment = (
        'Опция \'тяжелая посылка\': перевес 22 кг.\n'
        'Заказ с подтверждением по СМС.\n'
        'Количество точек маршрута: 4.'
    )
    assert response.json()['comment'] == expected_comment


@pytest.mark.config(CARGO_ORDERS_ITEMS_OVERWEIGHT_CONFIG={'cargo': 35.0})
async def test_dragon_order_with_zero_overweight(
        call_v1_setcar_data, default_order_id, my_waybill_info,
):
    add_items_with_overweight(my_waybill_info)
    response = await call_v1_setcar_data(
        request={
            'cargo_ref_id': f'order/{default_order_id}',
            'tariff_class': 'cargo',
        },
    )
    assert response.status_code == 200
    # (14*2 + 7*1)-35 = 0
    expected_comment = (
        'Заказ с подтверждением по СМС.\n' 'Количество точек маршрута: 4.'
    )
    assert response.json()['comment'] == expected_comment


async def test_dragon_order_with_profi_courier_comment(
        call_v1_setcar_data, default_order_id, my_waybill_info,
):
    waybill = my_waybill_info
    special_requirements = waybill['waybill']['special_requirements']
    tariff = special_requirements['virtual_tariffs'][0]
    tariff['special_requirements'].append({'id': 'pro_courier'})

    response = await call_v1_setcar_data(
        request={
            'cargo_ref_id': f'order/{default_order_id}',
            'tariff_class': 'cargo',
        },
    )
    assert response.status_code == 200
    expected_comment = (
        'Опция \'Профи-курьер\'.\n' 'Заказ с подтверждением по СМС.'
    )
    assert response.json()['comment'] == expected_comment


async def test_dragon_no_sms_order(
        call_v1_setcar_data, default_order_id, my_waybill_info,
):
    for point in my_waybill_info['execution']['points']:
        point['need_confirmation'] = False

    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    assert response.json()['comment'] == ''


async def test_dragon_batch_order_with_one_point_a(
        call_v1_setcar_data, default_order_id, my_batch_waybill_info,
):
    # Set point_A to the same location
    for point in my_batch_waybill_info['execution']['points']:
        if point['type'] == 'source':
            point['location']['coordinates'] = [1, 2]

    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['is_batch_order']
    assert resp_body['points_count'] == 2


async def test_dragon_pull_dispatch_order_points_count(
        call_v1_setcar_data, default_order_id, my_multipoints_waybill_info,
):
    my_multipoints_waybill_info['dispatch']['is_pull_dispatch'] = True

    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['points_count'] == 1


async def test_alive_batch_allowed(
        call_v1_setcar_data, default_order_id, my_waybill_info,
):
    my_waybill_info['execution']['segments'][0]['allow_alive_batch_v1'] = True

    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200

    assert response.json()['is_batch_order']


@pytest.mark.config(
    CARGO_ORDERS_COMMENT_OVERWRITE_SETTINGS={
        'enabled': True,
        'allowed_tariffs': ['eda', 'lavka'],
    },
)
async def test_overwrite_comments_for_eda(
        call_v1_setcar_data, default_order_id, my_waybill_info,
):
    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'overwrites_for_courier': [
            {'tariff': 'eda', 'comment': 'comment for eda'},
            {'tariff': 'lavka', 'comment': 'comment for lavka'},
            {'tariff': 'courier', 'comment': 'not allowed'},
        ],
    }
    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    assert response.json()['comment_overwrites'] == [
        {'comment': 'comment for eda', 'tariff': 'eda'},
        {'comment': 'comment for lavka', 'tariff': 'lavka'},
    ]


SURGE_CONTEXT_RUB = {
    'surge_data': {'enabled': True, 'currency_code': 'RUB', 'price': '40.3'},
}

SURGE_CONTEXT_USD = {
    'surge_data': {'enabled': True, 'currency_code': 'USD', 'price': '40.3'},
}

SURGE_CONTEXT_INCORRECT = {
    'surge_data': {'enabled': True, 'currency_code': 0, 'price': 'ten'},
}

INCOMPLETE_SURGE_CONTEXT = {'surge_data': {'enabled': True}}

SURGE_CONTEXT_WITHOUT_PRICE = {'surge_data': {'currency_code': 'RUB'}}


@pytest.mark.parametrize(
    'first_context, second_context, surge_offer',
    [
        (
            SURGE_CONTEXT_RUB,
            SURGE_CONTEXT_RUB,
            {'currency': '₽', 'currency_code': 'RUB', 'price': '80.6'},
        ),
        (
            SURGE_CONTEXT_USD,
            SURGE_CONTEXT_RUB,
            {'currency': '$', 'currency_code': 'USD', 'price': '40.3'},
        ),
        (
            SURGE_CONTEXT_INCORRECT,
            SURGE_CONTEXT_RUB,
            {'currency': '₽', 'currency_code': 'RUB', 'price': '40.3'},
        ),
        (
            INCOMPLETE_SURGE_CONTEXT,
            INCOMPLETE_SURGE_CONTEXT,
            None,  # check that field surge_offer is presented
        ),
        (SURGE_CONTEXT_WITHOUT_PRICE, SURGE_CONTEXT_WITHOUT_PRICE, None),
    ],
)
@pytest.mark.translations(
    tariff={
        'currency_sign.rub': {'ru': '₽'},
        'currency_sign.usd': {'ru': '$', 'en': '$'},
    },
)
async def test_dragon_surge_offer(
        call_v1_setcar_data,
        default_order_id,
        my_batch_waybill_info,
        first_context,
        second_context,
        surge_offer,
):
    my_batch_waybill_info['execution']['segments'][0][
        'custom_context'
    ] = first_context
    my_batch_waybill_info['execution']['segments'][1][
        'custom_context'
    ] = second_context

    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    response_json = response.json()
    if surge_offer:
        assert response_json['surge_offer'] == surge_offer
    else:
        assert 'surge_offer' not in response_json


@pytest.mark.parametrize(
    ('features', 'expected_flag'),
    (([{'id': 'picker_order'}], True), ([], False)),
)
async def test_is_picker_order(
        call_v1_setcar_data,
        default_order_id,
        my_waybill_info,
        features,
        expected_flag,
):
    my_waybill_info['execution']['segments'][0]['claim_features'] = features
    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    response_json = response.json()
    if expected_flag:
        assert response_json['is_picker_order'] is True


async def test_post_payment_comment(
        call_v1_setcar_data, default_order_id, waybill_state,
):
    """
        Check post_payment reminder is passed to setcar.
    """
    waybill_state.set_post_payment()

    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    assert (
        response.json()['comment']
        == 'Заказ с наложенным платежом.\nЗаказ с подтверждением по СМС.'
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_instructions_deeplink',
    consumers=['cargo-orders/setcar-data'],
    clauses=[],
    default_value={'deeplink': 'http://test/link'},
)
async def test_instructions_deeplink(
        call_v1_setcar_data, default_order_id, experiments3, mockserver,
):
    exp3_recorder = experiments3.record_match_tries(
        'cargo_orders_instructions_deeplink',
    )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _driver_tags(request):
        assert request.json == {'dbid': 'park_1', 'uuid': 'driver_1'}
        return {'tags': ['test_tag_1']}

    response = await call_v1_setcar_data(
        request={
            'cargo_ref_id': f'order/{default_order_id}',
            'tariff_class': 'cargo',
            'performer_info': {
                'park_id': 'park_1',
                'driver_profile_id': 'driver_1',
            },
        },
    )
    assert response.status_code == 200
    assert response.json()['instructions_deeplink'] == 'http://test/link'

    # 2 instead 1 because taximeter tylers use
    # cargo-orders/setcar-data consumer too
    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=2)
    assert match_tries[0].kwargs['corp_client_ids'] == [
        '5e36732e2bc54e088b1466e08e31c486',
    ]
    assert match_tries[0].kwargs['corp_clients_count'] == 1
    assert match_tries[0].kwargs['segments_count'] == 1
    assert match_tries[0].kwargs['special_requirements'] == ['cargo_eds']
    assert not match_tries[0].kwargs['has_multipoints_segment']
    assert match_tries[0].kwargs['has_sms_confirmation']
    assert match_tries[0].kwargs['tariff_class'] == 'cargo'
    assert match_tries[0].kwargs['driver_tags'] == ['test_tag_1']


async def test_driver_tags_500(
        call_v1_setcar_data,
        default_order_id,
        my_batch_waybill_info,
        mockserver,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def mock_driver_tags(request):
        return mockserver.make_response(500, json={})

    response = await call_v1_setcar_data(
        request={
            'cargo_ref_id': f'order/{default_order_id}',
            'performer_info': {
                'park_id': 'park_1',
                'driver_profile_id': 'driver_1',
            },
        },
    )
    assert response.status_code == 200

    assert mock_driver_tags.times_called == 1


@pytest.mark.parametrize(
    'driver_tags, expected_deeplink',
    (
        pytest.param(
            ['tag1', 'tag2'], 'http://matched', id='driver_tags_matched',
        ),
        pytest.param([], None, id='driver_tags_missed'),
    ),
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_instructions_deeplink',
    consumers=['cargo-orders/setcar-data'],
    clauses=[
        {
            'title': 'Ссылка для курьера по тегам',
            'predicate': {
                'init': {
                    'value': 'tag1',
                    'arg_name': 'driver_tags',
                    'set_elem_type': 'string',
                },
                'type': 'contains',
            },
            'value': {'deeplink': 'http://matched'},
        },
    ],
    default_value={},
)
async def test_deeplink_by_driver_tags(
        call_v1_setcar_data,
        default_order_id,
        my_batch_waybill_info,
        mockserver,
        driver_tags,
        expected_deeplink,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def mock_driver_tags(request):
        assert request.json == {'dbid': 'park_1', 'uuid': 'driver_1'}
        return {'tags': driver_tags}

    response = await call_v1_setcar_data(
        request={
            'cargo_ref_id': f'order/{default_order_id}',
            'performer_info': {
                'park_id': 'park_1',
                'driver_profile_id': 'driver_1',
            },
        },
    )
    assert response.status_code == 200

    assert mock_driver_tags.times_called == 1


@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.parametrize(
    'tanker_keys', [[], ['cargo_legal_entity_tanker_key']],
)
async def test_dragon_order_with_comment_extra_parts(
        taxi_cargo_orders,
        default_order_id,
        my_waybill_info,
        experiments3,
        enabled,
        call_v1_setcar_data,
        tanker_keys: list,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_setcar_data_order_comment',
        consumers=['cargo-orders/setcar-data'],
        clauses=[],
        default_value={
            'enabled': enabled,
            'comment_extra_parts_tanker_keys': tanker_keys,
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    add_items_with_overweight(my_waybill_info)

    response = await call_v1_setcar_data(
        request={
            'cargo_ref_id': f'order/{default_order_id}',
            'tariff_class': 'cargo',
        },
    )
    assert response.status_code == 200
    expected_comment = (
        'Опция \'тяжелая посылка\': перевес 22 кг.\n'
        'Заказ с подтверждением по СМС.\n'
        'Количество точек маршрута: 4.'
    )

    if enabled and tanker_keys:
        expected_comment = 'Этот заказ юр. лица Доставка\n' + expected_comment
    assert response.json()['comment'] == expected_comment


@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.parametrize(
    'tanker_keys', [[], ['cargo_legal_entity_tanker_key']],
)
@pytest.mark.config(
    CARGO_ORDERS_COMMENT_OVERWRITE_SETTINGS={
        'enabled': True,
        'allowed_tariffs': ['eda', 'lavka'],
    },
)
async def test_overwrite_comments_extra_parts_for_eda(
        taxi_cargo_orders,
        default_order_id,
        my_waybill_info,
        experiments3,
        enabled,
        call_v1_setcar_data,
        tanker_keys: list,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_setcar_data_order_comment',
        consumers=['cargo-orders/setcar-data'],
        clauses=[],
        default_value={
            'enabled': enabled,
            'comment_extra_parts_tanker_keys': tanker_keys,
        },
    )
    await taxi_cargo_orders.invalidate_caches()

    my_waybill_info['execution']['segments'][0]['custom_context'] = {
        'overwrites_for_courier': [
            {'tariff': 'eda', 'comment': 'comment for eda'},
            {'tariff': 'lavka', 'comment': 'comment for lavka'},
            {'tariff': 'courier', 'comment': 'not allowed'},
        ],
    }
    response = await call_v1_setcar_data(
        request={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    expected_comments = [
        {'comment': 'comment for eda', 'tariff': 'eda'},
        {'comment': 'comment for lavka', 'tariff': 'lavka'},
    ]

    if enabled and tanker_keys:
        for value in expected_comments:
            value['comment'] = (
                'Этот заказ юр. лица Доставка\n' + value['comment']
            )
    assert response.json()['comment_overwrites'] == expected_comments


_EXPERIMENTS_MERGE_BY_TAG = [
    {
        'consumer': 'cargo-orders/setcar-data',
        'merge_method': 'dicts_recursive_merge',
        'tag': 'cargo_orders_taximeter_tyler_tag',
    },
]


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_setcar_data_door_to_door_taximeter_tyler',
    consumers=['cargo-orders/setcar-data'],
    clauses=[
        {
            'title': 'door_to_door_with_payment',
            'value': {
                'door_to_door_with_payment': {
                    'title': {'tanker_key': 'door_to_door_tanker_key'},
                    'short_info': {
                        'tanker_key': 'payments_tanker_key',
                        'tanker_args_names': {
                            'payment': 'payments',
                            'currency': 'currency',
                        },
                        'pricing_requirements_with_payment_names': [
                            'door_to_door',
                        ],
                    },
                },
            },
            'enabled': True,
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {'arg_name': 'has_door_to_door'},
                            'type': 'bool',
                        },
                        {
                            'init': {
                                'value': 'door_to_door',
                                'arg_name': (
                                    'pricing_requirements_with_payment'
                                ),
                                'set_elem_type': 'string',
                            },
                            'type': 'contains',
                        },
                    ],
                },
            },
            'extension_method': 'replace',
        },
    ],
    default_value={},
    merge_values_by=_EXPERIMENTS_MERGE_BY_TAG,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_setcar_data_overweight_taximeter_tyler',
    consumers=['cargo-orders/setcar-data'],
    clauses=[
        {
            'title': 'overweight',
            'value': {
                'overweight': {
                    'title': {'tanker_key': 'overweight_tanker_key'},
                },
            },
            'enabled': True,
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'predicates': [
                                    {
                                        'init': {
                                            'value': (
                                                'too_heavy_no_walking_courier'
                                            ),
                                            'arg_name': 'special_requirements',
                                            'set_elem_type': 'string',
                                        },
                                        'type': 'contains',
                                    },
                                    {
                                        'init': {
                                            'value': (
                                                'max_point_weight_requirement'
                                            ),
                                            'arg_name': 'special_requirements',
                                            'set_elem_type': 'string',
                                        },
                                        'type': 'contains',
                                    },
                                ],
                            },
                            'type': 'any_of',
                        },
                    ],
                },
            },
        },
    ],
    default_value={},
    merge_values_by=_EXPERIMENTS_MERGE_BY_TAG,
)
async def test_taximeter_tylers(
        call_v1_setcar_data,
        default_order_id,
        my_waybill_info,
        mock_cargo_pricing_calc_retrieve,
        set_order_calculations_ids,
):
    waybill = my_waybill_info
    special_requirements = waybill['waybill']['special_requirements']
    tariff = special_requirements['virtual_tariffs'][0]
    tariff['special_requirements'].append(
        {'id': 'max_point_weight_requirement'},
    )
    taxi_order_requirements = waybill['waybill']['taxi_order_requirements']
    taxi_order_requirements['door_to_door'] = True

    set_order_calculations_ids('preset_id')

    response = await call_v1_setcar_data(
        request={
            'cargo_ref_id': f'order/{default_order_id}',
            'tariff_class': 'cargo',
        },
    )
    assert response.status_code == 200
    assert response.json()['taximeter_tylers'] == [
        {'name': 'overweight', 'title': 'Перевес'},
        {
            'name': 'door_to_door_with_payment',
            'title': 'До двери',
            'short_info': '+150 ₽',
        },
    ]


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_setcar_show_full_current_route_at_acceptance_screen',
    consumers=['cargo-orders/setcar-data'],
    clauses=[],
    default_value={'show_full_current_route': True},
)
async def test_truncated_current_route(
        call_v1_setcar_data, default_order_id, experiments3, mockserver,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _driver_tags(request):
        assert request.json == {'dbid': 'park_1', 'uuid': 'driver_1'}
        return {'tags': ['test_tag_1']}

    response = await call_v1_setcar_data(
        request={
            'cargo_ref_id': f'order/{default_order_id}',
            'tariff_class': 'cargo',
            'performer_info': {
                'park_id': 'park_1',
                'driver_profile_id': 'driver_1',
            },
            'taximeter_app': {
                'version': '10.06 (8891)',
                'version_type': '',
                'platform': 'android',
            },
        },
    )
    assert response.status_code == 200
    assert response.json()['truncated_current_route'] == [
        {
            'type': 'source',
            'coordinates': [37.642979, 55.734977],
            'number_of_parcels': 1,
        },
        {
            'type': 'destination',
            'coordinates': [37.583, 55.9873],
            'number_of_parcels': 1,
        },
    ]
