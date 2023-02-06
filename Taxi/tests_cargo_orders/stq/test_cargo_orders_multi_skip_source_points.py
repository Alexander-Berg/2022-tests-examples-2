import pytest


DEFAULT_CARGO_REF_ID = 'order/9db1622e-582d-4091-b6fc-4cb2ffdc12c0'
TASK_ID = 'task_id1'
PARK_ID = 'park_id1'
DRIVER_ID = 'driver_id1'
LAST_KNOWN_STATUS = 'new'
REASONS = ['some_reason_id']
COMMENT = 'Some comment'
PROCESSING_EVENT_KIND = 'multi-skip-source-points-end'


STQ_SETTINGS_CONFIG = pytest.mark.config(
    CARGO_ORDERS_TAXIMETER_ASYNC_OPERATIONS_STQ_SETTINGS={
        '__default__': {'max_attempts_count': 3},
    },
)

MULTI_SKIP_SETTINGS = pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_multi_skip_source_points_action_settings',
    consumers=['cargo-claims/driver'],
    clauses=[],
    default_value={'is_enabled': True},
)


def build_stq_kwargs(claim_point_id: int, cargo_ref_id=DEFAULT_CARGO_REF_ID):
    return {
        'accept_language': 'en',
        'remote_ip': '12.34.56.78',
        'taximeter_app': {
            'version': '9.40',
            'version_type': '',
            'platform': 'android',
        },
        'cargo_ref_id': cargo_ref_id,
        'claim_point_id': claim_point_id,
        'last_known_status': LAST_KNOWN_STATUS,
        'reasons': REASONS,
        'comment': COMMENT,
    }


TRANSLATIONS = {
    'async_operations.multi_skip_source_points.failure': {
        'en': 'Failed to skip the point',
    },
    'async_operations.multi_skip_source_points.success': {
        'en': 'The point is skipped',
    },
}


@pytest.fixture(name='mock_processing_create_event')
def _mock_processing_create_event(mockserver):
    @mockserver.json_handler(
        '/processing/v1/cargo/taximeter_async_operations/create-event',
    )
    def _mock(request):
        assert request.headers['X-Idempotency-Token'] == TASK_ID
        assert request.args['item_id'] == context.item_id
        assert request.json == context.expected_request
        return {'event_id': '0987654321'}

    class Context:
        def __init__(self):
            self.item_id = None
            self.expected_request = None
            self.mock = _mock

    context = Context()
    return context


def build_create_event_request():
    return {
        'kind': PROCESSING_EVENT_KIND,
        'accept_language': 'en',
        'remote_ip': '12.34.56.78',
        'taximeter_app': {
            'platform': 'android',
            'version': '9.40',
            'version_type': '',
        },
    }


@pytest.fixture(name='mock_client_notify_v2_push')
def _mock_client_notify_v2_push(mockserver):
    @mockserver.json_handler('/client-notify/v2/push')
    def _mock(request):
        assert request.headers['X-Idempotency-Token'] == TASK_ID
        assert request.json == context.expected_request
        return {'notification_id': '0987654321'}

    class Context:
        def __init__(self):
            self.expected_request = None
            self.mock = _mock

    context = Context()
    return context


def build_client_notify_request(task_id: str, text: str):
    return {
        'intent': 'MessageNew',
        'service': 'taximeter',
        'client_id': f'{PARK_ID}-{DRIVER_ID}',
        'notification': {'text': text},
        'data': {'id': task_id, 'flags': ['high_priority']},
    }


def build_cargo_dispatch_request(claim_point_id: int):
    return {
        'last_known_status': LAST_KNOWN_STATUS,
        'point_id': claim_point_id,
        'reasons': REASONS,
        'comment': COMMENT,
        'performer_info': {
            'park_id': PARK_ID,
            'driver_id': DRIVER_ID,
            'tariff_class': 'cargo',
            'phone_pd_id': 'phone_pd_id',
        },
        'async_timer_calculation_supported': False,
    }


@STQ_SETTINGS_CONFIG
@MULTI_SKIP_SETTINGS
@pytest.mark.translations(cargo=TRANSLATIONS)
async def test_happy_path(
        mockserver,
        mock_driver_tags_v1_match_profile,
        mock_processing_create_event,
        mock_client_notify_v2_push,
        mock_dispatch_return,
        mock_waybill_info,
        my_batch_waybill_info,
        set_current_point,
        stq_runner,
        stq,
        claim_point_id=1,
):
    set_current_point(my_batch_waybill_info, idx=0)

    mock_dispatch_return.expected_request = build_cargo_dispatch_request(
        claim_point_id,
    )

    mock_processing_create_event.item_id = DEFAULT_CARGO_REF_ID
    mock_processing_create_event.expected_request = (
        build_create_event_request()
    )

    mock_client_notify_v2_push.expected_request = build_client_notify_request(
        TASK_ID, 'The point is skipped',
    )

    await stq_runner.cargo_orders_multi_skip_source_points.call(
        task_id=TASK_ID, kwargs=build_stq_kwargs(claim_point_id),
    )

    assert mock_dispatch_return.handler.times_called == 1
    assert mock_processing_create_event.mock.times_called == 1
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )
    assert mock_client_notify_v2_push.mock.times_called == 1


async def test_bad_cargo_ref_id(stq_runner, claim_point_id=1):
    await stq_runner.cargo_orders_multi_skip_source_points.call(
        task_id=TASK_ID,
        kwargs=build_stq_kwargs(claim_point_id, cargo_ref_id='12345'),
        expect_fail=True,
    )


async def test_no_order(
        mockserver,
        mock_processing_create_event,
        mock_client_notify_v2_push,
        stq_runner,
        stq,
        cargo_ref_id='order/12345678-1234-1234-1234-123456789012',
        claim_point_id=1,
):
    mock_processing_create_event.item_id = cargo_ref_id
    mock_processing_create_event.expected_request = (
        build_create_event_request()
    )

    await stq_runner.cargo_orders_multi_skip_source_points.call(
        task_id=TASK_ID,
        kwargs=build_stq_kwargs(claim_point_id, cargo_ref_id=cargo_ref_id),
    )

    assert mock_processing_create_event.mock.times_called == 1
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 0
    )
    assert mock_client_notify_v2_push.mock.times_called == 0


async def test_no_performer(
        mockserver,
        mock_processing_create_event,
        mock_client_notify_v2_push,
        stq_runner,
        stq,
        cargo_ref_id='order/7771622e-4091-582d-b6fc-4cb2ffdc12c0',
        claim_point_id=1,
):
    mock_processing_create_event.item_id = cargo_ref_id
    mock_processing_create_event.expected_request = (
        build_create_event_request()
    )

    await stq_runner.cargo_orders_multi_skip_source_points.call(
        task_id=TASK_ID,
        kwargs=build_stq_kwargs(claim_point_id, cargo_ref_id=cargo_ref_id),
    )

    assert mock_processing_create_event.mock.times_called == 1
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 0
    )
    assert mock_client_notify_v2_push.mock.times_called == 0


@pytest.mark.translations(cargo=TRANSLATIONS)
async def test_action_validation(
        mockserver,
        mock_driver_tags_v1_match_profile,
        mock_processing_create_event,
        mock_client_notify_v2_push,
        my_waybill_info,  # not a batch
        mock_waybill_info,
        set_current_point,
        stq_runner,
        stq,
        claim_point_id=642499,
):
    set_current_point(my_waybill_info, idx=0)

    mock_processing_create_event.item_id = DEFAULT_CARGO_REF_ID
    mock_processing_create_event.expected_request = (
        build_create_event_request()
    )

    mock_client_notify_v2_push.expected_request = build_client_notify_request(
        TASK_ID, 'Failed to skip the point',
    )

    await stq_runner.cargo_orders_multi_skip_source_points.call(
        task_id=TASK_ID, kwargs=build_stq_kwargs(claim_point_id),
    )

    assert mock_processing_create_event.mock.times_called == 1
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )
    assert mock_client_notify_v2_push.mock.times_called == 1


@pytest.fixture(name='mock_flappy_waybill_return')
def _mock_flappy_waybill_return(mockserver, my_triple_batch_waybill_info):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/return')
    def _mock(request):
        context.call_count += 1
        if context.call_count == context.failed_call_number:
            return mockserver.make_response(
                status=500,
                json={'code': '500', 'message': 'Internal Server Error'},
            )
        return {
            'result': 'confirmed',
            'new_status': LAST_KNOWN_STATUS,
            'new_route': [],
            'waybill_info': my_triple_batch_waybill_info,
        }

    class Context:
        def __init__(self):
            self.call_count = 0
            self.failed_call_number = 2
            self.mock = _mock

    context = Context()
    return context


@STQ_SETTINGS_CONFIG
@pytest.mark.config(
    CARGO_DISPATCH_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 200},
    },
)
@MULTI_SKIP_SETTINGS
@pytest.mark.translations(cargo=TRANSLATIONS)
async def test_retry_skipping_second_point_in_group(
        mockserver,
        mock_driver_tags_v1_match_profile,
        mock_processing_create_event,
        mock_client_notify_v2_push,
        mock_flappy_waybill_return,
        mock_waybill_info,
        my_triple_batch_waybill_info,
        set_current_point,
        set_segments_place_id,
        set_segments_points_skipped,
        stq_runner,
        stq,
        claim_point_id=1,
):
    set_current_point(my_triple_batch_waybill_info, idx=0)
    set_segments_place_id(
        my_triple_batch_waybill_info, segment_ids=[0, 1], place_id=1234,
    )

    await stq_runner.cargo_orders_multi_skip_source_points.call(
        task_id=TASK_ID,
        kwargs=build_stq_kwargs(claim_point_id),
        expect_fail=True,
    )

    assert mock_flappy_waybill_return.mock.times_called == 2
    assert mock_processing_create_event.mock.times_called == 0
    assert mock_client_notify_v2_push.mock.times_called == 0

    mock_processing_create_event.item_id = DEFAULT_CARGO_REF_ID
    mock_processing_create_event.expected_request = (
        build_create_event_request()
    )

    mock_client_notify_v2_push.expected_request = build_client_notify_request(
        TASK_ID, 'The point is skipped',
    )

    set_segments_points_skipped(
        my_triple_batch_waybill_info, segment_ids=['seg_1'],
    )

    await stq_runner.cargo_orders_multi_skip_source_points.call(
        task_id=TASK_ID, kwargs=build_stq_kwargs(claim_point_id),
    )

    assert mock_flappy_waybill_return.mock.times_called == 3
    assert mock_processing_create_event.mock.times_called == 1
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )
    assert mock_client_notify_v2_push.mock.times_called == 1


@STQ_SETTINGS_CONFIG
@MULTI_SKIP_SETTINGS
@pytest.mark.translations(cargo=TRANSLATIONS)
async def test_retry_with_already_skipped_points(
        mockserver,
        mock_driver_tags_v1_match_profile,
        mock_processing_create_event,
        mock_client_notify_v2_push,
        mock_dispatch_return,
        mock_waybill_info,
        my_triple_batch_waybill_info,
        set_current_point,
        set_segments_place_id,
        set_segments_points_skipped,
        stq_runner,
        stq,
        claim_point_id=1,
):
    set_current_point(my_triple_batch_waybill_info, idx=0)
    set_segments_place_id(
        my_triple_batch_waybill_info, segment_ids=[0, 1], place_id=1234,
    )
    set_segments_points_skipped(
        my_triple_batch_waybill_info, segment_ids=['seg_1', 'seg_2'],
    )

    mock_processing_create_event.item_id = DEFAULT_CARGO_REF_ID
    mock_processing_create_event.expected_request = (
        build_create_event_request()
    )

    mock_client_notify_v2_push.expected_request = build_client_notify_request(
        TASK_ID, 'The point is skipped',
    )

    await stq_runner.cargo_orders_multi_skip_source_points.call(
        task_id=TASK_ID, kwargs=build_stq_kwargs(claim_point_id),
    )

    assert mock_dispatch_return.handler.times_called == 0
    assert mock_processing_create_event.mock.times_called == 1
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )
    assert mock_client_notify_v2_push.mock.times_called == 1


@pytest.mark.config(
    CARGO_ORDERS_TAXIMETER_ASYNC_OPERATIONS_STQ_SETTINGS={
        '__default__': {'max_attempts_count': 1},
    },
)
@MULTI_SKIP_SETTINGS
@pytest.mark.translations(cargo=TRANSLATIONS)
async def test_finishing_task_on_exceeding_attempts_count(
        mockserver,
        mock_driver_tags_v1_match_profile,
        mock_processing_create_event,
        mock_client_notify_v2_push,
        mock_waybill_info,
        my_triple_batch_waybill_info,
        set_current_point,
        stq_runner,
        stq,
        claim_point_id=1,
):
    set_current_point(my_triple_batch_waybill_info, idx=0)

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/return')
    def mock_waybill_return(request):
        return mockserver.make_response(
            status=500,
            json={'code': '500', 'message': 'Internal Server Error'},
        )

    mock_processing_create_event.item_id = DEFAULT_CARGO_REF_ID
    mock_processing_create_event.expected_request = (
        build_create_event_request()
    )

    mock_client_notify_v2_push.expected_request = build_client_notify_request(
        TASK_ID, 'Failed to skip the point',
    )

    await stq_runner.cargo_orders_multi_skip_source_points.call(
        task_id=TASK_ID, kwargs=build_stq_kwargs(claim_point_id),
    )

    assert mock_waybill_return.times_called == 3
    assert mock_processing_create_event.mock.times_called == 1
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )
    assert mock_client_notify_v2_push.mock.times_called == 1
