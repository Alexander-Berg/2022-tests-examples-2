import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from order_fines_plugins import *  # noqa: F403 F401


@pytest.fixture(name='processing_create_event_handler')
def _processing_create_event_handler(mockserver):
    @mockserver.json_handler('/processing/v1/taxi/order_fines/create-event')
    def _handler(request):
        idempotency_token = request.headers['X-Idempotency-Token']
        return {'event_id': 'event_' + idempotency_token}

    return _handler


@pytest.fixture(name='order_proc')
async def _order_proc(load_json, order_archive_mock):
    order_proc = load_json('order_proc.json')
    order_archive_mock.set_order_proc(order_proc)
    return order_proc


@pytest.fixture(name='save_decision')
def _save_decision(taxi_order_fines):
    async def _wrapper(decision, item_id: str):
        response = await taxi_order_fines.post(
            '/procaas/fines/save-decision',
            params={'item_id': item_id},
            json={'decision': decision},
        )
        assert response.status_code == 200

    return _wrapper


@pytest.fixture(name='base_fines_queue')
def _base_fines_queue(load_json):
    def _wrapper(events_path, cancelled_events_path):
        class BaseFinesQueue:
            def __init__(self):
                self.events = load_json(events_path)

            def drop_unresolved_request(self):
                return self.events.pop()

            def drop_all_events(self):
                orig_events = self.events.copy()
                self.events = []
                return orig_events

            def restore_all_events(self):
                self.events = load_json(events_path)

            def restore_events_rejected_fine(self):
                self.events = load_json(cancelled_events_path)

            @property
            def update_fine_request_event(self):
                return self.events[1]

            @property
            def unresolved_request_event(self):
                return self.events[-1]

        return BaseFinesQueue()

    return _wrapper


@pytest.fixture(name='handlers')
def _processing_handlers(
        mockserver, processing_create_event_handler, fines_queue,
):
    @mockserver.json_handler('/processing/v1/taxi/order_fines/events')
    def _processing_events_handler(request):
        return {'events': fines_queue.events}

    class Handlers:
        processing_events = _processing_events_handler
        processing_create_event = processing_create_event_handler

    return Handlers()


@pytest.fixture(name='fines_queue')
def _fines_queue(base_fines_queue):
    return base_fines_queue(
        events_path='processing_events.json',
        cancelled_events_path='cancelled_fine_events.json',
    )


@pytest.fixture(name='handlers_automated_fines')
def _processing_handlers_automated_fines(
        mockserver, processing_create_event_handler, automated_fines_queue,
):
    @mockserver.json_handler('/processing/v1/taxi/order_fines/events')
    def _processing_events_handler(request):
        return {'events': automated_fines_queue.events}

    class Handlers:
        processing_events = _processing_events_handler
        processing_create_event = processing_create_event_handler

    return Handlers()


@pytest.fixture(name='automated_fines_queue')
def _automated_fines_queue(base_fines_queue):
    return base_fines_queue(
        events_path='processing_events_automated_fines.json',
        cancelled_events_path='cancelled_fine_events_automated_fines.json',
    )


@pytest.fixture(name='request_order_fines_state')
def _request_order_fines_state(taxi_order_fines):
    async def _wrapper(order_id, yandex_uid):
        params = {'order_id': order_id}
        headers = {'X-Yandex-Uid': str(yandex_uid)}
        response = await taxi_order_fines.get(
            '/admin/order/fines/state', params=params, headers=headers,
        )
        return response

    return _wrapper


@pytest.fixture(name='get_fine_state')
def _get_fine_state(request_order_fines_state, order_proc):
    async def _wrapper(x_uid=1111):
        response = await request_order_fines_state(order_proc['_id'], x_uid)
        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='get_disable_reason')
def _get_disable_reason(request_order_fines_state, order_proc):
    async def _wrapper(order_id=None, x_uid=1111):
        if order_id is None:
            order_id = order_proc['_id']

        response = await request_order_fines_state(order_id, x_uid)
        assert response.status_code == 200
        new_decision = response.json()['new_decision']
        assert 'disable_reason' in new_decision
        return new_decision['disable_reason']

    return _wrapper
