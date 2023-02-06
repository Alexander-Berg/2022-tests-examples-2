import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.parametrize('enable_processing', [True, False])
async def test_clid(
        taxi_driver_orders_builder,
        experiments3,
        parks,
        enable_processing,
        setcar_create_params,
):
    parks.set_aggregators_id({'park1': 'aggregator1'})
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_processings_settings',
        consumers=['driver-orders-builder/setcar'],
        clauses=[],
        default_value={
            '__default__': True,
            'park_clid_processing': enable_processing,
        },
    )
    await taxi_driver_orders_builder.invalidate_caches()

    response = await taxi_driver_orders_builder.post(**setcar_create_params)

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert ('clid' in response_json) == enable_processing
    if enable_processing:
        assert response_json['clid'] == 'aggregator1_clid'
