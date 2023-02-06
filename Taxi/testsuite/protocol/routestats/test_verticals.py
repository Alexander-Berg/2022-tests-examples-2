from typing import List

import pytest


@pytest.mark.config(
    ZONEINFO_VERTICALS={
        'moscow': [
            {
                'type': 'group',
                'id': 'delivery',
                'can_make_order_from_summary': True,
                'tariffs': [{'class': 'courier'}, {'class': 'minivan'}],
            },
            {
                'type': 'group',
                'id': 'ultima',
                'can_make_order_from_summary': True,
                'tariffs': [{'class': 'business'}, {'class': 'comfortplus'}],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'verticals_enabled, supported_vertical_types, expected_verticals',
    [
        (False, ['group', 'tariff'], []),
        (True, [], []),
        (True, ['tariff'], []),
        (
            True,
            ['group', 'tariff'],
            [
                {'class': 'econom', 'type': 'tariff'},
                {
                    'id': 'ultima',
                    'tariffs': [
                        {'class': 'business'},
                        {'class': 'comfortplus'},
                    ],
                    'type': 'group',
                },
                {'class': 'vip', 'type': 'tariff'},
                {
                    'id': 'delivery',
                    'tariffs': [{'class': 'minivan'}],
                    'type': 'group',
                },
            ],
        ),
    ],
)
def test_routestats_verticals(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        local_services_base,
        experiments3,
        verticals_enabled,
        supported_vertical_types,
        expected_verticals,
):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='zoneinfo_verticals_support',
        consumers=['protocol/routestats'],
        clauses=[
            {
                'value': {'enabled': verticals_enabled},
                'predicate': {'type': 'true'},
            },
        ],
    )
    taxi_protocol.invalidate_caches()

    routestats_request = load_json('simple_request.json')
    routestats_request['supported_vertical_types'] = supported_vertical_types
    response = taxi_protocol.post('3.0/routestats', routestats_request)

    assert 200 == response.status_code
    assert expected_verticals == response.json().get('verticals', [])


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/routestats'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.parametrize(
    'tariffs_use_config_order, cfg_tariffs, resp_tariffs',
    [
        pytest.param(
            None,
            ['comfortplus', 'business', 'vip'],
            ['business', 'comfortplus', 'vip'],
            id='without_config_order_by_max_tariffs_1',
        ),
        pytest.param(
            None,
            ['business', 'vip', 'comfortplus'],
            ['business', 'comfortplus', 'vip'],
            id='without_config_order_by_max_tariffs_2',
        ),
        pytest.param(
            False,
            ['comfortplus', 'vip', 'business'],
            ['business', 'comfortplus', 'vip'],
            id='with_disabled_flag_order_by_max_tariffs_1',
        ),
        pytest.param(
            False,
            ['vip', 'business', 'comfortplus'],
            ['business', 'comfortplus', 'vip'],
            id='with_disabled_flag_order_by_max_tariffs_2',
        ),
        pytest.param(
            True,
            ['comfortplus', 'vip', 'business'],
            ['comfortplus', 'vip', 'business'],
            id='with_enabled_flag_order_by_config_1',
        ),
        pytest.param(
            True,
            ['vip', 'business', 'comfortplus'],
            ['vip', 'business', 'comfortplus'],
            id='with_enabled_flag_order_by_config_2',
        ),
        pytest.param(
            True,
            [
                'fake_tariff_1',
                'vip',
                'fake_tariff_2',
                'comfortplus',
                'fake_tariff_3',
            ],
            ['vip', 'comfortplus'],
            id='unkown_tariffs_does_not_matter',
        ),
    ],
)
def test_routestats_verticals_tariffs_order(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        local_services_base,
        taxi_config,
        tariffs_use_config_order,
        cfg_tariffs,
        resp_tariffs,
):
    ultima_vertical_cfg = {
        'type': 'group',
        'id': 'ultima',
        'can_make_order_from_summary': True,
        'tariffs': tariffs_list_to_cfg(cfg_tariffs),
    }

    if tariffs_use_config_order is not None:
        ultima_vertical_cfg[
            'tariffs_use_config_order'
        ] = tariffs_use_config_order

    taxi_config.set_values(
        {'ZONEINFO_VERTICALS': {'moscow': [ultima_vertical_cfg]}},
    )

    routestats_request = load_json('simple_request.json')
    routestats_request['supported_vertical_types'] = ['group', 'tariff']

    response = taxi_protocol.post('3.0/routestats', routestats_request)

    assert 200 == response.status_code

    check_vertical_tariffs(response, ultima_vertical_cfg['id'], resp_tariffs)


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/routestats'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.parametrize(
    'cfg_tariffs, without_point_b',
    [
        pytest.param(
            ['econom', 'comfortplus', 'minivan', 'business', 'vip'],
            True,
            id='all_tariffs_without_point_b',
        ),
        pytest.param(
            ['econom', 'comfortplus', 'minivan', 'business', 'vip'],
            False,
            id='all_tariffs_with_point_b',
        ),
        pytest.param(
            ['econom', 'business', 'vip'],
            True,
            id='some_tariffs_without_point_b',
        ),
        pytest.param(
            ['comfortplus', 'minivan', 'business'],
            False,
            id='some_tariffs_with_point_b',
        ),
    ],
)
def test_routestats_verticals_price(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        local_services_base,
        taxi_config,
        cfg_tariffs,
        without_point_b,
):
    vertical_id = 'test_price'

    price_vertical_cfg = {
        'type': 'group',
        'id': vertical_id,
        'can_make_order_from_summary': False,
        'tariffs': tariffs_list_to_cfg(cfg_tariffs),
    }

    taxi_config.set_values(
        {'ZONEINFO_VERTICALS': {'moscow': [price_vertical_cfg]}},
    )

    routestats_request = load_json('simple_request.json')
    routestats_request['supported_vertical_types'] = ['group']
    if without_point_b:
        routestats_request['route'] = routestats_request['route'][:1]

    response = taxi_protocol.post('3.0/routestats', routestats_request)

    assert 200 == response.status_code

    verticals = response.json().get('verticals', [])
    verticals = [x for x in verticals if x.get('id', '') == vertical_id]
    assert 1 == len(verticals)

    service_level_min_price = min_price(
        response.json().get('service_levels', []), cfg_tariffs,
    )
    expected_price = 'from {}\xa0$SIGN$$CURRENCY$'.format(
        service_level_min_price,
    )

    assert expected_price == verticals[0].get('price', '')


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/routestats'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.parametrize(
    'cfg_tariffs, hidden_tariff',
    [
        (['econom', 'business', 'comfortplus', 'vip'], ''),
        (['econom', 'business', 'comfortplus', 'vip'], 'comfortplus'),
        (['econom', 'business', 'comfortplus', 'vip'], 'minivan'),
    ],
)
def test_routestats_verticals_hidden_tariffs(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        local_services_base,
        taxi_config,
        cfg_tariffs,
        hidden_tariff,
):
    vertical_id = 'test_hidden'

    vertical_cfg = {
        'type': 'group',
        'id': vertical_id,
        'tariffs': tariffs_list_to_cfg(cfg_tariffs),
    }

    taxi_config.set_values({'ZONEINFO_VERTICALS': {'moscow': [vertical_cfg]}})

    if hidden_tariff != '':
        taxi_config.set_values(
            {
                'TARIFF_CATEGORIES_VISIBILITY': {
                    '__default__': {
                        hidden_tariff: {'visible_by_default': False},
                    },
                },
            },
        )

    routestats_request = load_json('simple_request.json')
    routestats_request['supported_vertical_types'] = ['group']

    response = taxi_protocol.post('3.0/routestats', routestats_request)

    assert 200 == response.status_code

    verticals = response.json().get('verticals', [])
    single_tariffs = [x for x in verticals if x.get('type', '') == 'tariff']
    assert hidden_tariff not in single_tariffs

    expected_tariffs = list(filter(lambda t: t != hidden_tariff, cfg_tariffs))
    check_vertical_tariffs(response, vertical_id, expected_tariffs)


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/routestats'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.config(
    ZONEINFO_VERTICALS={
        'moscow': [
            {
                'experiment_name': 'delivery_vertical',
                'can_make_order_from_summary': True,
                'type': 'group',
                'id': 'delivery',
                'title': 'tanker.delivery_title',
                'tariffs': [{'class': 'courier'}, {'class': 'minivan'}],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'expected_verticals, verticals_customization',
    [
        ([], {'enabled': False}),
        (
            [
                {'class': 'econom', 'type': 'tariff'},
                {'class': 'business', 'type': 'tariff'},
                {'class': 'comfortplus', 'type': 'tariff'},
                {'class': 'vip', 'type': 'tariff'},
                {'class': 'minivan', 'type': 'tariff'},
            ],
            {
                'enabled': True,
                'tariffs': [{'class': 'courier'}, {'class': 'express'}],
            },
        ),
        (
            [
                {'class': 'econom', 'type': 'tariff'},
                {'class': 'business', 'type': 'tariff'},
                {'class': 'comfortplus', 'type': 'tariff'},
                {'class': 'vip', 'type': 'tariff'},
                {
                    'id': 'delivery',
                    'tariffs': [{'class': 'minivan'}],
                    'type': 'group',
                },
            ],
            {'enabled': True, 'tariffs': [{'class': 'minivan'}]},
        ),
        (
            [
                {'class': 'econom', 'type': 'tariff'},
                {'class': 'business', 'type': 'tariff'},
                {'class': 'comfortplus', 'type': 'tariff'},
                {'class': 'vip', 'type': 'tariff'},
                {
                    'id': 'delivery',
                    'tariffs': [{'class': 'minivan'}],
                    'type': 'group',
                },
                {'class': 'minivan', 'type': 'tariff'},
            ],
            {
                'enabled': True,
                'tariffs': [{'class': 'minivan'}],
                'show_on_summary': ['minivan'],
            },
        ),
        (
            [
                {'class': 'econom', 'type': 'tariff'},
                {'class': 'business', 'type': 'tariff'},
                {'class': 'comfortplus', 'type': 'tariff'},
                {'class': 'vip', 'type': 'tariff'},
                {
                    'id': 'delivery',
                    'tariffs': [{'class': 'minivan'}],
                    'type': 'group',
                },
            ],
            {
                'enabled': True,
                'tariffs': [{'class': 'minivan'}, {'class': 'business'}],
                'show_on_summary': ['business'],
            },
        ),
    ],
)
def test_delivery_vertical_by_experiment(
        taxi_protocol,
        pricing_data_preparer,
        experiments3,
        load_json,
        local_services_base,
        expected_verticals,
        verticals_customization,
):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='delivery_vertical',
        consumers=['protocol/routestats'],
        clauses=[
            {'value': verticals_customization, 'predicate': {'type': 'true'}},
        ],
    )
    taxi_protocol.invalidate_caches()

    routestats_request = load_json('simple_request.json')
    routestats_request['supported_vertical_types'] = ['group']

    response = taxi_protocol.post('3.0/routestats', routestats_request)

    assert 200 == response.status_code
    assert expected_verticals == response.json().get('verticals', [])


def tariffs_list_to_cfg(tt):
    return list(map(lambda t: {'class': t}, tt))


def min_price(service_levels, all_tariffs):
    prices = []
    for sl in service_levels:
        if sl.get('class', '') in all_tariffs and 'price' in sl:
            price_value = ''.join(
                filter(lambda x: x.isdigit(), sl.get('price')),
            )
            prices.append(int(price_value))
    return min(prices)


def check_vertical_tariffs(response, vertical_id, expected_tariffs):
    verticals = response.json().get('verticals', [])
    verticals = [x for x in verticals if x.get('id', '') == vertical_id]
    assert 1 == len(verticals)
    assert tariffs_list_to_cfg(expected_tariffs) == verticals[0]['tariffs']


VERTICAL = 'vertical'


def _create_vert_ans(names: List[str]) -> List[dict]:
    verticals = []
    for name in names:
        if name == VERTICAL:
            verticals.append(
                {
                    'id': 'delivery',
                    'tariffs': [{'class': 'econom'}, {'class': 'vip'}],
                    'type': 'group',
                },
            )

        else:
            verticals.append({'class': name, 'type': 'tariff'})

    return verticals


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='zoneinfo_verticals_support',
    consumers=['protocol/routestats'],
    clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
)
@pytest.mark.config(
    ZONEINFO_VERTICALS={
        'moscow': [
            {
                'experiment_name': 'delivery_vertical',
                'can_make_order_from_summary': True,
                'type': 'group',
                'id': 'delivery',
                'title': 'tanker.delivery_title',
                'default_tariff': 'vip',
                'tariffs': [{'class': 'econom'}, {'class': 'vip'}],
            },
        ],
    },
)
@pytest.mark.parametrize(
    ('verticals_names', 'verticals_customization'),
    (
        pytest.param(
            ['business', 'comfortplus', VERTICAL, 'minivan'],
            {
                'enabled': True,
                'tariffs': [{'class': 'econom'}, {'class': 'vip'}],
            },
            id='vert_position',
        ),
        pytest.param(
            ['business', 'comfortplus', VERTICAL, 'vip', 'minivan'],
            {
                'enabled': True,
                'tariffs': [{'class': 'econom'}, {'class': 'vip'}],
                'show_on_summary': ['vip'],
            },
            id='default_class_position',
        ),
        pytest.param(
            ['econom', 'business', 'comfortplus', VERTICAL, 'minivan'],
            {
                'enabled': True,
                'tariffs': [{'class': 'econom'}, {'class': 'vip'}],
                'show_on_summary': ['econom'],
            },
            id='summary_class_position',
        ),
    ),
)
def test_vertical_order(
        taxi_protocol,
        pricing_data_preparer,
        experiments3,
        load_json,
        local_services_base,
        verticals_names,
        verticals_customization,
):

    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='delivery_vertical',
        consumers=['protocol/routestats'],
        clauses=[
            {'value': verticals_customization, 'predicate': {'type': 'true'}},
        ],
    )
    taxi_protocol.invalidate_caches()

    routestats_request = load_json('simple_request.json')
    routestats_request['supported_vertical_types'] = ['group']

    response = taxi_protocol.post('3.0/routestats', routestats_request)

    assert 200 == response.status_code
    assert _create_vert_ans(verticals_names) == response.json()['verticals']
