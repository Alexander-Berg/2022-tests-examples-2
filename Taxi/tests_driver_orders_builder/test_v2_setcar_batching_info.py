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
        default_value={
            'enable_requirements_rebuild': True,
            'enable_candidate_meta_request': True,
        },
    ),
]


@pytest.mark.parametrize(
    'candidate_meta_response, should_be_enabled',
    [
        [{'combo': {}}, False],
        [{'combo': {'active': False}}, False],
        [{'combo': {'active': True, 'route': []}}, False],
        [{'combo': {'active': True}}, True],
    ],
)
async def test_setcar_batching_info(
        taxi_driver_orders_builder,
        load_json,
        redis_store,
        mockserver,
        experiments3,
        candidate_meta_response,
        should_be_enabled,
        setcar_create_params,
        order_proc,
):
    OTHER_ORDER_ID = '111122223333aaaaffff'
    redis_store.sadd(
        'Order:SetCar:Driver:Reserv:Itemspark1:driver1', OTHER_ORDER_ID,
    )

    order_proc.set_file(load_json, 'order_core_response.json')

    @mockserver.json_handler('/candidate-meta/v1/candidate/meta/get')
    def _mock_candidate_meta(request):
        return {'metadata': candidate_meta_response}

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200
    response_json = response.json()['setcar']

    if should_be_enabled:
        assert response_json['batching_info'] == {
            'delayed_order_id': OTHER_ORDER_ID,
        }
    else:
        assert 'batching_info' not in response_json
