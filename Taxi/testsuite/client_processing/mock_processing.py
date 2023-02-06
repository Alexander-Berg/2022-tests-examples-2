import dataclasses
import datetime
import re
import typing
import uuid

import pytest


@pytest.fixture(name='processing', autouse=True)
def mock_processing(mockserver, now):
    @dataclasses.dataclass
    class Event:
        event_id: str
        scope: str
        queue: str
        item_id: str
        payload: dict
        due: datetime.datetime
        idempotency_token: str

    class Context:
        def __init__(self):
            self._events: typing.Dict[str, Event] = {}
            self._error_code = None

        def events(self, scope, queue):
            for _, event in self._events.items():
                if event.scope == scope and event.queue == queue:
                    yield event

        def set_error_code(self, error_code=500):
            self._error_code = error_code

    context = Context()

    create_event_rex = re.compile(
        r'.*/v1/(?P<scope>\w+)/(?P<queue>\w+)/create-event',
    )

    @mockserver.json_handler('/processing/v1', prefix=True)
    async def _mock_processing(request):
        match = create_event_rex.match(request.url)
        events = context._events  # pylint: disable=protected-access
        error_code = context._error_code  # pylint: disable=protected-access
        due = datetime.datetime
        if 'due' in request.query:
            due = request.query['due']
        if match is not None:
            if error_code is not None:
                return mockserver.make_response('', status=error_code)

            event_id = uuid.uuid4().hex
            request_idempotency_token = request.headers['X-Idempotency-Token']

            idempotency_key = (
                request_idempotency_token + event_id + request.query['item_id']
            )
            event = Event(
                event_id=event_id,
                scope=match['scope'],
                queue=match['queue'],
                item_id=request.query['item_id'],
                payload=request.json,
                due=due,
                idempotency_token=request_idempotency_token,
            )
            events[idempotency_key] = event

            return {'event_id': event_id}
        assert False, f'Cannot route url {request.url}'

    return context
