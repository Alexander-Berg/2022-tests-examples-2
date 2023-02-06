import pytest


@pytest.mark.now('2020-07-07T00:00:00Z')
@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'pipelines': [{'period': 15, 'pipeline': 'test_pipeline'}]},
    is_config=True,
)
async def test_basic_resource(
        taxi_grocery_surge,
        admin_pipeline,
        stq,
        stq_runner,
        mocked_time,
        testpoint,
):
    depot_id = '1'
    out_data = {'out_key': 'out_value'}

    @testpoint('parsed_data_processing')
    def _parsed_data_processing(val):
        assert val['depot_id'] == depot_id
        assert val['data'] == {'key': 'value'}
        return out_data

    @testpoint('wrap_serialized_result')
    def _wrap_serialized_result(val):
        assert val['depot_id'] == depot_id
        assert val['data'] == out_data

    task_id = 'task_id'
    await stq_runner.grocery_surge_calculate_pipeline.call(
        task_id=task_id,
        kwargs={'pipeline': 'test_pipeline', 'depot_id': depot_id},
    )


# проверка, что ресурс depot_state успешно создается с данными из кэша
@pytest.mark.now('2020-07-07T00:00:00Z')
@pytest.mark.experiments3(
    name='grocery_surge_js_pipeline_schedule',
    consumers=['grocery_surge/js_pipeline_scheduler'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'pipelines': [{'period': 15, 'pipeline': 'test_pipeline'}]},
    is_config=True,
)
@pytest.mark.experiments3(
    name='grocery_surge_use_delivery_type',
    consumers=['grocery_surge/surge'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.pipeline('depot_state')
async def test_resource_depot_state(
        taxi_grocery_surge,
        admin_pipeline,
        stq,
        stq_runner,
        mocked_time,
        testpoint,
        mockserver,
):
    depot_id = '1'

    order = {
        'order_id': '6e32572a76624cec812c733b1fcb3cff-grocery',
        'order_status': 'dispatching',
        'cart_id': '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9',
        'delivery_type': 'pickup',
        'courier_dbid_uuid': 'dbid0_uuid778',
        'assembly_started': '2021-10-26T15:01:19+00:00',
        'assembly_finished': '2021-10-26T15:05:19+00:00',
    }

    @mockserver.json_handler(
        '/grocery-dispatch-tracking/internal/'
        'grocery-dispatch-tracking/v1/depot-state',
    )
    def _depot_state(request):
        assert request.json['legacy_depot_id'] == depot_id
        return {'orders': [order], 'performers': []}

    @testpoint('wrap_serialized_result')
    def _wrap_serialized_result(val):
        val_order = val['orders'][0]
        assert val_order['order_id'] == order['order_id']
        assert val_order['dispatch_status'] == order['order_status']
        assert val_order['cart_id'] == order['cart_id']
        assert val_order['delivery_type'] == order['delivery_type']
        assert val_order['performer_id'] == order['courier_dbid_uuid']
        assert val_order['assembly_started'] == order['assembly_started']
        assert val_order['assembly_finished'] == order['assembly_finished']
        val_performer = val['performers'][0]
        assert val_performer['performer_id'] == order['courier_dbid_uuid']

    task_id = 'task_id'
    await stq_runner.grocery_surge_calculate_pipeline.call(
        task_id=task_id,
        kwargs={'pipeline': 'test_pipeline', 'depot_id': depot_id},
    )
