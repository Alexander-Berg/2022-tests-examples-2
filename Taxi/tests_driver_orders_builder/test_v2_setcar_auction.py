import pytest

ORDER_CORE_RESPONSE_FILE_NAME = 'order_core_response.json'
ORDER_CORE_RESPONSE_PRICE_INCREMENT_FILE_NAME = (
    'order_core_response_price_increment.json'
)
ORDER_CORE_RESPONSE_AUCTION_FILE_NAME = 'order_core_response_auction.json'
ORDER_CORE_RESPONSE_AUCTION_WITHOUT_CHENGE_PRICE_FILE_NAME = (
    'order_core_response_auction_without_change_price.json'
)

VALID_AUCTIN_VERSION = '2.00'
INVALID_AUCTION_VERSION = '10.00'


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_price_activity_rebuild': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='setcar_constructor_modifications_items',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'tyler': {'id': 'iamtyler'},
        'activity': {'id': 'activity_item'},
        'auction': {'id': 'auction_item'},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize(
    'auction_version', [VALID_AUCTIN_VERSION, INVALID_AUCTION_VERSION],
)
@pytest.mark.parametrize('enabled_auction', [True, False])
@pytest.mark.parametrize(
    'order_proc_file_name',
    [
        ORDER_CORE_RESPONSE_FILE_NAME,
        ORDER_CORE_RESPONSE_PRICE_INCREMENT_FILE_NAME,
        ORDER_CORE_RESPONSE_AUCTION_FILE_NAME,
    ],
)
async def test_setcar_auction(
        taxi_driver_orders_builder,
        taxi_config,
        load_json,
        experiments3,
        order_proc,
        params_wo_original_setcar,
        auction_version,
        enabled_auction,
        order_proc_file_name,
):

    taxi_config.set(
        TAXIMETER_VERSION_SETTINGS_BY_BUILD={
            '__default__': {'feature_support': {'auction': auction_version}},
        },
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_auction',
        consumers=['driver-orders-builder/setcar'],
        default_value={'enabled_auction': enabled_auction},
    )

    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(load_json, order_proc_file_name)

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']

    if (
            order_proc_file_name == ORDER_CORE_RESPONSE_AUCTION_FILE_NAME
            and enabled_auction
            and auction_version == VALID_AUCTIN_VERSION
    ):
        assert 'multioffer' in response_json
        assert 'auction' in response_json['multioffer']
        auction = response_json['multioffer']['auction']
        assert auction['price']['min_price'] == 100
        assert auction['price']['max_price'] == 900
        assert auction['price']['start_price'] == 499
        assert auction['price']['price_options'] == [400, 499, 500, 600]
        assert auction['iteration'] == 3
    else:
        assert 'multioffer' in response_json
        assert 'auction' not in response_json['multioffer']


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_price_activity_rebuild': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='setcar_constructor_modifications_items',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'tyler': {'id': 'iamtyler'},
        'activity': {'id': 'activity_item'},
        'auction': {'id': 'auction_item'},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_orders_builder_ui_parts_settings',
    consumers=['driver-orders-builder/ui-parts-settings-experiment'],
    clauses=[],
    merge_values_by=[
        {
            'tag': 'ui_experiments',
            'consumer': 'driver-orders-builder/ui-parts-settings-experiment',
            'merge_method': 'dicts_recursive_merge',
        },
    ],
    default_value={'hide_ui_parts': {}, 'show_ui_parts': {}},
)
@pytest.mark.parametrize(
    'auction_version', [VALID_AUCTIN_VERSION, INVALID_AUCTION_VERSION],
)
@pytest.mark.parametrize('enabled_auction', [True, False])
@pytest.mark.parametrize('show_total_price', [True, False])
@pytest.mark.parametrize('show_price_change', [True, False])
@pytest.mark.parametrize('price_change_view_type', ['tyler', 'item'])
async def test_show_price_increment_for_not_auction(
        taxi_driver_orders_builder,
        taxi_config,
        load_json,
        experiments3,
        order_proc,
        auction_version,
        enabled_auction,
        show_total_price,
        show_price_change,
        price_change_view_type,
        params_wo_original_setcar,
):
    taxi_config.set(
        TAXIMETER_VERSION_SETTINGS_BY_BUILD={
            '__default__': {
                'feature_support': {
                    'auction': auction_version,
                    'modifications_items': '2.00',
                },
            },
        },
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='ui_experiments_auction_show_price',
        consumers=['driver-orders-builder/ui-parts-settings-experiment'],
        merge_values_by=[
            {
                'tag': 'ui_experiments',
                'consumer': (
                    'driver-orders-builder/ui-parts-settings-experiment'
                ),
                'merge_method': 'dicts_recursive_merge',
            },
        ],
        default_value={
            'auction_ui_parts': {
                'show_price': show_total_price,
                'show_price_change': show_price_change,
                'price_change_view_type': price_change_view_type,
            },
            'hide_ui_parts': {},
            'show_ui_parts': {},
        },
    )
    experiments3.add_config(
        consumers=['driver-orders-builder/setcar'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='taximeter_cost_settings_accept',
        default_value={'show_income_cost': show_total_price},
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_auction',
        consumers=['driver-orders-builder/setcar'],
        default_value={'enabled_auction': enabled_auction},
    )

    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(load_json, ORDER_CORE_RESPONSE_FILE_NAME)

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']

    assert 'acceptance_items' in response_json['ui']
    assert len(response_json['ui']['acceptance_items']) == 1

    assert 'items' in response_json['ui']['acceptance_items'][0]
    assert len(response_json['ui']['acceptance_items'][0]['items']) == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_price_activity_rebuild': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='setcar_constructor_modifications_items',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'tyler': {'id': 'iamtyler'},
        'activity': {'id': 'activity_item'},
        'auction': {'id': 'auction_item'},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize(
    'auction_version', [VALID_AUCTIN_VERSION, INVALID_AUCTION_VERSION],
)
@pytest.mark.parametrize('enabled_auction', [True, False])
@pytest.mark.parametrize(
    'auction_tyler,auction_item,show_total_price,'
    'show_price_change,price_change_view_type,',
    [
        (None, None, False, False, 'tyler'),
        (
            {'id': 'auction_item', 'short_info': '+300 ₽', 'title': 'Торг'},
            None,
            False,
            True,
            'tyler',
        ),
        (None, None, True, False, 'tyler'),
        (
            {'id': 'auction_item', 'short_info': '+300 ₽', 'title': 'Торг'},
            None,
            True,
            True,
            'tyler',
        ),
        (None, None, False, False, 'item'),
        (
            None,
            {
                'type': 'detail',
                'title': 'Доплата пользователя',
                'subtitle': 'Включена в стоимость',
                'subdetail': '300 ₽',
            },
            False,
            True,
            'item',
        ),
        (None, None, True, False, 'item'),
        (
            None,
            {
                'type': 'detail',
                'title': 'Доплата пользователя',
                'subtitle': 'Включена в стоимость',
                'subdetail': '300 ₽',
            },
            True,
            True,
            'item',
        ),
    ],
)
async def test_show_price_increment_for_price_increment(
        taxi_driver_orders_builder,
        taxi_config,
        load_json,
        experiments3,
        order_proc,
        auction_tyler,
        auction_item,
        auction_version,
        enabled_auction,
        show_total_price,
        show_price_change,
        price_change_view_type,
        params_wo_original_setcar,
):
    taxi_config.set(
        TAXIMETER_VERSION_SETTINGS_BY_BUILD={
            '__default__': {
                'feature_support': {
                    'auction': auction_version,
                    'modifications_items': '2.00',
                },
            },
        },
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='ui_experiments_auction_show_price',
        consumers=['driver-orders-builder/ui-parts-settings-experiment'],
        merge_values_by=[
            {
                'tag': 'ui_experiments',
                'consumer': (
                    'driver-orders-builder/ui-parts-settings-experiment'
                ),
                'merge_method': 'dicts_recursive_merge',
            },
        ],
        default_value={
            'auction_ui_parts': {
                'show_price': show_total_price,
                'show_price_change': show_price_change,
                'price_change_view_type': price_change_view_type,
            },
            'hide_ui_parts': {},
            'show_ui_parts': {},
        },
    )
    experiments3.add_config(
        consumers=['driver-orders-builder/setcar'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='taximeter_cost_settings_accept',
        default_value={'show_income_cost': show_total_price},
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_auction',
        consumers=['driver-orders-builder/setcar'],
        default_value={'enabled_auction': enabled_auction},
    )

    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(
        load_json, ORDER_CORE_RESPONSE_PRICE_INCREMENT_FILE_NAME,
    )

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']

    assert 'acceptance_items' in response_json['ui']

    if not show_price_change:
        assert len(response_json['ui']['acceptance_items']) == 1

        assert 'items' in response_json['ui']['acceptance_items'][0]
        assert len(response_json['ui']['acceptance_items'][0]['items']) == 1

    if show_price_change and price_change_view_type == 'tyler':
        assert len(response_json['ui']['acceptance_items']) == 1
        assert 'items' in response_json['ui']['acceptance_items'][0]
        assert len(response_json['ui']['acceptance_items'][0]['items']) == 2
        assert (
            response_json['ui']['acceptance_items'][0]['items'][0]
            != auction_tyler
        )
        assert (
            response_json['ui']['acceptance_items'][0]['items'][1]
            == auction_tyler
        )

    if show_price_change and price_change_view_type == 'item':
        assert len(response_json['ui']['acceptance_items']) == 2

        assert 'items' in response_json['ui']['acceptance_items'][0]
        assert len(response_json['ui']['acceptance_items'][0]['items']) == 1
        assert (
            response_json['ui']['acceptance_items'][0]['items'][0]
            != auction_tyler
        )
        assert response_json['ui']['acceptance_items'][1] == auction_item


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_price_activity_rebuild': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='setcar_constructor_modifications_items',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'tyler': {'id': 'iamtyler'},
        'activity': {'id': 'activity_item'},
        'auction': {'id': 'auction_item'},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize(
    'auction_version', [VALID_AUCTIN_VERSION, INVALID_AUCTION_VERSION],
)
@pytest.mark.parametrize('enabled_auction', [True, False])
@pytest.mark.parametrize(
    'auction_tyler,auction_item,show_total_price,'
    'show_price_change,price_change_view_type,',
    [
        (None, None, False, False, 'tyler'),
        (
            {'id': 'auction_item', 'short_info': '+300 ₽', 'title': 'Торг'},
            None,
            False,
            True,
            'tyler',
        ),
        (None, None, True, False, 'tyler'),
        (
            {'id': 'auction_item', 'short_info': '+300 ₽', 'title': 'Торг'},
            None,
            True,
            True,
            'tyler',
        ),
        (None, None, False, False, 'item'),
        (
            None,
            {
                'type': 'detail',
                'title': 'Доплата пользователя',
                'subtitle': 'Включена в стоимость',
                'subdetail': '300 ₽',
            },
            False,
            True,
            'item',
        ),
        (None, None, True, False, 'item'),
        (
            None,
            {
                'type': 'detail',
                'title': 'Доплата пользователя',
                'subtitle': 'Включена в стоимость',
                'subdetail': '300 ₽',
            },
            True,
            True,
            'item',
        ),
    ],
)
async def test_show_price_increment_for_auction(
        taxi_driver_orders_builder,
        taxi_config,
        load_json,
        experiments3,
        order_proc,
        auction_tyler,
        auction_item,
        auction_version,
        enabled_auction,
        show_total_price,
        show_price_change,
        price_change_view_type,
        params_wo_original_setcar,
):
    taxi_config.set(
        TAXIMETER_VERSION_SETTINGS_BY_BUILD={
            '__default__': {
                'feature_support': {
                    'auction': auction_version,
                    'modifications_items': '2.00',
                },
            },
        },
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='ui_experiments_auction_show_price',
        consumers=['driver-orders-builder/ui-parts-settings-experiment'],
        merge_values_by=[
            {
                'tag': 'ui_experiments',
                'consumer': (
                    'driver-orders-builder/ui-parts-settings-experiment'
                ),
                'merge_method': 'dicts_recursive_merge',
            },
        ],
        default_value={
            'auction_ui_parts': {
                'show_price': show_total_price,
                'show_price_change': show_price_change,
                'price_change_view_type': price_change_view_type,
            },
            'hide_ui_parts': {},
            'show_ui_parts': {},
        },
    )
    experiments3.add_config(
        consumers=['driver-orders-builder/setcar'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='taximeter_cost_settings_accept',
        default_value={'show_income_cost': show_total_price},
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_auction',
        consumers=['driver-orders-builder/setcar'],
        default_value={'enabled_auction': enabled_auction},
    )

    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(load_json, ORDER_CORE_RESPONSE_AUCTION_FILE_NAME)

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']

    assert 'acceptance_items' in response_json['ui']

    if not show_price_change:
        assert len(response_json['ui']['acceptance_items']) == 1

        assert 'items' in response_json['ui']['acceptance_items'][0]
        assert len(response_json['ui']['acceptance_items'][0]['items']) == 1

    if show_price_change and price_change_view_type == 'tyler':
        assert len(response_json['ui']['acceptance_items']) == 1
        assert 'items' in response_json['ui']['acceptance_items'][0]
        assert len(response_json['ui']['acceptance_items'][0]['items']) == 2
        assert (
            response_json['ui']['acceptance_items'][0]['items'][0]
            != auction_tyler
        )
        assert (
            response_json['ui']['acceptance_items'][0]['items'][1]
            == auction_tyler
        )

    if show_price_change and price_change_view_type == 'item':
        assert len(response_json['ui']['acceptance_items']) == 2

        assert 'items' in response_json['ui']['acceptance_items'][0]
        assert len(response_json['ui']['acceptance_items'][0]['items']) == 1
        assert (
            response_json['ui']['acceptance_items'][0]['items'][0]
            != auction_tyler
        )
        assert response_json['ui']['acceptance_items'][1] == auction_item


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_price_activity_rebuild': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='setcar_constructor_modifications_items',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'tyler': {'id': 'iamtyler'},
        'activity': {'id': 'activity_item'},
        'auction': {'id': 'auction_item'},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize(
    'auction_version', [VALID_AUCTIN_VERSION, INVALID_AUCTION_VERSION],
)
@pytest.mark.parametrize('enabled_auction', [True, False])
@pytest.mark.parametrize('high_offer_ratio', [None, 0.5, 1, 2, 5])
@pytest.mark.parametrize(
    'order_proc_file_name',
    [
        ORDER_CORE_RESPONSE_FILE_NAME,
        ORDER_CORE_RESPONSE_PRICE_INCREMENT_FILE_NAME,
        ORDER_CORE_RESPONSE_AUCTION_FILE_NAME,
        ORDER_CORE_RESPONSE_AUCTION_WITHOUT_CHENGE_PRICE_FILE_NAME,
    ],
)
async def test_accept_toolbar(
        taxi_driver_orders_builder,
        taxi_config,
        load_json,
        experiments3,
        order_proc,
        params_wo_original_setcar,
        auction_version,
        enabled_auction,
        order_proc_file_name,
        high_offer_ratio,
):
    taxi_config.set(
        TAXIMETER_VERSION_SETTINGS_BY_BUILD={
            '__default__': {'feature_support': {'auction': auction_version}},
        },
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_auction',
        consumers=['driver-orders-builder/setcar'],
        default_value={'enabled_auction': enabled_auction},
    )

    if high_offer_ratio is not None:
        experiments3.add_experiment(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='full_auction',
            consumers=['driver-orders-builder/auction'],
            default_value={
                'enabled': True,
                'high_offer_ratio': high_offer_ratio,
            },
        )
    else:
        experiments3.add_experiment(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='full_auction',
            consumers=['driver-orders-builder/auction'],
            default_value={'enabled': True},
        )

    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(load_json, order_proc_file_name)

    exp3_recorder = experiments3.record_match_tries('full_auction')
    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']

    accept_toolbar_params = response_json['ui']['accept_toolbar_params']

    if (
            order_proc_file_name == ORDER_CORE_RESPONSE_AUCTION_FILE_NAME
            and enabled_auction
            and auction_version == VALID_AUCTIN_VERSION
    ):
        assert accept_toolbar_params['title'] == '{price}'
        assert accept_toolbar_params['subtitle'] == '7,3 км · 5 мин'

        if high_offer_ratio in (None, 0.5, 1, 2):
            assert (
                accept_toolbar_params['offer_info']['title']
                == 'Хорошее предложение'
            )
            assert (
                accept_toolbar_params['offer_info']['icon_start']['icon_type']
                == 'bullet_arrow_up'
            )
            assert (
                accept_toolbar_params['offer_info']['icon_start']['tint_color']
                == '#029154'
            )
            assert (
                accept_toolbar_params['offer_info']['icon_start'][
                    'tint_color_night'
                ]
                == '#1CC052'
            )

        else:
            assert 'offer_info' not in accept_toolbar_params

        assert (
            accept_toolbar_params['item_button']['title'] == 'Сделать ставку'
        )
        assert (
            accept_toolbar_params['item_button']['icon_title_start'][
                'icon_type'
            ]
            == 'filter_fill'
        )
        assert (
            accept_toolbar_params['item_button']['payload']['type']
            == 'change_offer_price'
        )
        match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
        assert match_tries[0].kwargs['tariff_zone'] == 'moscow'
        assert match_tries[0].kwargs['tariff_classes'] == ['auction']
        assert match_tries[0].kwargs['phone_id'] == '61c24345658288d92514fede'

        assert match_tries[0].kwargs['application'] == 'iphone'
        assert match_tries[0].kwargs['application.name'] == 'iphone'
        assert match_tries[0].kwargs['application.brand'] == 'yataxi'
        assert match_tries[0].kwargs['application.full_version'] == '3.73.5291'
        assert (
            match_tries[0].kwargs['application.platform_full_version']
            == '10.0.1'
        )
        assert (
            match_tries[0].kwargs['application.platform_version'] == '10.0.1'
        )
        assert match_tries[0].kwargs['application.platform'] == 'ios'
        assert match_tries[0].kwargs['version'] == '3.73.5291'

        assert match_tries[0].kwargs['device_model'] == ''
        assert match_tries[0].kwargs['device_make'] == ''

    elif (
        order_proc_file_name
        == ORDER_CORE_RESPONSE_AUCTION_WITHOUT_CHENGE_PRICE_FILE_NAME
        and enabled_auction
        and auction_version == VALID_AUCTIN_VERSION
    ):
        assert accept_toolbar_params['title'] == '{price}'
        assert accept_toolbar_params['subtitle'] == '7,3 км · 5 мин'

        if high_offer_ratio in (None, 0.5, 1):
            assert (
                accept_toolbar_params['offer_info']['title']
                == 'Хорошее предложение'
            )
            assert (
                accept_toolbar_params['offer_info']['icon_start']['icon_type']
                == 'bullet_arrow_up'
            )
            assert (
                accept_toolbar_params['offer_info']['icon_start']['tint_color']
                == '#029154'
            )
            assert (
                accept_toolbar_params['offer_info']['icon_start'][
                    'tint_color_night'
                ]
                == '#1CC052'
            )
        else:
            assert 'offer_info' not in accept_toolbar_params

        assert (
            accept_toolbar_params['item_button']['title'] == 'Сделать ставку'
        )
        assert (
            accept_toolbar_params['item_button']['icon_title_start'][
                'icon_type'
            ]
            == 'filter_fill'
        )
        assert (
            accept_toolbar_params['item_button']['payload']['type']
            == 'change_offer_price'
        )
        match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
        assert match_tries[0].kwargs['tariff_zone'] == 'moscow'
        assert match_tries[0].kwargs['tariff_classes'] == ['auction']
        assert match_tries[0].kwargs['phone_id'] == '61c24345658288d92514fede'

        assert match_tries[0].kwargs['application'] == 'iphone'
        assert match_tries[0].kwargs['application.name'] == 'iphone'
        assert match_tries[0].kwargs['application.brand'] == 'yataxi'
        assert match_tries[0].kwargs['application.full_version'] == '3.73.5291'
        assert (
            match_tries[0].kwargs['application.platform_full_version']
            == '10.0.1'
        )
        assert (
            match_tries[0].kwargs['application.platform_version'] == '10.0.1'
        )
        assert match_tries[0].kwargs['application.platform'] == 'ios'
        assert match_tries[0].kwargs['version'] == '3.73.5291'

        assert match_tries[0].kwargs['device_model'] == ''
        assert match_tries[0].kwargs['device_make'] == ''

    else:
        assert accept_toolbar_params['title'] == '1,3 км · 24 мин'
        assert accept_toolbar_params['subtitle'] == ''


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_price_activity_rebuild': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='setcar_constructor_modifications_items',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'tyler': {'id': 'iamtyler'},
        'activity': {'id': 'activity_item'},
        'auction': {'id': 'auction_item'},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize(
    'auction_version', [VALID_AUCTIN_VERSION, INVALID_AUCTION_VERSION],
)
@pytest.mark.parametrize('enabled_auction', [True, False])
@pytest.mark.parametrize(
    'order_proc_file_name',
    [
        ORDER_CORE_RESPONSE_FILE_NAME,
        ORDER_CORE_RESPONSE_PRICE_INCREMENT_FILE_NAME,
        ORDER_CORE_RESPONSE_AUCTION_FILE_NAME,
    ],
)
async def test_accept_button(
        taxi_driver_orders_builder,
        taxi_config,
        load_json,
        experiments3,
        order_proc,
        params_wo_original_setcar,
        auction_version,
        enabled_auction,
        order_proc_file_name,
):
    taxi_config.set(
        TAXIMETER_VERSION_SETTINGS_BY_BUILD={
            '__default__': {'feature_support': {'auction': auction_version}},
        },
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_auction',
        consumers=['driver-orders-builder/setcar'],
        default_value={'enabled_auction': enabled_auction},
    )

    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(load_json, order_proc_file_name)

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']

    accept_button_params = response_json['ui']['acceptance_button_params']

    if (
            order_proc_file_name == ORDER_CORE_RESPONSE_AUCTION_FILE_NAME
            and enabled_auction
            and auction_version == VALID_AUCTIN_VERSION
    ):
        assert accept_button_params['title'] == 'Принять {price}'

    else:
        assert accept_button_params['title'] == 'Принять'

    assert accept_button_params['subtitle'] == ''
