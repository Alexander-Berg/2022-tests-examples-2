import copy
import datetime
import itertools
import uuid

import bson
import pytest


EVENTS = [
    {
        'event_id': '12345',
        'created': '2021-02-27T09:43:06+03:00',
        'handled': True,
        'payload': {'event-index': 0, 'q': 'create', 's': 'pending'},
        'extra_order_key': 0,
    },
    {
        'event_id': '12346',
        'created': '2021-02-27T09:43:06+03:00',
        'handled': True,
        'payload': {'event-index': 1, 'q': 'assign', 's': 'assigned'},
        'extra_order_key': 1,
    },
]

EVENT_3 = [
    {
        'event_id': '12347',
        'created': '2021-02-27T09:43:06+03:00',
        'handled': True,
        'payload': {'event-index': 2, 'q': 'drive', 't': 'driving'},
        'extra_order_key': 2,
    },
]

_NOW = datetime.datetime.fromisoformat('2021-04-13T13:04:58.101')


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.parametrize(
    'filter_, event_key, idempotency_token, expected_response_code, '
    'expected_event_keys, expected_order_version, expected_processing_version,'
    'processing_called, event_index',
    [
        (
            {'status': 'assigned'},
            'transport',
            'x-transport',
            200,
            ['create', 'assign', 'drive', 'transport'],
            3,
            4,
            1,
            3,
        ),
        (
            # filter mismatch
            {'status': 'finished'},
            'transport',
            'x-transport',
            409,
            ['create', 'assign', 'drive'],
            2,
            3,
            0,
            None,
        ),
        (
            # retry last event
            {'status': 'assigned'},
            'assign',
            'x-assign',
            200,
            ['create', 'assign', 'drive'],
            2,
            3,
            1,  # we should call processing anyway,
            # because previous attempt could fail
            1,
        ),
        (
            # No optional fields
            None,
            'transport',
            'x-transport',
            200,
            ['create', 'assign', 'drive', 'transport'],
            3,
            4,
            1,
            3,
        ),
    ],
)
@pytest.mark.parametrize(
    'super_legacy',
    [
        pytest.param(False, marks=[pytest.mark.filldb(order_proc='procaas')]),
        pytest.param(True, marks=[pytest.mark.filldb(order_proc='legacy')]),
    ],
)
async def test_send_event(
        taxi_order_core,
        filter_,
        idempotency_token,
        expected_response_code,
        expected_event_keys,
        expected_order_version,
        expected_processing_version,
        event_key,
        mongodb,
        processing_called,
        event_index,
        stq,
        mockserver,
        super_legacy,
):
    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def mock_create_event(req):
        assert req.query['item_id'] == order_id
        assert req.query['extra_order_key'] == str(event_index)
        body = {'q': event_key, 'event-index': event_index}
        if super_legacy and event_key != 'transport':
            body['old']: True
        assert req.json == body
        token = f'{order_id}_e{event_index}'
        assert req.headers['x-idempotency-token'] == token
        resp = {'event_id': '123456'}
        return mockserver.make_response(status=200, json=resp)

    order_id = 'foo'

    request = {}
    if filter_ is not None:
        request['filter'] = filter_
    with stq.flushing():
        response = await taxi_order_core.post(
            f'/internal/processing/v1/event/{event_key}?order_id={order_id}',
            headers={
                'X-Idempotency-Token': idempotency_token,
                'Content-Type': 'application/bson',
            },
            data=bson.BSON.encode(request),
        )
        assert mock_create_event.times_called == processing_called

    assert response.status_code == expected_response_code
    if expected_response_code == 200:
        proc: dict = bson.BSON.decode(response.content)
    else:
        proc = mongodb.order_proc.find_one({'_id': order_id})
    assert proc
    assert 'order' in proc
    assert proc['order']['version'] == expected_order_version
    assert proc['processing']['version'] == expected_processing_version
    events = proc['order_info']['statistics']['status_updates']
    for expected, actual_event in itertools.zip_longest(
            expected_event_keys, events,
    ):
        assert actual_event['q'] == expected


@pytest.mark.parametrize(
    'events_code, expected_response', [(200, 200), (400, 500), (500, 500)],
)
@pytest.mark.filldb(order_proc='procaas')
async def test_procaas_errors(
        taxi_order_core, stq, mockserver, events_code, expected_response,
):
    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def mock_create_event(req):
        counter[0] += 1
        assert req.query['item_id'] == 'foo'
        extra_order_keys.append(int(req.query['extra_order_key']))
        if counter[0] == 1:
            assert req.json == {
                'q': 'drive',
                't': 'driving',
                'event-index': 2,
                'i': 0,
            }
            assert req.headers['x-idempotency-token'] == f'foo_e2'
        else:
            assert req.json == {'q': 'any_key', 'event-index': 3}
            assert req.headers['x-idempotency-token'] == f'foo_e3'
        if counter[0] == 0:
            resp = {'code': 'race_condition', 'message': 'it happens'}
            return mockserver.make_response(status=409, json=resp)
        resp = {'event_id': '123456'}
        return mockserver.make_response(status=200, json=resp)

    @mockserver.handler('/processing/v1/taxi/orders/events')
    def mock_events(req):
        resp = {'events': EVENTS}
        return mockserver.make_response(status=events_code, json=resp)

    counter = [-1]
    extra_order_keys = []
    with stq.flushing():
        response = await taxi_order_core.post(
            '/internal/processing/v1/event/any_key?'
            'order_id=foo&extra_order_key=3',
            headers={
                'X-Idempotency-Token': 'foo_e3',
                'Content-Type': 'application/bson',
            },
            data=bson.BSON.encode({}),
        )

    assert response.status_code == expected_response
    if expected_response == 200:
        proc: dict = bson.BSON.decode(response.content)
        assert proc['order']['version'] == 3
        assert proc['processing']['version'] == 4
        events = proc['order_info']['statistics']['status_updates']
        for expected, actual_event in itertools.zip_longest(
                ['create', 'assign', 'drive', 'any_key'], events,
        ):
            assert actual_event['q'] == expected

        assert extra_order_keys == [3, 2, 3]
        assert mock_events.times_called == 1
        assert mock_create_event.times_called == 3


_DROP = {'enabled_keys': ['noone'], 'disabled_keys': []}


@pytest.mark.parametrize(
    'processing',
    [
        {'version': 4},
        pytest.param(
            {'version': 4, 'need_start': True},
            marks=[pytest.mark.config(ORDER_CORE_DROP_NEED_START=_DROP)],
        ),
    ],
)
async def test_payload(taxi_order_core, now, mockserver, processing):
    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def _mock_create_event(req):
        assert req.json == {'q': 'transport', 't': None, 'event-index': 3}
        json = {'event_id': '123456'}
        return mockserver.make_response(status=200, json=json)

    request = {
        'event_arg': {'a': 'b', 'c': ['d', 'e', 1, 2, {}, []]},
        'extra_update': {'$set': {'order.taxi_status': 'transporting'}},
        'event_extra_payload': {'t': None},
        'fields': [
            'order_info.statistics.status_updates.q',
            'order_info.statistics.status_updates.t',
            'order_info.statistics.status_updates.h',
            'order_info.statistics.status_updates.a',
            'order.taxi_status',
            'updated',
            'processing.need_start',
            'order_info.need_sync',
        ],
    }
    response = await taxi_order_core.post(
        '/internal/processing/v1/event/transport?order_id=foo',
        headers={
            'X-Idempotency-Token': 'x-transport',
            'Content-Type': 'application/bson',
        },
        data=bson.BSON.encode(request),
    )
    assert response.status_code == 200
    proc: dict = bson.BSON.decode(response.content)
    assert proc.pop('updated') >= now
    status_updates = proc['order_info']['statistics'].pop('status_updates')
    expected_status_updates = [
        {'q': 'create'},
        {'q': 'assign'},
        {'q': 'drive', 't': 'driving'},
        {'q': 'transport', 't': None, 'h': True},
    ]
    for status, expected in zip(status_updates, expected_status_updates):
        assert status['q'] == expected['q']
        assert status.get('t', '') == expected.get('t', '')
        assert status.get('h') == expected.get('h')
    proc.pop('created')
    assert proc == {
        '_id': 'foo',
        'order': {'taxi_status': 'transporting', 'version': 3},
        'order_info': {'need_sync': True, 'statistics': {}},
        'processing': processing,
        'order_link': 'foo-link',  # this is always added
    }


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.parametrize(
    'events, due, restart_processing_due, expected_events',
    [
        (
            [],
            None,
            None,
            [
                {'q': 'create', 's': 'pending', 'event-index': 0, 'old': True},
                {
                    'q': 'assign',
                    's': 'assigned',
                    'event-index': 1,
                    'i': 0,
                    'old': True,
                },
                {'q': 'drive', 't': 'driving', 'event-index': 2, 'i': 0},
            ],
        ),
        (
            EVENTS,
            None,
            None,
            [{'q': 'drive', 't': 'driving', 'event-index': 2, 'i': 0}],
        ),
        (
            EVENTS,
            _NOW,
            None,
            [{'q': 'drive', 't': 'driving', 'event-index': 2, 'i': 0}],
        ),
        # send restart-processing with due in future
        (
            EVENTS,
            _NOW + datetime.timedelta(seconds=20),
            _NOW + datetime.timedelta(seconds=20),
            [
                {'q': 'drive', 't': 'driving', 'event-index': 2, 'i': 0},
                {'q': 'restart-processing'},
            ],
        ),
        # no lost events, send restart-processing
        (EVENTS + EVENT_3, None, None, [{'q': 'restart-processing'}]),
        (EVENTS + EVENT_3, _NOW, None, [{'q': 'restart-processing'}]),
        (
            EVENTS + EVENT_3,
            _NOW + datetime.timedelta(seconds=20),
            _NOW + datetime.timedelta(seconds=20),
            [{'q': 'restart-processing'}],
        ),
    ],
)
@pytest.mark.parametrize(
    'super_legacy',
    [
        pytest.param(False, marks=[pytest.mark.filldb(order_proc='procaas')]),
        pytest.param(True, marks=[pytest.mark.filldb(order_proc='legacy')]),
    ],
)
async def test_restart_processing(
        taxi_order_core,
        stq,
        mockserver,
        events,
        expected_events,
        due,
        restart_processing_due,
        super_legacy,
):
    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def _mock_create_event(req):
        assert req.query['item_id'] == 'foo'
        if req.json['q'] == 'restart-processing':
            if restart_processing_due is None:
                assert req.query.get('due') is None
                assert req.headers['x-idempotency-token'] == 'abc'
            else:
                due_dt = datetime.datetime.fromisoformat(req.query['due'])
                due_ts = due_dt.timestamp()
                assert datetime.datetime.utcfromtimestamp(due_ts) == due
                token = f'restart_{str(round(due_ts * 1000))}'
                assert req.headers['x-idempotency-token'] == token

        events_created.append(req.json)
        json = {'event_id': '123456'}
        return mockserver.make_response(status=200, json=json)

    @mockserver.handler('/processing/v1/taxi/orders/events')
    def mock_events(req):
        resp = {'events': events}
        return mockserver.make_response(status=200, json=resp)

    events_created = []
    patched_expected_events = copy.deepcopy(expected_events)
    if not super_legacy:
        for event in patched_expected_events:
            event.pop('old', None)

    with stq.flushing():
        params = {'order_id': 'foo'}
        if due is not None:
            params['due'] = f'{due.isoformat()}+0000'
        response = await taxi_order_core.post(
            '/internal/processing/v1/event/restart-processing',
            params=params,
            headers={
                'X-Idempotency-Token': 'abc',
                'Content-Type': 'application/bson',
            },
            data=bson.BSON.encode({}),
        )
        assert response.status_code == 200
        assert bson.BSON.decode(response.content) == {}
        assert mock_events.times_called == 1
        assert events_created == patched_expected_events


EVENTS_4 = [
    {
        'event_id': '12345',
        'created': '2021-02-27T09:43:06+03:00',
        'handled': True,
        'payload': {'event-index': 0, 'q': 'restart-processing'},
        'extra_order_key': 0,
    },
    {
        'event_id': '12346',
        'created': '2021-02-27T09:43:06+03:00',
        'handled': True,
        'payload': {'event-index': 1, 'q': 'restart-processing'},
        'extra_order_key': 1,
    },
    {
        'event_id': '12347',
        'created': '2021-02-27T09:43:06+03:00',
        'handled': True,
        'payload': {'event-index': 2, 'q': 'restart-processing'},
        'extra_order_key': 2,
    },
    {
        'event_id': '12348',
        'created': '2021-02-27T09:43:06+03:00',
        'handled': True,
        'payload': {'event-index': 3, 'q': 'restart-processing'},
        'extra_order_key': 3,
    },
]


@pytest.mark.parametrize(
    'events, expected_code',
    [
        pytest.param(
            EVENTS_4,
            400 if i < len(EVENTS_4) else 200,
            marks=(
                pytest.mark.config(
                    ORDER_CORE_STQ_PROCESSING_STARTER_RESTART_LIMIT=i,
                ),
            ),
        )
        for i in [0, 1, 2, len(EVENTS_4) + 1, len(EVENTS_4) + 100]
    ],
)
async def test_restart_processing_limit(
        stq, taxi_order_core, mockserver, events, expected_code,
):
    @mockserver.handler('/processing/v1/taxi/orders/events')
    def mock_events(req):
        resp = {'events': events}
        return mockserver.make_response(status=200, json=resp)

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def mock_create_event(req):
        json = {'event_id': '123456'}
        return mockserver.make_response(status=200, json=json)

    params = {'order_id': 'foo'}
    response = await taxi_order_core.post(
        '/internal/processing/v1/event/restart-processing',
        params=params,
        headers={
            'X-Idempotency-Token': 'abc',
            'Content-Type': 'application/bson',
        },
        data=bson.BSON.encode({}),
    )

    assert mock_events.times_called == 1
    assert response.status_code == expected_code
    if response.status_code == 400:
        assert (
            response.json()['message']
            == '\'Restart-processing\' limit reached'
        )
    else:
        assert mock_create_event.times_called == 1


@pytest.mark.filldb(order_proc='procaas')
@pytest.mark.parametrize(
    'fields, expected',
    [
        ([], []),
        (['_id'], []),
        (['order_info'], ['status_updates']),
        (['order_info.need_sync'], []),
        (['order_info.statistics'], ['status_updates']),
        (['order_info.statistics.status_updates'], ['status_updates']),
        (['order_info.statistics.status_updates.q'], ['status_updates']),
    ],
)
async def test_fields(taxi_order_core, mockserver, fields, expected):
    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def _mock_create_event(req):
        json = {'event_id': '123456'}
        return mockserver.make_response(status=200, json=json)

    request = {'fields': fields}
    response = await taxi_order_core.post(
        '/internal/processing/v1/event/transport?order_id=foo',
        headers={
            'X-Idempotency-Token': 'x-transport',
            'Content-Type': 'application/bson',
        },
        data=bson.BSON.encode(request),
    )
    assert response.status_code == 200
    proc: dict = bson.BSON.decode(response.content)
    assert set(proc['order_info']['statistics'].keys()) == set(expected)


@pytest.mark.parametrize(
    'event_key, expected_code, added',
    [('create', 200, True), ('mark_related_switched_to_cash', 409, False)],
)
async def test_post_event_to_draft(
        event_key, expected_code, added, taxi_order_core, mongodb, mockserver,
):
    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def _mock_create_event(req):
        json = {'event_id': '123456'}
        return mockserver.make_response(status=200, json=json)

    request = {'fields': ['_id']}
    response = await taxi_order_core.post(
        f'/internal/processing/v1/event/{event_key}?order_id=draft',
        headers={
            'X-Idempotency-Token': uuid.uuid4().hex,
            'Content-Type': 'application/bson',
        },
        data=bson.BSON.encode(request),
    )
    assert response.status_code == expected_code
    proc = mongodb.order_proc.find_one({'_id': 'draft'})
    events = proc['order_info']['statistics']['status_updates']
    if added:
        assert len(events) == 1
    else:
        assert events == []


@pytest.mark.config(ORDER_CORE_ORDER_PROC_STATUS_UPDATES_LIMIT=6)
@pytest.mark.parametrize(
    'data,expected_codes,expected_events',
    [
        (
            {},
            [200, 200, 500, 500],
            ['create', 'assign', 'drive', 'event1', 'event2', 'event3'],
        ),
        (
            {'force_commit': True},
            [200, 200, 200, 200],
            [
                'create',
                'assign',
                'drive',
                'event1',
                'event2',
                'event3',
                'event4',
            ],
        ),
    ],
)
async def test_order_proc_limit(
        taxi_order_core,
        mongodb,
        mockserver,
        data,
        expected_codes,
        expected_events,
):
    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def _mock_create_event(req):
        json = {'event_id': '123456'}
        return mockserver.make_response(status=200, json=json)

    send_events = ['event1', 'event2', 'event3', 'event4']
    for i in range(4):
        response = await taxi_order_core.post(
            f'/internal/processing/v1/event/{send_events[i]}?order_id=foo',
            headers={
                'X-Idempotency-Token': uuid.uuid4().hex,
                'Content-Type': 'application/bson',
            },
            data=bson.BSON.encode(data),
        )
        assert response.status_code == expected_codes[i]
    proc = mongodb.order_proc.find_one({'_id': 'foo'})
    events = proc['order_info']['statistics']['status_updates']
    events_q = [event['q'] for event in events]
    assert events_q == expected_events


EVENTS_WITHOUT_KEYS = [
    {
        'event_id': '12345',
        'created': '2021-02-27T09:43:06+03:00',
        'handled': True,
        'payload': {'event-index': 0, 'q': 'create', 's': 'pending'},
    },
    {
        'event_id': '12346',
        'created': '2021-02-27T09:43:06+03:00',
        'handled': True,
        'payload': {'event-index': 1, 'q': 'assign', 's': 'assigned'},
    },
]

RESTART = [
    {
        'event_id': '12347',
        'created': '2021-02-27T09:43:06+03:00',
        'handled': True,
        'payload': {'q': 'restart-processing'},
    },
]


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.parametrize(
    'events, keys_in_processing, extra_keys_sent, indexes_sent',
    [
        # empty order, sent all events with extra keys
        ([], [], [0, 1, 2, 3], [0, 1, 2, 3]),
        # order with only restart, sent all events with extra keys
        (RESTART, [], [0, 1, 2, 3], [0, 1, 2, 3]),
        # order with events with keys
        (EVENTS, [0, 1], [2, 3], [2, 3]),
        # order with events with keys + restart
        (EVENTS + RESTART, [0, 1], [2, 3], [2, 3]),
        # order with events without keys
        (EVENTS_WITHOUT_KEYS, [None, None], [None, None], [2, 3]),
        # order with events without keys and restart
        (RESTART + EVENTS_WITHOUT_KEYS, [None, None], [None, None], [2, 3]),
    ],
)
@pytest.mark.filldb(order_proc='procaas')
async def test_post_event_to_existing_order(
        taxi_order_core,
        stq,
        mockserver,
        events,
        keys_in_processing,
        extra_keys_sent,
        indexes_sent,
):
    order_id = 'foo'
    processing = {
        'race_count': 0,
        'success_count': 0,
        'keys_in_processing': keys_in_processing,
        'extra_keys_sent': [],
        'indexes_sent': [],
    }

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def _mock_create_event(req):
        def _calc_acceptable_key(existing_keys):
            keys_without_none = [k for k in existing_keys if k is not None]
            if not keys_without_none:
                return 0
            return max(keys_without_none) + 1

        extra_order_key = req.query.get('extra_order_key')
        if extra_order_key is not None:
            extra_order_key = int(extra_order_key)
        acceptable_key = _calc_acceptable_key(processing['keys_in_processing'])

        if extra_order_key is None or extra_order_key == acceptable_key:
            processing['success_count'] += 1
            processing['keys_in_processing'].append(extra_order_key)
            assert req.query['item_id'] == order_id
            processing['extra_keys_sent'].append(extra_order_key)
            processing['indexes_sent'].append(req.json.pop('event-index'))

            json = {'event_id': '123456'}
            return mockserver.make_response(status=200, json=json)

        processing['race_count'] += 1
        json = {'code': 'race_condition', 'message': 'it happens'}
        return mockserver.make_response(status=409, json=json)

    @mockserver.handler('/processing/v1/taxi/orders/events')
    def mock_events(req):
        resp = {'events': events}
        return mockserver.make_response(status=200, json=resp)

    with stq.flushing():
        response = await taxi_order_core.post(
            '/internal/processing/v1/event/my-reason',
            params={'order_id': order_id},
            headers={
                'X-Idempotency-Token': 'abc',
                'Content-Type': 'application/bson',
            },
            data=bson.BSON.encode({'event_extra_payload': {'i': 0}}),
        )
        assert response.status_code == 200
        assert mock_events.times_called == 1
        assert processing['race_count'] == 1
        assert processing['success_count'] == len(extra_keys_sent)
        assert processing['extra_keys_sent'] == extra_keys_sent
        assert processing['indexes_sent'] == indexes_sent

        proc: dict = bson.BSON.decode(response.content)
        # drop need_start on races with success sending of lost events
        assert proc['processing'].get('need_start') is None


@pytest.mark.parametrize(
    'create_status,expected_need_starts',
    [
        (200, [None] * 4),
        # do not drop need_start on races
        (409, [True] * 4),
        pytest.param(
            200,
            [None, None, None, True],
            marks=[
                pytest.mark.config(
                    ORDER_CORE_DROP_NEED_START={
                        'enabled_keys': ['transporting', 'change_payment'],
                        'disabled_keys': [],
                    },
                ),
            ],
        ),
        pytest.param(
            200,
            [None, None, True, None],
            marks=[
                pytest.mark.config(
                    ORDER_CORE_DROP_NEED_START={
                        'enabled_keys': [],
                        'disabled_keys': ['change_payment'],
                    },
                ),
            ],
        ),
        pytest.param(
            200,
            [None] * 4,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_DROP_NEED_START={
                        'enabled_keys': [],
                        'disabled_keys': ['restart-processing'],
                    },
                ),
            ],
        ),
    ],
)
async def test_drop_need_start(
        taxi_order_core,
        mockserver,
        stq,
        mongodb,
        create_status,
        expected_need_starts,
):
    order_id = 'foo1'

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def _mock_create_event(req):
        json = {'event_id': '123456'}
        if create_status == 409:
            json = {'code': 'race_condition', 'message': 'it happens'}
        return mockserver.make_response(status=create_status, json=json)

    @mockserver.handler('/processing/v1/taxi/orders/events')
    def _mock_events(req):
        json = {'events': []}
        return mockserver.make_response(status=200, json=json)

    events = [
        {'q': 'transporting'},
        {'q': 'restart-processing'},
        {'q': 'change_payment'},
        {'q': 'complete'},
    ]
    need_starts = []

    with stq.flushing():
        for event in events:
            response = await taxi_order_core.post(
                f'/internal/processing/v1/event/{event["q"]}',
                params={'order_id': order_id},
                headers={
                    'X-Idempotency-Token': f'abc_{event["q"]}',
                    'Content-Type': 'application/bson',
                },
                data=bson.BSON.encode({'fields': ['processing']}),
            )
            proc = mongodb.order_proc.find_one({'_id': order_id})
            need_starts.append(proc['processing'].get('need_start'))

        assert need_starts == expected_need_starts
        assert response.status_code == 200


@pytest.mark.config(ORDER_CORE_DROP_NEED_START_LAST_EVENT=True)
async def test_do_not_drop_need_start_for_not_last_event(
        taxi_order_core, mockserver, stq, mongodb, testpoint,
):
    order_id = 'foo1'

    async def send_event(event):
        return await taxi_order_core.post(
            f'/internal/processing/v1/event/{event["q"]}',
            params={'order_id': order_id},
            headers={
                'X-Idempotency-Token': f'abc_{event["q"]}',
                'Content-Type': 'application/bson',
            },
            data=bson.BSON.encode({'fields': ['processing']}),
        )

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def _mock_create_event(req):
        json = {'event_id': '123456'}
        return mockserver.make_response(status=200, json=json)

    @mockserver.handler('/processing/v1/taxi/orders/events')
    def _mock_events(req):
        json = {'events': []}
        return mockserver.make_response(status=200, json=json)

    @testpoint('before-drop-need-start')
    async def _testpoint_before_drop_need_start(event_key):
        if event_key == 'cancel':
            # `cancel` wasn't send to procaas
            # and did not drop need_start (imitate exception while the call).

            # retry new-driver-found
            await send_event({'q': 'new-driver-found'})

            proc = mongodb.order_proc.find_one({'_id': order_id})
            # succeeded new-driver-found retry should not drop need_start flag
            # set by `cancel`
            assert proc['processing'].get('need_start') is True

    with stq.flushing():
        await send_event({'q': 'new-driver-found'})
        await send_event({'q': 'cancel'})
