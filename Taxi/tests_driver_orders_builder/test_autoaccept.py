import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.parametrize('config', [{'autoaccept': 42}, {'autoaccept': 0}, {}])
async def test_autoaccept(
        taxi_driver_orders_builder, config, setcar_create_params,
):

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text()
    if 'auto_confirmation' in config:
        assert (
            response.json()['setcar']['taximeter_settings'][
                'auto_confirmation'
            ]
            == config['auto_confirmation']
        )
        assert (
            response.json()['setcar']['auto_confirmation']['settings']
            == config['auto_confirmation']
        )
    elif 'taximeter_settings' in response.json():
        assert 'auto_confirmation' not in response.json()['taximeter_settings']
        assert 'settings' not in response.json()['auto_confirmation']


@pytest.mark.parametrize(
    'candidate_override, auto_confirmation',
    [
        (
            {'autoaccept': {'enabled': True}},
            {'flow': 'autoaccept', 'enabled': True, 'set_status': 2},
        ),
        ({}, None),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
async def test_autoaccept_autoaccept(
        taxi_driver_orders_builder,
        mockserver,
        load_json,
        candidate_override,
        auto_confirmation,
        setcar_create_params,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response.json')
    order_proc.order_proc['fields']['candidates'][0].update(candidate_override)

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text()
    assert (
        response.json()['setcar']['taximeter_settings'].get(
            'auto_confirmation',
        )
        == auto_confirmation
    )
    if auto_confirmation:
        assert (
            response.json()['setcar']['auto_confirmation'].get('settings')
            == auto_confirmation
        )
