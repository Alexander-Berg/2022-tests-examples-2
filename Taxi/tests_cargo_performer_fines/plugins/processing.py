import pytest


@pytest.fixture(name='mock_create_event')
def _mock_create_event(mockserver):
    def mock(
            event_id='event_id_1',
            item_id=None,
            event=None,
            idempotency_token=None,
            queue='performer_fines',
            error_code=None,
    ):
        @mockserver.json_handler(f'/processing/v1/cargo/{queue}/create-event')
        def create_event(request):
            if error_code:
                return mockserver.make_response(
                    status=error_code,
                    json={'code': 'invalid_payload', 'message': 'error'},
                )
            if item_id is not None:
                assert request.query['item_id'] == item_id
            if idempotency_token is not None:
                assert (
                    request.headers['X-Idempotency-Token'] == idempotency_token
                )
            if event is not None:
                assert request.json == event

            return {'event_id': event_id}

        return create_event

    return mock


@pytest.fixture(name='start_stq_event')
def _mock_start_stq_event():
    def mock(stq_task_id='test_stq'):
        return {
            'event_id': '1',
            'created': '2020-02-25T06:00:00+03:00',
            'payload': {
                'kind': 'start-stq',
                'tag': 'taxi-order-complete',
                'data': {'stq_task_id': stq_task_id},
            },
            'handled': True,
        }

    return mock


@pytest.fixture(name='mock_fetch_events')
def _mock_fetch_events(mockserver):
    def mock(events=None, queue='performer_fines'):
        @mockserver.json_handler(f'/processing/v1/cargo/{queue}/events')
        def _events(request):
            return {'events': events if events is not None else []}

    return mock
