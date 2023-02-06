import dateutil.parser
import pytest

UID = 1111
LOGIN = 'ya1111'


async def test_only_finished_requests_in_decisions(
        load_json, recently, handlers, get_fine_state,
):
    expected = load_json('order_fines_state.json')

    state = await get_fine_state()
    assert state['decisions'] == expected['decisions']


async def test_recent_finished_operations_in_pending_list(
        load_json, recently, handlers, get_fine_state,
):
    expected = load_json('order_fines_state.json')

    state = await get_fine_state()
    assert state['pending_decisions'] == expected['pending_decisions']


@pytest.mark.now('2021-02-13T12:00:00+00:00')
async def test_only_recent_operations_in_pending(
        load_json, handlers, get_fine_state,
):
    expected = load_json('order_fines_state.json')
    del expected['pending_decisions'][0]

    state = await get_fine_state()
    assert state['pending_decisions'] == expected['pending_decisions']


async def test_update_idempotency(
        recently, handlers, get_fine_state, send_request,
):
    state = await get_fine_state()
    decision = state['pending_decisions'][1]
    request_body = {
        'operation_id': decision['operation_id'],
        'decision': decision['decision'],
        'reason': decision['reason'],
    }
    await send_request(request_body)

    assert not handlers.processing_create_event.has_calls


async def test_opening_event_before_first_request(
        recently,
        fines_queue,
        order_proc,
        handlers,
        send_request,
        request_body_from_payload,
):
    update_req_event = fines_queue.update_fine_request_event.copy()
    payload = update_req_event['payload']
    fines_queue.drop_unresolved_request()
    events = fines_queue.drop_all_events()
    await send_request(request_body_from_payload(payload))

    assert handlers.processing_create_event.times_called == 2
    for event in events[:2]:
        request = handlers.processing_create_event.next_call()['request']
        assert request.query['item_id'] == order_proc['_id']
        assert request.headers.get('X-Idempotency-Token') == event['event_id']
        assert request.json == event['payload']


async def test_no_opening_events_after_first_request(
        recently,
        fines_queue,
        order_proc,
        handlers,
        send_request,
        request_body_from_payload,
):
    event = fines_queue.drop_unresolved_request()
    payload = event['payload']
    await send_request(request_body_from_payload(payload))

    assert handlers.processing_create_event.times_called == 1
    request = handlers.processing_create_event.next_call()['request']
    assert request.headers.get('X-Idempotency-Token') == event['event_id']
    assert request.json == event['payload']


async def test_fail_order_does_not_exist(
        recently,
        mockserver,
        handlers,
        fines_queue,
        get_disable_reason,
        send_request_409_json,
        request_body_from_payload,
):
    @mockserver.json_handler('order-archive/v1/order_proc/retrieve')
    def _order_archive_handler(request):
        return mockserver.make_response(status=404, json={})

    event = fines_queue.update_fine_request_event
    fines_queue.drop_all_events()

    disable_reason = await get_disable_reason('unknown_id')
    assert disable_reason['code'] == 'order_does_not_exist'
    assert disable_reason == await send_request_409_json(
        request_body_from_payload(event['payload']), 'unknown_id',
    )


async def test_fail_order_bad_operation_id(
        recently,
        mockserver,
        handlers,
        fines_queue,
        send_request_400_json,
        request_body_from_payload,
):
    event = fines_queue.update_fine_request_event
    fines_queue.drop_all_events()

    response = await send_request_400_json(
        request_body_from_payload(event['payload']), 'INVALID_OPERATION_ID',
    )
    assert response['code'] == 'invalid_cursor'


async def _prepare_order_unfinished(ctx):
    ctx.order_proc['status'] = 'assigned'
    ctx.order_archive_mock.set_order_proc(ctx.order_proc)


async def _prepare_order_without_performer(ctx):
    del ctx.order_proc['performer']
    ctx.order_archive_mock.set_order_proc(ctx.order_proc)


async def _prepare_order_with_performer_null_index(ctx):
    ctx.order_proc['performer']['candidate_index'] = None
    ctx.order_archive_mock.set_order_proc(ctx.order_proc)


async def _prepare_too_late_to_rebill(ctx):
    now = '2021-05-15T10:00:00+00:00'
    ctx.mocked_time.set(dateutil.parser.parse(now))
    await ctx.taxi_order_fines.invalidate_caches()


@pytest.mark.parametrize(
    'prepare, expected_code',
    [
        (_prepare_order_unfinished, 'order_unfinished'),
        (_prepare_order_without_performer, 'order_without_performer'),
        (_prepare_order_with_performer_null_index, 'order_without_performer'),
        (_prepare_too_late_to_rebill, 'too_late_to_rebill'),
    ],
)
async def test_fail_because_of(
        prepare,
        expected_code,
        recently,
        fines_queue,
        handlers,
        order_archive_mock,
        order_proc,
        request_body_from_payload,
        taxi_order_fines,
        mocked_time,
        send_request_409_json,
        get_disable_reason,
):
    class Ctx:
        def __init__(self):
            self.order_archive_mock = order_archive_mock
            self.order_proc = order_proc
            self.mocked_time = mocked_time
            self.taxi_order_fines = taxi_order_fines

    event = fines_queue.update_fine_request_event
    fines_queue.drop_all_events()

    await prepare(Ctx())

    disable_reason = await get_disable_reason()
    assert disable_reason['code'] == expected_code
    assert disable_reason == await send_request_409_json(
        request_body_from_payload(event['payload']),
    )


async def test_fail_has_pending_operations(
        recently, handlers, order_proc, send_request_409_json, get_fine_state,
):
    state = await get_fine_state()
    disable_reason = state['new_decision']['disable_reason']
    assert disable_reason['code'] == 'has_pending_operations'

    request_body = {
        'operation_id': state['new_decision']['operation_id'],
        'decision': {'has_fine': False},
        'reason': state['decisions'][0]['reason'],
    }
    assert disable_reason == await send_request_409_json(request_body)


async def test_fail_race_condition(
        recently,
        fines_queue,
        handlers,
        order_proc,
        send_request_409_json,
        get_fine_state,
):
    fines_queue.drop_all_events()
    state = await get_fine_state()
    fines_queue.restore_all_events()
    fines_queue.drop_unresolved_request()

    request_body = {
        'operation_id': state['new_decision']['operation_id'],
        'decision': {'has_fine': False},
        'reason': {'st_ticket': 'SOMEQUEUE-123'},
    }
    fail_reason = await send_request_409_json(request_body)
    assert fail_reason['code'] == 'race_condition'


@pytest.fixture(name='recently')
async def _recently(mocked_time, taxi_order_fines):
    # 10 seconds after order_info event was sent
    now = '2021-02-13T11:00:10+00:00'
    mocked_time.set(dateutil.parser.parse(now))
    await taxi_order_fines.invalidate_caches()
    return now


@pytest.fixture(name='request_order_fines_update')
def _request_order_fines_update(taxi_order_fines):
    async def _wrapper(request_body, order_id, yandex_uid, yandex_login):
        params = {'order_id': order_id}
        headers = {
            'X-Yandex-Uid': str(yandex_uid),
            'X-Yandex-Login': yandex_login,
        }
        response = await taxi_order_fines.post(
            '/admin/order/fines/update',
            params=params,
            headers=headers,
            json=request_body,
        )
        return response

    return _wrapper


@pytest.fixture(name='send_request')
def _send_request(request_order_fines_update, order_proc):
    async def _wrapper(request_body):
        response = await request_order_fines_update(
            request_body, order_proc['_id'], UID, LOGIN,
        )
        assert response.status_code == 200

    return _wrapper


@pytest.fixture(name='send_request_409_json')
def _send_request_409_json(request_order_fines_update, order_proc):
    async def _wrapper(request_body, order_id=None):
        if order_id is None:
            order_id = order_proc['_id']
        response = await request_order_fines_update(
            request_body, order_id, UID, LOGIN,
        )
        assert response.status_code == 409
        return response.json()

    return _wrapper


@pytest.fixture(name='send_request_400_json')
def _send_request_400_json(request_order_fines_update, order_proc):
    async def _wrapper(request_body, operation_id='INVALID'):
        request_body['operation_id'] = operation_id
        response = await request_order_fines_update(
            request_body, order_proc['_id'], UID, LOGIN,
        )
        assert response.status_code == 400
        return response.json()

    return _wrapper


@pytest.fixture(name='request_body_from_payload')
def _request_body_from_payload():
    def _wrapper(payload):
        request_body = {
            'operation_id': payload['data']['operation_id'],
            'decision': payload['data']['decision'],
            'reason': {'st_ticket': payload['data']['st_ticket']},
        }
        if 'comment' in payload['data']:
            request_body['reason']['comment'] = payload['data']['comment']
        return request_body

    return _wrapper
