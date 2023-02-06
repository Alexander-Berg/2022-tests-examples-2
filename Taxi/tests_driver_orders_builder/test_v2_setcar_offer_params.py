import pytest


# pylint: disable=C0103
pytestmark = [
    pytest.mark.translations(
        taximeter_backend_driver_messages={
            'notification.key': {'ru': 'notify'},
        },
    ),
    pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        is_config=True,
        name='driver_orders_builder_settings',
        consumers=['driver-orders-builder/setcar'],
        clauses=[],
        default_value={'enable_requirements_rebuild': True},
    ),
]


@pytest.mark.config(
    DRIVER_ORDERS_BUILDER_ISR_OFFER_PARAMS_MOCK_ZONES={
        'tel_aviv': ['comfortplus', 'ultimate'],
    },
)
@pytest.mark.parametrize(
    'nearest_zone, tariff_class, expected_offer_params',
    [
        ['tel_aviv', 'comfortplus', {}],
        ['tel_aviv', 'econom', None],
        ['israel_ashkelon', 'comfortplus', None],
    ],
)
async def test_setcar_offer_params(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        nearest_zone,
        tariff_class,
        expected_offer_params,
        setcar_create_params,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response.json')
    order_proc.order_proc['fields']['order']['nz'] = nearest_zone
    order_proc.order_proc['fields']['candidates'][0][
        'tariff_class'
    ] = tariff_class

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200
    response_json = response.json()['setcar']
    assert response_json['ui'].get('offer_params') == expected_offer_params
