import random

import pytest

SCOPE = 'cargo'
QUEUE = 'crm_process_name'
ITEM_ID = '123'
STALE = 'stale'
PRIMARY = 'primary'


@pytest.mark.parametrize(
    'read_preferences,should_take_events_from_cache,should_reauest_procaas',
    [(PRIMARY, False, True), (STALE, True, False)],
)
async def test_read_preferences_behaviour(
        read_events,
        write_events,
        all_events,
        event_producer,
        procaas_events_handler,
        read_preferences,
        should_take_events_from_cache,
        should_reauest_procaas,
):
    event_producer.events = all_events
    cached_events = all_events[:-1]
    await write_events(cached_events)
    events_from_proxy = await read_events(read_preferences=read_preferences)

    events_was_taken_from_cache = cached_events == events_from_proxy
    procaas_was_requested = procaas_events_handler.has_calls

    assert events_was_taken_from_cache == should_take_events_from_cache
    assert procaas_was_requested == should_reauest_procaas


async def test_read_from_primary_if_cache_is_empty(
        read_events, procaas_events_handler,
):
    await read_events(read_preferences=STALE)
    assert procaas_events_handler.times_called == 1


async def test_keep_same_order_in_cache(write_events, read_events, all_events):
    events = all_events.copy()
    random.shuffle(events)
    await write_events(events)
    cached_events = await read_events(read_preferences=STALE)
    assert events == cached_events


async def test_cant_handle_400_from_procaas(mockserver, taxi_cargo_crm):
    @mockserver.json_handler('/processing/v1/cargo/unknown_queue/events')
    def _handler(request):
        body = {
            'code': 'no_such_queue',
            'message': 'Queue "unknown_queue" does not exist',
        }
        return mockserver.make_response(status=400, json=body)

    params = {
        'scope': 'cargo',
        'queue': 'unknown_queue',
        'item_id': '123',
        'read_preferences': PRIMARY,
    }
    response = await taxi_cargo_crm.get(
        '/procaas/caching-proxy/events', params=params,
    )
    assert response.status_code == 500


@pytest.fixture(name='read_events')
def _read_events(taxi_cargo_crm, common_params):
    async def wrapper(read_preferences=STALE):
        params = {'read_preferences': read_preferences}
        params.update(common_params)
        response = await taxi_cargo_crm.get(
            '/procaas/caching-proxy/events', params=params,
        )
        assert response.status_code == 200
        return response.json()['events']

    return wrapper


@pytest.fixture(name='write_events')
def _write_events(taxi_cargo_crm, common_params):
    async def wrapper(events):
        for event in events:
            response = await taxi_cargo_crm.post(
                '/procaas/caching-proxy/event',
                params=common_params,
                json=event,
            )
            assert response.status_code == 200

    return wrapper


@pytest.fixture(name='common_params')
def _common_params():
    return {'scope': SCOPE, 'queue': QUEUE, 'item_id': ITEM_ID}


@pytest.fixture(name='all_events')
def _all_events():
    return [
        {
            'event_id': '1',
            'created': '2021-06-08T01:00:00+00:00',
            'payload': {'kind': 'some_kind_1', 'data': {}},
        },
        {
            'event_id': '2',
            'created': '2021-06-08T02:00:00+00:00',
            'payload': {'kind': 'some_kind_2', 'data': {}},
        },
        {
            'event_id': '3',
            'created': '2021-06-08T03:00:00+00:00',
            'payload': {'kind': 'some_kind_3', 'data': {}},
        },
        {
            'event_id': '4',
            'created': '2021-06-08T04:00:00+00:00',
            'payload': {'kind': 'some_kind_4', 'data': {}},
        },
    ]


@pytest.fixture(name='event_producer')
def _event_producer():
    class EventProducer:
        def __init__(self):
            self.events = []

        def enriched_events(self):
            enriched = []
            for event in self.events:
                modified = event.copy()
                modified['handled'] = True
                enriched.append(modified)
            return enriched

    return EventProducer()


@pytest.fixture(name='procaas_events_handler')
def _procaas_events_handler(mockserver, event_producer):
    url = '/processing/v1/%s/%s/events' % (SCOPE, QUEUE)

    @mockserver.json_handler(url)
    def handler(request):
        return {'events': event_producer.enriched_events()}

    return handler
