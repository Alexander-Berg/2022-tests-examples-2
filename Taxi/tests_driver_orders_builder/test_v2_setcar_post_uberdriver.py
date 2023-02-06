import pytest

PARAMS = {'park_id': 'park1', 'order_id': 'test_order_id'}

MATCH_ALWAYS = {'predicate': {'type': 'true'}, 'enabled': True}

MATCH_UBERDRIVER = {
    'predicate': {
        'type': 'all_of',
        'init': {
            'predicates': [
                {
                    'type': 'contains',
                    'init': {
                        'arg_name': 'driver_tags',
                        'set_elem_type': 'string',
                        'value': 'uberdriver',
                    },
                },
                {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'application',
                        'arg_type': 'string',
                        'value': 'uberdriver',
                    },
                },
            ],
        },
    },
    'enabled': True,
}


def build_feature_support(is_detail_tip, is_semantic_colors):
    feature_support = {}
    if is_detail_tip:
        feature_support['detail_tip'] = '9.49'
    if is_semantic_colors:
        feature_support['semantic_color_scheme'] = '9.49'
    return feature_support


@pytest.mark.parametrize(
    'is_detail_tip, by_tag',
    [
        pytest.param(None, False, id='is_detail_tip has no effect'),
        pytest.param(None, True, id='check by_tag'),
    ],
)
@pytest.mark.parametrize(
    'show_destination, show_price, show_payment_type',
    # they are independent, no need to check all permutations
    [(True, True, True), (False, False, False)],
)
@pytest.mark.parametrize('has_surge', [True, False])
@pytest.mark.parametrize('semantic_colors', [True, False])
@pytest.mark.parametrize(
    'pricing_data_driver_meta, surge_patch',
    [
        pytest.param(
            {'setcar.show_surcharge': 777.55, 'setcar.show_surge': 1.95},
            'Сурж +777.55 ₽',
            id='get_surge_new_pricing_surcharge_1',
        ),
        pytest.param(
            {'setcar.show_surcharge': 990},
            'Сурж +990 ₽',
            id='get_surge_new_pricing_surcharge_2',
        ),
        pytest.param(
            {'setcar.show_surge': 1.95},
            'Сурж ×1.95',
            id='get_surge_new_pricing_surge',
        ),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_driver_tags_request': True},
)
@pytest.mark.config(MAX_SURGE_COEFF_BY_ZONE={'__default__': 10})
@pytest.mark.experiments3()
async def test_uberdriver(
        taxi_driver_orders_builder,
        show_destination,
        show_price,
        show_payment_type,
        has_surge,
        semantic_colors,
        by_tag,
        is_detail_tip,
        pricing_data_driver_meta,
        surge_patch,
        driver_tags_mocks,
        mockserver,
        taxi_config,
        load_json,
        experiments3,
        parks,
        order_proc,
):
    if by_tag:
        driver_tags_mocks.set_tags_info('park1', 'driver1', ['uberdriver'])

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_get_driver_app(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'park1_driver1',
                    'data': {
                        'locale': 'ru',
                        'taximeter_version': '9.50',
                        'taximeter_version_type': 'uber',
                        'taximeter_platform': 'android',
                        'fleet_type': 'uberdriver',
                    },
                },
            ],
        }

    parks.set_response('rus')

    experiments3.add_config(
        consumers=['driver-orders-builder/setcar'],
        match=MATCH_UBERDRIVER if by_tag else MATCH_ALWAYS,
        clauses=[],
        name='setcar_uberdriver_destination',
        default_value={'enabled': show_destination},
    )
    experiments3.add_config(
        consumers=['driver-orders-builder/setcar'],
        match=MATCH_UBERDRIVER if by_tag else MATCH_ALWAYS,
        clauses=[],
        name='setcar_uberdriver_price',
        default_value={'enabled': show_price},
    )
    experiments3.add_config(
        consumers=['driver-orders-builder/setcar'],
        match=MATCH_UBERDRIVER if by_tag else MATCH_ALWAYS,
        clauses=[],
        name='setcar_uberdriver_payment_type',
        default_value={'enabled': show_payment_type},
    )
    # await taxi_driver_orders_builder.invalidate_caches()

    setcar_json = load_json('setcar.json')
    setcar_json['address_to'] = {
        'City': 'Москва',
        'Description': '',
        'House': '1',
        'HouseSub1': '',
        'HouseSub2': '',
        'Lat': 55.698142,
        'Lon': 37.628561,
        'Porch': '',
        'Street': 'Ленина',
    }

    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='passenger_ratings_for_drivers',
        consumers=['driver-orders-builder/setcar'],
        clauses=[],
        default_value=True,
    )

    @mockserver.json_handler('/passenger-profile/passenger-profile/v1/profile')
    def _mock_passenger_profile(request):
        return {'first_name': 'Иаков', 'rating': '4.76'}

    order_proc.set_file(load_json, 'order_core_response.json')
    # add paid_supply for tag
    order_proc.order_proc['fields']['candidates'][0]['paid_supply'] = True
    order_proc.order_proc['fields']['order']['fixed_price'] = {}
    order_proc.order_proc['fields']['order']['fixed_price'][
        'paid_supply_price'
    ] = 59.0

    order_proc.order_proc['fields'].pop('price_modifiers')  # there's 0.9 coeff
    if has_surge:
        order_proc.order_proc['fields']['order']['request']['sp'] = 1.2
        if pricing_data_driver_meta:
            order_proc.order_proc['fields']['order']['pricing_data']['driver'][
                'meta'
            ] = pricing_data_driver_meta
    order_proc.order_proc['fields']['order']['application'] = 'android'
    order_proc.order_proc['fields']['order']['user_uid'] = 'something'
    order_proc.order_proc['fields']['order']['calc'] = {'time': 1255}

    taxi_config.set_values(
        {
            'TAXIMETER_VERSION_SETTINGS_BY_BUILD': {
                '__default__': {
                    'min': '9.00',
                    'current': '9.00',
                    'feature_support': {},
                },
                'taximeter-uber': {
                    'min': '9.00',
                    'current': '9.00',
                    'feature_support': build_feature_support(
                        is_detail_tip, semantic_colors,
                    ),
                },
            },
        },
    )

    request = {}
    request['order_id'] = PARAMS['order_id']
    request['driver'] = {
        'park_id': 'park1',
        'driver_profile_id': 'driver1',
        'alias_id': '3282ba102f1e4abcb2bc42b315074c10',
    }
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        '/v2/setcar', json=request,
    )

    assert response.status_code == 200
    response_json = response.json()['setcar']
    assert response_json['show_address'] == show_destination

    expected_ui = load_json(
        'response_ui'
        f'{"_semantic" if semantic_colors else "_1"}'
        f'{"_surge" if has_surge else ""}.json',
    )['ui']
    if has_surge and surge_patch:
        expected_ui['acceptance_items'][3]['tags'][0]['text'] = surge_patch

    if not show_destination:
        expected_ui['acceptance_items'][0]['items'].pop(-1)
        expected_ui['acceptance_items'][0]['items'][-1][
            'padding_type'
        ] = 'tiny_bottom'
        expected_ui['acceptance_items'][0]['items'][-1][
            'horizontal_divider_type'
        ] = 'none'

    # independent of has_surge
    if not show_price:
        expected_ui['acceptance_items'][2]['subtitle'] = ''

    if not show_payment_type:
        del expected_ui['acceptance_items'][2]['title_icon']
        expected_ui['acceptance_items'][2]['title'] = ' ★ 4.76'

    assert response_json['ui'] == expected_ui
