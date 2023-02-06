# pylint: disable=import-error
import base64
import datetime

import bson
import event_pb2 as mc_proto
import google.protobuf
import google.protobuf.json_format
import pytest

from testsuite.utils import callinfo


PROTO_JSON_FORMAT_KWARGS = {
    'including_default_value_fields': True,
    'preserving_proto_field_name': True,
    'float_precision': 4,
}
ORDER_CORE_ENDPOINT_PATH = (
    '/order-core/internal/processing/v1/order-proc/get-fields'
)
INVOICE_RETRIEVE_ENDPOINT = '/transactions/v2/invoice/retrieve'
PROTOSEQ_SYNC_WORD = (
    b'\x1F\xF7\xF7~\xBE\xA6^\2367\xA6\xF6.\xFE\xAEG\xA7'
    b'\xB7n\xBF\xAF\x16\x9E\2377\xF6W\367f\xA7\6\xAF\xF7'
)
MARK_CHECK_FIRST_OPERATION = pytest.mark.experiments3(
    filename='experiments/operation_check_mode_first.json',
)
MARK_CHECK_LAST_OPERATION = pytest.mark.experiments3(
    filename='experiments/operation_check_mode_last.json',
)


@pytest.mark.experiments3(filename='exp3_send_useractions_enabled.json')
@pytest.mark.parametrize('order_id', [pytest.param('order_1')])
async def test_mission_control(
        stq_runner, testpoint, load_yaml, load_json, mockserver, order_id,
):
    @mockserver.handler(ORDER_CORE_ENDPOINT_PATH)
    def _mock_order_core_response(request):
        order = load_json(f'{order_id}_order_core.json')
        return mockserver.make_response(
            response=bson.BSON.encode(order),
            status=200,
            content_type='application/bson',
        )

    @testpoint('logbroker_publish_b64')
    def publish(data):
        protoseq_bytes = base64.b64decode(data['data'])
        protobuf_bytes = protoseq_bytes[4:].split(PROTOSEQ_SYNC_WORD)[0]
        event: google.protobuf.message.Message = mc_proto.Event()
        event.ParseFromString(protobuf_bytes)
        proto_dict = google.protobuf.json_format.MessageToDict(
            event, **PROTO_JSON_FORMAT_KWARGS,
        )
        expected_dict = load_json(f'{order_id}_proto.json')
        assert expected_dict == proto_dict

    await stq_runner.mission_control_order_events_sending.call(
        task_id=order_id, args=[order_id], expect_fail=False,
    )
    await publish.wait_call()


@pytest.mark.experiments3(filename='exp3_send_useractions_disabled.json')
@pytest.mark.parametrize('order_id', [pytest.param('order_1')])
async def test_mission_control_send_useractions_disabled(
        stq_runner, testpoint, load_json, mockserver, order_id,
):
    @mockserver.handler(ORDER_CORE_ENDPOINT_PATH)
    def _mock_order_core_response(request):
        order = load_json(f'{order_id}_order_core.json')
        return mockserver.make_response(
            response=bson.BSON.encode(order),
            status=200,
            content_type='application/bson',
        )

    @testpoint('logbroker_publish_b64')
    def publish(data):
        pass

    await stq_runner.mission_control_order_events_sending.call(
        task_id=order_id, args=[order_id], expect_fail=False,
    )
    with pytest.raises(callinfo.CallQueueTimeoutError):
        await publish.wait_call(2)


@pytest.mark.xfail(reason='broken test, will be fixed in TAXIBACKEND-39851')
@pytest.mark.experiments3(filename='exp3_send_useractions_enabled.json')
@pytest.mark.experiments3(
    filename='experiment_mission_control_do_process_order.json',
)
@pytest.mark.parametrize(
    'mode',
    [
        pytest.param('first', marks=[MARK_CHECK_FIRST_OPERATION]),
        pytest.param('last', marks=[MARK_CHECK_LAST_OPERATION]),
    ],
)
async def test_operations_mode_first(
        mode,
        mock_order_core,
        mock_invoice_retrieve,
        mock_logbrocker_publish,
        load_json,
        stq_runner,
):
    invoice = load_json('card_order/invoice.json')
    invoice.update(load_json('card_order/operations_two_done.json'))
    mock_invoice_retrieve(invoice)
    mock_order_core(load_json('card_order/order_proc_fields.json'))
    lb_mock = mock_logbrocker_publish()

    async def expect_send():
        await lb_mock.wait_call()

    async def expect_skip():
        with pytest.raises(callinfo.CallQueueTimeoutError):
            await lb_mock.wait_call(1)

    await stq_runner.mission_control_transactions_callback.call(
        **load_json('card_order/stq_args_operation_1.json'), expect_fail=False,
    )
    if mode == 'first':
        await expect_send()
    elif mode == 'last':
        await expect_skip()

    await stq_runner.mission_control_transactions_callback.call(
        **load_json('card_order/stq_args_operation_2.json'), expect_fail=False,
    )
    if mode == 'first':
        await expect_skip()
    elif mode == 'last':
        await expect_send()


@pytest.mark.experiments3(filename='exp3_send_useractions_enabled.json')
async def test_refund(stq_runner, load_json, mockserver, testpoint, stq):
    @mockserver.handler(INVOICE_RETRIEVE_ENDPOINT)
    def _mock_invoice_retrieve(request):
        return mockserver.make_response(
            json=load_json(f'transactions_response_1.json'), status=200,
        )

    @testpoint('logbroker_publish_b64')
    def publish(data):
        protoseq_bytes = base64.b64decode(data['data'])
        protobuf_bytes = protoseq_bytes[4:].split(PROTOSEQ_SYNC_WORD)[0]
        event: google.protobuf.message.Message = mc_proto.Event()
        event.ParseFromString(protobuf_bytes)
        proto_dict = google.protobuf.json_format.MessageToDict(
            event, **PROTO_JSON_FORMAT_KWARGS,
        )
        expected_dict = load_json(f'refund_1_proto.json')
        assert expected_dict == proto_dict

    task = load_json('transactions_callback_1.json')
    await stq_runner.mission_control_transactions_callback.call(
        task_id=task['task_id'], args=task['args'], expect_fail=False,
    )
    await publish.wait_call()


@pytest.mark.now('2021-11-08 00:00:00.000000')
@pytest.mark.experiments3(filename='exp3_send_useractions_enabled.json')
async def test_transactions_callback_cashback_rescheduling(
        stq_runner, load_json, mockserver, stq,
):
    expected_eta = datetime.datetime.fromisoformat(
        '2021-11-08 00:00:30.000000',
    )

    @mockserver.handler(INVOICE_RETRIEVE_ENDPOINT)
    def _mock_invoice_retrieve(request):
        return mockserver.make_response(
            json=load_json(f'transactions_response_cashback_race.json'),
            status=200,
        )

    task = load_json('transactions_callback_1.json')
    await stq_runner.mission_control_transactions_callback.call(
        task_id=task['task_id'], args=task['args'], expect_fail=False,
    )
    next_call = stq.mission_control_transactions_callback.next_call()
    diff = next_call['eta'] - expected_eta
    assert abs(diff.total_seconds()) < 1


@pytest.mark.now('2021-11-08 00:02:00.000000')
@pytest.mark.experiments3(filename='exp3_send_useractions_enabled.json')
@pytest.mark.experiments3(
    filename='experiment_mission_control_do_process_order.json',
)
@pytest.mark.parametrize(
    'expect_reschedule', [pytest.param(True), pytest.param(False)],
)
async def test_payment_event(
        stq_runner, load_json, mockserver, testpoint, stq, expect_reschedule,
):
    order_id = 'order_2'

    @mockserver.handler(ORDER_CORE_ENDPOINT_PATH)
    def _mock_order_core_response(request):
        order = load_json(f'{order_id}_order_core.json')
        if expect_reschedule:
            order['document']['status'] = 'assigned'

        return mockserver.make_response(
            response=bson.BSON.encode(order),
            status=200,
            content_type='application/bson',
        )

    @mockserver.handler(INVOICE_RETRIEVE_ENDPOINT)
    def _mock_invoice_retrieve(request):
        return mockserver.make_response(
            json=load_json(f'{order_id}_invoice.json'), status=200,
        )

    @testpoint('logbroker_publish_b64')
    def publish(data):
        protoseq_bytes = base64.b64decode(data['data'])
        protobuf_bytes = protoseq_bytes[4:].split(PROTOSEQ_SYNC_WORD)[0]
        event: google.protobuf.message.Message = mc_proto.Event()
        event.ParseFromString(protobuf_bytes)
        proto_dict = google.protobuf.json_format.MessageToDict(
            event, **PROTO_JSON_FORMAT_KWARGS,
        )
        expected_dict = load_json(f'{order_id}_proto.json')
        assert expected_dict == proto_dict

    task = load_json(f'{order_id}_transactions_callback.json')
    await stq_runner.mission_control_transactions_callback.call(
        task_id=task['task_id'], args=task['args'], expect_fail=False,
    )
    if expect_reschedule:
        # Rescheduled to expected ride finish time
        # order.created + order.route.time
        expected_eta = datetime.datetime.fromisoformat(
            '2021-11-08 00:19:17.000000',
        )
        next_call = stq.mission_control_transactions_callback.next_call()
        diff = next_call['eta'] - expected_eta
        assert abs(diff.total_seconds()) < 1

    else:
        await publish.wait_call()


@pytest.mark.experiments3(filename='exp3_send_useractions_enabled.json')
@pytest.mark.experiments3(
    filename='experiment_mission_control_do_process_order.json',
)
@pytest.mark.parametrize(
    'expect_reschedule, expected_eta',
    [
        pytest.param(
            True,
            '2021-11-08 00:19:17.000000',
            id='route_time',
            marks=(pytest.mark.now('2021-11-08 00:02:00.000000'),),
        ),
        pytest.param(
            True,
            '2021-11-08 00:21:17.000000',
            id='expected_finish_in_past',
            marks=(pytest.mark.now('2021-11-08 00:20:17.000000'),),
        ),
    ],
)
async def test_rescheduling(
        mock_order_core,
        mock_invoice_retrieve,
        load_json,
        stq_runner,
        stq,
        expect_reschedule,
        expected_eta,
):
    order_proc_fields = load_json('card_order/order_proc_fields.json')
    order_proc_fields['status'] = 'assigned'
    mock_order_core(order_proc_fields)
    mock_invoice_retrieve(load_json('card_order/invoice.json'))

    task = load_json(f'card_order/stq_args_operation_1.json')
    await stq_runner.mission_control_transactions_callback.call(
        task_id=task['task_id'], args=task['args'], expect_fail=False,
    )

    if expect_reschedule:
        next_call = stq.mission_control_transactions_callback.next_call()
        diff = next_call['eta'] - datetime.datetime.fromisoformat(expected_eta)
        assert abs(diff.total_seconds()) < 1


@pytest.mark.now('2021-11-08 00:02:00.000000')
@pytest.mark.experiments3(filename='exp3_send_useractions_enabled.json')
@pytest.mark.experiments3(
    filename='experiment_mission_control_do_process_order.json',
)
async def test_invalid_enums(stq_runner, testpoint, load_json, mockserver):
    order_id = 'invalid_enums'

    @mockserver.handler(ORDER_CORE_ENDPOINT_PATH)
    def _mock_order_core_response(request):
        order = load_json(f'{order_id}_order_core.json')
        return mockserver.make_response(
            response=bson.BSON.encode(order),
            status=200,
            content_type='application/bson',
        )

    @mockserver.handler(INVOICE_RETRIEVE_ENDPOINT)
    def _mock_invoice_retrieve(request):
        return mockserver.make_response(
            json=load_json(f'{order_id}_invoice.json'), status=200,
        )

    @testpoint('logbroker_publish_b64')
    def publish(data):
        protoseq_bytes = base64.b64decode(data['data'])
        protobuf_bytes = protoseq_bytes[4:].split(PROTOSEQ_SYNC_WORD)[0]
        event: google.protobuf.message.Message = mc_proto.Event()
        event.ParseFromString(protobuf_bytes)
        proto_dict = google.protobuf.json_format.MessageToDict(
            event, **PROTO_JSON_FORMAT_KWARGS,
        )
        assert proto_dict == load_json(f'{order_id}_proto.json')

    await stq_runner.mission_control_order_events_sending.call(
        task_id=order_id, args=[order_id], expect_fail=False,
    )
    await publish.wait_call()

    await stq_runner.mission_control_transactions_callback.call(
        task_id='invoice/version/1',
        args=['test', 'invoice/version/1', 'done', 'operation_finish', []],
    )
    await publish.wait_call()


@pytest.mark.now('2022-03-08 00:02:00.000000')
@pytest.mark.experiments3(filename='exp3_send_useractions_enabled.json')
@pytest.mark.experiments3(
    filename='experiment_mission_control_do_process_order.json',
)
async def test_old_orders(stq_runner, testpoint, load_json, mockserver):
    order_id = 'invalid_enums'

    @mockserver.handler(ORDER_CORE_ENDPOINT_PATH)
    def _mock_order_core_response(request):
        order = load_json(f'{order_id}_order_core.json')
        return mockserver.make_response(
            response=bson.BSON.encode(order),
            status=200,
            content_type='application/bson',
        )

    @testpoint('logbroker_publish_b64')
    def publish(data):
        # Shouldn't be called
        assert False

    await stq_runner.mission_control_transactions_callback.call(
        task_id='invoice/version/1',
        args=['test', 'invoice/version/1', 'done', 'operation_finish', []],
    )
    assert not publish.has_calls
