import json

import pytest


@pytest.fixture(name='mock_setcar_update_lite', autouse=True)
def _mock_setcar_update_lite(mockserver):
    @mockserver.json_handler('/driver-orders-builder/v1/setcar/update-lite')
    def _handler(request):
        return {}

    return _handler


@pytest.fixture(name='mock_driver_push')
def _mock_driver_push(mockserver):
    @mockserver.json_handler('/client-notify/v2/push')
    def v2_push(request):
        return mockserver.make_response(
            json.dumps({'notification_id': 'somemagicid'}), status=200,
        )

    return v2_push


async def test_happy_path(
        stq_runner,
        happy_path_state_performer_found,
        read_waybill_info,
        mock_setcar_update_lite,
        mock_driver_push,
        mock_segments_bulk_info_cut,
):
    waybill = await read_waybill_info('waybill_fb_3')
    cargo_order_id = waybill['diagnostics']['order_id']

    await stq_runner.cargo_update_setcar_state_version.call(
        task_id='test',
        kwargs={
            'cargo_order_id': cargo_order_id,
            'driver_profile_id': 'driver_id_1',
            'park_id': 'park_id_1',
            'send_taximeter_push': True,
        },
    )

    # Check request to DOB service
    assert mock_setcar_update_lite.times_called == 1
    update_setcar_request = mock_setcar_update_lite.next_call()['request']
    assert update_setcar_request.json == {
        'changes': [
            {
                'allow_replace': True,
                'field': 'cargo.state_version',
                'value': 'v1_w_1_s_0',
            },
        ],
    }
    assert dict(update_setcar_request.query) == {
        'order_id': '1234',
        'park_id': 'park_id_1',
        'driver_profile_id': 'driver_id_1',
    }

    # Check request to communications service
    assert mock_driver_push.times_called == 1
    driver_push_request = mock_driver_push.next_call()['request']
    assert driver_push_request.json == {
        'client_id': 'park_id_1-driver_id_1',
        'intent': 'ForcePollingOrder',
        'service': 'taximeter',
        'data': {'code': 1600},
    }


async def test_driver_was_changed(
        stq_runner,
        happy_path_state_performer_found,
        read_waybill_info,
        mock_setcar_update_lite,
        mock_driver_push,
        mock_segments_bulk_info_cut,
):
    """
    This case is unreal now, because we will change taximeter_state_version
    only when driver can't cancel order
    """
    waybill = await read_waybill_info('waybill_fb_3')
    cargo_order_id = waybill['diagnostics']['order_id']

    await stq_runner.cargo_update_setcar_state_version.call(
        task_id='test',
        kwargs={
            'cargo_order_id': cargo_order_id,
            'driver_profile_id': 'new_driver_id',
            'park_id': 'new_park_id',
            'send_taximeter_push': True,
        },
    )

    # Check no actions
    assert mock_setcar_update_lite.times_called == 0
    assert mock_driver_push.times_called == 0


async def test_setcar_not_found(
        stq_runner,
        happy_path_state_performer_found,
        read_waybill_info,
        mock_driver_push,
        mockserver,
        mock_segments_bulk_info_cut,
):
    waybill = await read_waybill_info('waybill_fb_3')
    cargo_order_id = waybill['diagnostics']['order_id']

    # Return 404, setcar not found (order complete)
    @mockserver.json_handler('/driver-orders-builder/v1/setcar/update-lite')
    def mock_setcar_update(request):
        return mockserver.make_response(
            status=404, json={'code': '', 'message': ''},
        )

    await stq_runner.cargo_update_setcar_state_version.call(
        task_id='test',
        kwargs={
            'cargo_order_id': cargo_order_id,
            'driver_profile_id': 'driver_id_1',
            'park_id': 'park_id_1',
            'send_taximeter_push': True,
        },
    )

    assert mock_setcar_update.times_called == 1
    assert mock_driver_push.times_called == 0


async def test_setcar_500(
        stq_runner,
        happy_path_state_performer_found,
        read_waybill_info,
        mock_driver_push,
        mockserver,
        mock_segments_bulk_info_cut,
):
    waybill = await read_waybill_info('waybill_fb_3')
    cargo_order_id = waybill['diagnostics']['order_id']

    # Return 500
    @mockserver.json_handler('/driver-orders-builder/v1/setcar/update-lite')
    def mock_setcar_update(request):
        return mockserver.make_response(
            status=500, json={'code': '', 'message': ''},
        )

    await stq_runner.cargo_update_setcar_state_version.call(
        task_id='test',
        kwargs={
            'cargo_order_id': cargo_order_id,
            'driver_profile_id': 'driver_id_1',
            'park_id': 'park_id_1',
            'send_taximeter_push': True,
        },
        expect_fail=True,
    )

    # 3 because of _CLIENT_QOS config
    assert mock_setcar_update.times_called == 3
    assert mock_driver_push.times_called == 0


async def test_do_not_send_push(
        stq_runner,
        happy_path_state_performer_found,
        read_waybill_info,
        mock_driver_push,
        mock_segments_bulk_info_cut,
):
    waybill = await read_waybill_info('waybill_fb_3')
    cargo_order_id = waybill['diagnostics']['order_id']

    await stq_runner.cargo_update_setcar_state_version.call(
        task_id='test',
        kwargs={
            'cargo_order_id': cargo_order_id,
            'driver_profile_id': 'driver_id_1',
            'park_id': 'park_id_1',
            'send_taximeter_push': False,
        },
    )
    assert mock_driver_push.times_called == 0


async def test_driver_message_push(
        stq_runner,
        happy_path_state_performer_found,
        read_waybill_info,
        mock_setcar_update_lite,
        mock_driver_push,
        mock_segments_bulk_info_cut,
):
    waybill = await read_waybill_info('waybill_fb_3')
    cargo_order_id = waybill['diagnostics']['order_id']

    await stq_runner.cargo_update_setcar_state_version.call(
        task_id='test',
        kwargs={
            'cargo_order_id': cargo_order_id,
            'driver_profile_id': 'driver_id_1',
            'park_id': 'park_id_1',
            'send_taximeter_push': True,
            'driver_notification_tanker_key': 'test_tanker_ket',
            'driver_notification_tanker_keyset': 'test_tanker_keyset',
        },
    )

    assert mock_driver_push.times_called == 2
    _ = mock_driver_push.next_call()

    message_push_request = mock_driver_push.next_call()['request']
    assert message_push_request.json == {
        'client_id': 'park_id_1-driver_id_1',
        'intent': 'MessageNew',
        'service': 'taximeter',
        'notification': {
            'text': {'key': 'test_tanker_ket', 'keyset': 'test_tanker_keyset'},
        },
        'data': {
            'id': (
                'cargo_alive_dragon_update_'
                'park_id_1_driver_id_1_test_tanker_ket'
            ),
        },
    }


async def test_notification_with_tanker_params(
        stq_runner,
        happy_path_state_performer_found,
        read_waybill_info,
        mock_setcar_update_lite,
        mock_driver_push,
        mock_segments_bulk_info_cut,
):
    waybill = await read_waybill_info('waybill_fb_3')
    cargo_order_id = waybill['diagnostics']['order_id']

    await stq_runner.cargo_update_setcar_state_version.call(
        task_id='test',
        kwargs={
            'cargo_order_id': cargo_order_id,
            'driver_profile_id': 'driver_id_1',
            'park_id': 'park_id_1',
            'send_taximeter_push': True,
            'driver_notification_tanker_key': 'test_tanker_ket',
            'driver_notification_tanker_keyset': 'test_tanker_keyset',
            'driver_notification_params': {'key_1': 'value_1'},
        },
    )

    _ = mock_driver_push.next_call()
    message_push_request = mock_driver_push.next_call()['request']
    assert message_push_request.json == {
        'client_id': 'park_id_1-driver_id_1',
        'intent': 'MessageNew',
        'service': 'taximeter',
        'notification': {
            'text': {
                'key': 'test_tanker_ket',
                'keyset': 'test_tanker_keyset',
                'params': {'key_1': 'value_1'},
            },
        },
        'data': {
            'id': (
                'cargo_alive_dragon_update_'
                'park_id_1_driver_id_1_test_tanker_ket'
            ),
        },
    }
