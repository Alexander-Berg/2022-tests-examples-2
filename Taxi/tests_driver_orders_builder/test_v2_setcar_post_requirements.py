# pylint: disable=too-many-lines

import pytest

from tests_driver_orders_builder import utils

SETCAR_CREATE_URL = '/v2/setcar'
PARAMS = {
    'driver': {
        'park_id': 'park1',
        'driver_profile_id': 'driver1',
        'alias_id': '4d605a2849d747079b5d8c7012830419',
    },
    'order_id': 'test_order_id',
}
TRANSLATED_REQUIREMENTS = {
    'bicycle': 'Велосипед',
    'yellowcardnumber': 'Желтые номера',
}
LONG_TRIP = {
    'reverse': True,
    'subtitle': 'Долгая поездка',
    'title': '45 мин, 6.8 км',
    'type': 'default',
}


@pytest.mark.experiments3(filename='exp3_config_taximeter_settings.json')
@pytest.mark.config(
    EXPERIMENTS3_TO_TAXIMETER_SETTINGS_MAP={
        'experiments': [],
        'configs': [
            {
                'name': 'config_with_boolean',
                'field_name': 'enabled',
                'taximeter_settings_property': 'some_boolean_property',
            },
            {
                'name': 'config_full',
                'taximeter_settings_property': 'some_object_property',
            },
        ],
    },
)
@pytest.mark.parametrize(
    'requirements,expected_props',
    (
        pytest.param(
            None,
            {
                'some_boolean_property': True,
                'some_object_property': {'field': 'value'},
            },
            id='no_requirements',
        ),
        pytest.param(
            {'bicycle': 'yes', 'yellowcardnumber': True},
            {
                'some_boolean_property': True,
                'some_object_property': {'field1': 'value1'},
            },
            id='bicycle_requirement',
        ),
    ),
)
@pytest.mark.experiments3()
async def test_taximeter_settings_experiments(
        taxi_driver_orders_builder,
        mockserver,
        load_json,
        requirements,
        expected_props,
        setcar_create_params,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response3.json')
    if requirements:
        order_proc.order_proc['fields']['order']['request'][
            'requirements'
        ] = requirements

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    setcar = response.json()['setcar']
    for (name, val) in expected_props.items():
        assert setcar['taximeter_settings'][name] == val
    if requirements is not None:
        assert len(setcar['requirement_list']) == 2
        assert setcar['requirement_list'][0] in [
            {'id': key} for (key, value) in requirements.items()
        ]
        assert setcar['requirement_list'][1] in [
            {'id': key} for (key, value) in requirements.items()
        ]
    else:
        assert setcar['requirement_list'] is not None


REQUIREMENTS_ITEM_1 = {
    'type': 'default',
    'title': 'Комментарий',
    'primary_max_lines': 3,
    'secondary_max_lines': 1,
    'markdown': True,
    'subtitle': (
        '**2 бустера, Желтые номера, Кресло, 3–7 лет.**  \n'
        'Какой-то комментарий'
    ),
    'reverse': True,
}

REQUIREMENTS_ITEM_2 = {
    'type': 'default',
    'title': 'Комментарий',
    'primary_max_lines': 3,
    'secondary_max_lines': 1,
    'markdown': True,
    'subtitle': '**Большой кузов.**  \nКакой-то комментарий',
    'reverse': True,
}

REQUIREMENTS_ITEM_3 = {
    'type': 'default',
    'title': 'Комментарий',
    'primary_max_lines': 3,
    'secondary_max_lines': 1,
    'markdown': True,
    'subtitle': '**Велосипед.**  \nКакой-то комментарий',
    'reverse': True,
}

REQUIREMENTS_ITEM_4 = {
    'type': 'default',
    'title': 'Комментарий',
    'primary_max_lines': 3,
    'secondary_max_lines': 1,
    'markdown': True,
    'subtitle': '**Велосипед.**  \nКакой-то комментарий',
    'reverse': True,
}

REQUIREMENTS_ITEM_5 = {
    'type': 'default',
    'title': 'Комментарий',
    'primary_max_lines': 3,
    'secondary_max_lines': 1,
    'markdown': True,
    'subtitle': '**Велосипед.**',
    'reverse': True,
}

REQUIREMENTS_ITEM_6 = {
    'type': 'default',
    'title': 'Комментарий',
    'primary_max_lines': 3,
    'secondary_max_lines': 1,
    'markdown': True,
    'subtitle': '**Бустер, Кресло, 3–7 лет.**',
    'reverse': True,
}

REQUIREMENTS_ITEM_7 = {
    'type': 'default',
    'title': 'Комментарий',
    'primary_max_lines': 3,
    'secondary_max_lines': 1,
    'markdown': True,
    'subtitle': '**2 грузчика.**  \nКакой-то комментарий',
    'reverse': True,
}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_requirements_rebuild': True},
)
@pytest.mark.parametrize(
    'requirements,requirements_localized,source_type, drop_comment',
    [
        (
            {
                'yellowcardnumber': True,
                'childchair_for_child_tariff': [7, 3, 7],
            },
            REQUIREMENTS_ITEM_1,
            'yandex',
            False,
        ),
        ({'cargo_type': 'lcv_l'}, REQUIREMENTS_ITEM_2, 'yandex', False),
        ({'bicycle': True}, REQUIREMENTS_ITEM_3, 'yandex', False),
        ({'bicycle': True}, REQUIREMENTS_ITEM_4, 'yauber', False),
        ({'bicycle': True}, REQUIREMENTS_ITEM_5, 'yandex', True),
        (
            {'childchair_for_child_tariff': [7, 3]},
            REQUIREMENTS_ITEM_6,
            'yandex',
            True,
        ),
        ({'cargo_loaders': 2}, REQUIREMENTS_ITEM_7, 'yandex', False),
    ],
)
@pytest.mark.experiments3()
async def test_build_requirements(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        requirements,
        requirements_localized,
        source_type,
        drop_comment,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response3.json')
    order_proc.order_proc['fields']['order']['request'][
        'requirements'
    ] = requirements
    order_proc.order_proc['fields']['order']['source'] = source_type
    if drop_comment:
        order_proc.order_proc['fields']['order']['request'].pop('comment')

    setcar_json = load_json('setcar_requirements.json')
    request = PARAMS
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    setcar = response.json()['setcar']
    response_requirements = setcar['ui']['acceptance_items'][1]

    assert response_requirements == requirements_localized


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_requirements_rebuild': True,
        'enable_cargo_multipoints': True,
    },
)
@pytest.mark.parametrize(
    'tariff_class, expected_requirements',
    [('lavka', ['bicycle']), ('courier', ['bicycle', 'yellowcardnumber'])],
)
@pytest.mark.experiments3()
async def test_cargo_requirements_overwrite(
        order_proc,
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        mock_cargo_setcar_data,
        experiments3,
        tariff_class: str,
        expected_requirements: list,
        cargo_ref_id='cargo_claim_id_1',
        default_comment='default cargo comment',
):
    """
        Check 'yellowcardnumber' is hidden for 'lavka' performer.
        And is visible for another tariff performer.
    """
    mock_cargo_setcar_data(comment=default_comment)
    experiments_data = load_json('experiments3_defaults.json')
    for config in experiments_data['configs']:
        if config['name'] == 'driver_orders_builder_requirements':
            for clause in config['clauses']:
                if clause['alias'] == 'cargo':
                    clause['value'] = {
                        'bicycle': {},
                        'yellowcardnumber': {'mode': 'remove'},
                    }

    experiments3.add_experiments_json(experiments_data)

    order_proc.set_file(load_json, 'order_core_response3.json')
    order_proc.order_proc['fields']['candidates'][0][
        'tariff_class'
    ] = tariff_class
    proc_request = order_proc.order_proc['fields']['order']['request']
    proc_request['requirements'] = {'bicycle': True, 'yellowcardnumber': True}
    proc_request['cargo_ref_id'] = cargo_ref_id
    proc_request['corp_comment'] = 'Корп комментарий'
    proc_request['comment'] = 'комментарий из сервиса cargo-dispatch'
    proc_request['corp'] = {'client_id': 'corp_client_id_12312312312312312'}

    setcar_json = load_json('setcar_requirements.json')
    setcar_json['requirement_list'] = [
        {'id': 'bicycle'},
        {'id': 'yellowcardnumber'},
    ]
    request = PARAMS
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    setcar = response.json()['setcar']

    subtitle = next(
        i['subtitle']
        for i in setcar['ui']['acceptance_items']
        if i['type'] == 'default'
    )
    translated_requirements = ', '.join(
        [TRANSLATED_REQUIREMENTS[req] for req in expected_requirements],
    )
    assert subtitle == f'**{translated_requirements}.**  \n{default_comment}'
    setcar['requirement_list'].sort(key=lambda x: x['id'])
    assert setcar['requirement_list'] == [
        {'id': req} for req in expected_requirements
    ]


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize(
    'distance,time,expected_title',
    [
        (6710.527526140213, 2500, '45 мин, 6.8 км'),
        (10000, 3000, '50 мин, 10 км'),
    ],
)
async def test_build_long_distance(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        mocked_time,
        distance,
        time,
        expected_title,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response2.json')
    order_proc.order_proc['fields']['order']['calc'] = {
        'distance': distance,
        'time': time,
    }

    setcar_json = load_json('setcar_long_trip.json')
    setcar_push = load_json('setcar_push.json')
    setcar_json['date_last_change'] = utils.date_to_taximeter_str(
        mocked_time.now(),
    )
    setcar_push['date_last_change'] = utils.date_to_taximeter_str(
        mocked_time.now(),
    )
    request = PARAMS
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    setcar_json['ui']['acceptance_items'][-1]['title'] = expected_title
    setcar_push['ui'] = setcar_json['ui']
    utils.add_accents(setcar_push)
    assert response.status_code == 200, response.text
    resp_push, resp_setcar = (
        response.json()['setcar_push'],
        response.json()['setcar'],
    )
    utils.add_accents(setcar_json)

    assert resp_push == setcar_push
    assert resp_setcar == setcar_json


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize(
    'distance,time,expected_title',
    [
        (6710.527526140213, 2500, '45 мин, 6.8 км'),
        (10000, 3000, '50 мин, 10 км'),
    ],
)
async def test_long_distance_no_performer_index(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        mocked_time,
        distance,
        time,
        expected_title,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response2.json')
    order_proc.order_proc['fields']['order']['calc'] = {
        'distance': distance,
        'time': time,
    }
    order_proc.order_proc['fields']['candidates'][0][
        'driver_id'
    ] = 'xxx_driver1'

    setcar_json = load_json('setcar_long_trip.json')
    setcar_push = load_json('setcar_push.json')
    setcar_json['date_last_change'] = utils.date_to_taximeter_str(
        mocked_time.now(),
    )
    setcar_json['date_drive'] = utils.date_to_taximeter_str(mocked_time.now())
    setcar_push['date_last_change'] = utils.date_to_taximeter_str(
        mocked_time.now(),
    )
    setcar_push['date_drive'] = utils.date_to_taximeter_str(mocked_time.now())
    request = PARAMS
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    setcar_json['ui']['acceptance_items'][-1]['title'] = expected_title
    setcar_push['ui'] = setcar_json['ui']
    utils.add_accents(setcar_push)
    assert response.status_code == 200, response.text
    resp_push, resp_setcar = (
        response.json()['setcar_push'],
        response.json()['setcar'],
    )
    utils.add_accents(setcar_json)

    assert resp_push == setcar_push
    assert resp_setcar == setcar_json
