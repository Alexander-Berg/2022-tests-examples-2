import pytest

from . import utils


@utils.eats_eta_settings_config3()
async def test_stq_update_estimations_retries_number_exceeded(
        experiments3,
        mockserver,
        stq_runner,
        redis_store,
        make_order,
        db_insert_order,
        db_select_orders,
):
    max_retries = 3
    experiments3.add_experiment3_from_marker(
        utils.eats_eta_settings_config3(
            stq_update_estimations_retries=max_retries,
        ),
        None,
    )
    order_nr = 'order-nr'
    order = make_order(order_nr=order_nr)
    db_insert_order(order)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(_):
        return {}

    await stq_runner.eats_eta_update_estimations.call(
        task_id=order_nr,
        kwargs={'order_nr': order_nr},
        exec_tries=max_retries,
    )

    assert mock_stq_reschedule.times_called == 0

    assert db_select_orders(order_nr=order_nr) == [order]
    assert not redis_store.keys()


@pytest.mark.update_mode('force_update')
@pytest.mark.redis_testcase(True)
@pytest.mark.parametrize('send_to_logbroker', [False, True])
async def test_stq_update_estimations(
        testpoint,
        experiments3,
        stq_runner,
        cargo,
        pickers,
        eta_testcase,
        check_redis_value,
        db_select_orders,
        send_to_logbroker,
):
    experiments3.add_experiment3_from_marker(
        utils.eats_eta_send_to_logbroker_config3(send_to_logbroker), None,
    )

    @testpoint('eats-eta::message-pushed')
    def after_push(_):
        pass

    cargo_claims_times_called = 0
    picker_orders_times_called = 0
    for i, testcase_order in enumerate(eta_testcase['orders']):
        order = testcase_order['order']
        order_nr = order['order_nr']
        expected_estimations = testcase_order['expected_estimations']

        await stq_runner.eats_eta_update_estimations.call(
            task_id=order_nr, kwargs={'order_nr': order_nr},
        )
        for key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], key, order[key])
        for key, data in expected_estimations.items():
            check_redis_value(order['order_nr'], key, data['value'])

        if 'order_update' in testcase_order:
            order.update(testcase_order['order_update'])
            assert db_select_orders(order_nr=order['order_nr']) == [order]
        metrics = testcase_order.get('metrics', {})
        if 'update_cargo_info' in metrics:
            cargo_claims_times_called += metrics['update_cargo_info']
        else:
            cargo_claims_times_called = (
                cargo.mock_cargo_claims_info.times_called
            )
        if 'update_retail_info' in metrics:
            picker_orders_times_called += metrics['update_retail_info']
        else:
            picker_orders_times_called = (
                pickers.mock_picker_orders_get_order.times_called
            )
        assert (
            cargo.mock_cargo_claims_info.times_called
            == cargo_claims_times_called
        )
        assert (
            pickers.mock_picker_orders_get_order.times_called
            == picker_orders_times_called
        )
        assert after_push.times_called == int(send_to_logbroker) * (i + 1)
