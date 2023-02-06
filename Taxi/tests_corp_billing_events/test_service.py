import base64
import dataclasses
import datetime
import hashlib
import hmac
import itertools
import json
import time

import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from corp_billing_events_plugins.generated_tests import *  # noqa


async def test_empty_events_break_nothing(_register_events):
    result = await _register_events([])
    assert not result.registred_events


@pytest.mark.parametrize('reverse_input', [False, True])
async def test_keep_insertion_order(
        load_json, _register_events, reverse_input,
):
    # Server gives a guarantee that you read journal entries in
    # the same order they were registred.

    input_events = load_json('corp_orders_events.json')
    if reverse_input:
        input_events = list(reversed(input_events))
    result = await _register_events(input_events)
    registred_events = result.registred_events['corp']

    assert _extract_ids(input_events) == _extract_ids(registred_events)


@pytest.mark.parametrize('bulk', [False, True])
async def test_singles_equal_bulk(
        load_json, _register_events, _read_events, bulk,
):
    # You can insert event-by-event or insert all events bulk. Functional
    # results are the same. But bulk insertions may be more efficient.

    input_events = load_json('corp_orders_events.json')

    if bulk:
        await _register_events(input_events)
    else:
        for event in input_events:
            await _register_events([event])

    dummy_cursor, registred_events = await _read_events('corp')

    assert _extract_ids(input_events) == _extract_ids(registred_events)


async def test_insert_different_namespaces(load_json, _register_events):
    # Server supports bulk insertion of events withing different namespaces.

    corp_events = load_json('corp_orders_events.json')
    hiring_events = load_json('hiring_activity_events.json')
    result = await _register_events(corp_events + hiring_events)
    registred_corp = result.registred_events['corp']
    registred_hiring = result.registred_events['hiring']

    assert _extract_ids(corp_events) == _extract_ids(registred_corp)
    assert _extract_ids(hiring_events) == _extract_ids(registred_hiring)


async def test_idempotency(load_json, _register_events):
    # You can pass events two or more times. Server inserts only
    # previously unknown events.

    input_events = load_json('corp_orders_events.json')
    for dummy_i in range(2):
        result = await _register_events(input_events)
        registred_events = result.registred_events['corp']

        # Second time result is the same
        assert _extract_ids(input_events) == _extract_ids(registred_events)


async def test_consider_timezones(load_json, _register_events):
    # Client can pass time in any timezone. For example, in UTC (+00:00)
    # or in Asia/Yekaterinburg (+05:00). Server handles it correctly.

    input_events = load_json('corp_orders_events.json')[:2]
    input_events[0]['occured_at'] = '2019-09-13T10:00:00+00:00'
    input_events[1]['occured_at'] = '2019-09-13T15:00:00+05:00'
    result = await _register_events(input_events)
    registred_events = result.registred_events['corp']

    same_occured_at = _to_datetime(input_events[0]['occured_at'])
    for event in input_events + registred_events:
        event_occured_at = _to_datetime(event['occured_at'])
        assert event_occured_at == same_occured_at


@pytest.mark.config(CORP_BILLING_EVENTS_JOURNAL_CHUNK_SIZE=1)
async def test_read_all_journal(load_json, _register_events, _read_events):
    # Server gives only new events to subscribers. New event means client
    # didn't see it before.

    input_events = load_json('corp_orders_events.json')
    await _register_events(input_events)
    registred_events = []
    cursor = None
    while True:
        cursor, new_events = await _read_events('corp', cursor)
        if not new_events:
            break
        registred_events.extend(new_events)

    assert _extract_ids(input_events) == _extract_ids(registred_events)


@pytest.mark.config(CORP_BILLING_EVENTS_JOURNAL_CHUNK_SIZE=2)
async def test_cursor_chunk_size(load_json, _register_events, _read_events):
    input_events = load_json('corp_orders_events.json')
    await _register_events(input_events)
    dummy_cursor, registred_events = await _read_events('corp')
    assert len(registred_events) == 2  # chunk_size


async def test_cursor_gaps_awaited(load_json, _register_events, _read_events):
    input_events = load_json('corp_orders_events.json')
    await _register_events(input_events)
    cursor = _build_cursor(last_known_id=3, holes=[(1, -1)])
    dummy_cursor, registred_events = await _read_events('corp', cursor, 'eats')

    expected_ids = _extract_ids([input_events[0]] + input_events[3:])
    assert _extract_ids(registred_events) == expected_ids


async def test_too_old_gaps_forgotten(
        load_json, _register_events, _read_events,
):
    cursor = _build_cursor(last_known_id=3, holes=[(1, -100500)])
    new_cursor, dummy_events = await _read_events('corp', cursor)

    expected_cursor = _build_cursor(last_known_id=3, holes=[])
    assert _load_cursor(new_cursor) == _load_cursor(expected_cursor)


async def test_double_insertion_doesnt_affect_cursor(
        load_json, _register_events, _read_events,
):
    input_events = load_json('corp_orders_events.json')
    # insert twice a few events
    few = 2
    await _register_events(input_events[:few])
    await _register_events(input_events[:few])
    # insert all events (already known and completely new)
    result = await _register_events(input_events)

    output_cursor = result.cursors['corp']
    expected_cursor = _build_cursor(last_known_id=len(input_events), holes=[])
    assert _load_cursor(output_cursor) == _load_cursor(expected_cursor)


async def test_find_changed_topics(load_json, _register_events):
    # Typical usage: find changed topics and fetch all events withing
    # changed topics.

    # All events in corp_orders_events.json relate only to 2 (two) topics.

    input_events = load_json('corp_orders_events.json')
    result = await _register_events(input_events)

    assert len(result.changed_topics['corp']) == 2


async def test_full_topics(load_json, _register_events):
    # Full topics contain all events.

    input_events = load_json('corp_orders_events.json')
    result = await _register_events(input_events)

    all_events_count = int(
        sum(len(obj['events']) for obj in result.full_topics.values()),
    )

    assert all_events_count == len(input_events)


@pytest.mark.parametrize('reverse_input', [False, True])
async def test_compacted_topics(load_json, _register_events, reverse_input):
    # But often you need only latest revision of each event within
    # topic. That's why api provides "compacted topics".

    # To simplify this test meta of compacted events has flag skiped=true.

    input_events = load_json('corp_orders_events.json')
    if reverse_input:
        input_events = list(reversed(input_events))
    result = await _register_events(input_events)

    key = ('corp', 'order', 'c8c646a8eaa94e4eba7ecb6d4274bd7f')
    compacted = result.compacted_topics[key]

    assert not any(
        event for event in compacted['events'] if event['meta'].get('skipped')
    )


async def test_topic_revision(load_json, _register_events):
    input_events = load_json('corp_orders_events.json')
    result = await _register_events(input_events)
    key = ('corp', 'order', 'c8c646a8eaa94e4eba7ecb6d4274bd7f')

    compacted_revision = result.compacted_topics[key]['topic']['revision']
    full_revision = result.full_topics[key]['topic']['revision']
    full_events = result.full_topics[key]['events']

    assert compacted_revision == full_revision == len(full_events)


@pytest.mark.config(CORP_BILLING_EVENTS_JOURNAL_DELAY_MS=1000)
async def test_no_x_polling_delay_if_has_events(
        load_json, read_journal_full, _register_events,
):
    input_events = load_json('corp_orders_events.json')
    await _register_events(input_events)

    response = await read_journal_full('corp')
    assert response.status_code == 200
    assert response.headers['X-Polling-Delay-Ms'] == '0'


@pytest.mark.config(CORP_BILLING_EVENTS_JOURNAL_DELAY_MS=1000)
async def test_x_polling_delay_if_no_events(
        read_journal_full, _register_events,
):
    response = await read_journal_full('corp')
    assert response.status_code == 200
    assert response.headers['X-Polling-Delay-Ms'] == '1000'


async def test_metrics(
        load_json,
        _register_events,
        taxi_corp_billing_events,
        taxi_corp_billing_events_monitor,
):
    await taxi_corp_billing_events.tests_control(reset_metrics=True)

    input_events = load_json('corp_orders_events.json')
    expected: dict = {'$meta': {'solomon_children_labels': 'topic_type'}}
    for event in input_events:
        topic_type = event['topic']['type']
        if topic_type not in expected:
            expected[topic_type] = {
                '$meta': {'solomon_children_labels': 'event_type'},
            }
        if event['type'] not in expected[topic_type]:
            expected[topic_type][event['type']] = 0
        expected[topic_type][event['type']] += 1

    await _register_events(input_events)

    metrics = await taxi_corp_billing_events_monitor.get_metrics(
        'billing_event',
    )
    assert metrics['billing_event'] == expected


@pytest.fixture
def _register_events(
        push_events, read_journal_full, read_journal_topics, get_topics,
):
    async def _wrapper(events):
        namespaces = {e['namespace'] for e in events}

        response = await push_events(events)
        assert response.status_code == 200

        registred_events = {}
        cursors = {}
        changed_topics = {}
        for namespace in namespaces:
            response = await read_journal_full(namespace)
            assert response.status_code == 200
            response_body = response.json()
            registred_events[namespace] = response_body['events']
            cursors[namespace] = response_body['cursor']

            response = await read_journal_topics(namespace)
            assert response.status_code == 200
            changed_topics[namespace] = response.json()['changed_topics']

        all_changed_topics = list(itertools.chain(*changed_topics.values()))

        response = await get_topics(all_changed_topics)
        assert response.status_code == 200
        full_topics = {
            _topic_id(obj): obj for obj in response.json()['topics']
        }

        response = await get_topics(all_changed_topics, compact=True)
        assert response.status_code == 200
        compacted_topics = {
            _topic_id(obj): obj for obj in response.json()['topics']
        }

        @dataclasses.dataclass
        class Result:
            registred_events: dict
            cursors: dict
            changed_topics: dict
            full_topics: list
            compacted_topics: list

        return Result(
            registred_events,
            cursors,
            changed_topics,
            full_topics,
            compacted_topics,
        )

    return _wrapper


@pytest.fixture
def _read_events(read_journal_full):
    async def _wrapper(namespace, cursor=None, consumer=None):
        response = await read_journal_full(namespace, cursor, consumer)
        assert response.status_code == 200
        response_body = response.json()

        return response_body['cursor'], response_body['events']

    return _wrapper


def _extract_ids(events):
    return [_event_id(event) for event in events]


def _event_id(event):
    return (
        event['namespace'],
        event['topic']['type'],
        event['topic']['external_ref'],
        event['type'],
        event.get('external_ref'),
        event['meta_schema_version'],
        _to_datetime(event['occured_at']),
    )


def _topic_id(changed_topic):
    return (
        changed_topic['namespace'],
        changed_topic['topic']['type'],
        changed_topic['topic']['external_ref'],
    )


def _to_datetime(timestring):
    return datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S%z')


def _load_cursor(cursor):
    payload_part = cursor.split('.')[1].encode()
    payload_part += b'=' * (-len(payload_part) % 4)
    return json.loads(base64.b64decode(payload_part))


def _build_cursor(last_known_id, holes):
    payload = _build_cursor_dict(last_known_id, holes)
    return _jwt_hs512(payload, b'secret').decode()


def _build_cursor_dict(last_known_id, holes):
    cursor = {'version': 1, 'last_known_id': last_known_id, 'holes': []}
    for event_id, delta_seconds in holes:
        timestamp = int(time.time()) + delta_seconds
        cursor['holes'].append({'id': event_id, 'timestamp': timestamp})
    return cursor


def _jwt_hs512(payload, key):
    header = {'alg': 'HS512', 'typ': 'JWT'}
    signing_input = b'.'.join([_b64_encode(header), _b64_encode(payload)])
    signature = hmac.new(key, signing_input, hashlib.sha512).digest()
    return b'.'.join(
        [signing_input, base64.urlsafe_b64encode(signature).rstrip(b'=')],
    )


def _b64_encode(dct):
    binary = json.dumps(dct, separators=(',', ':')).encode()
    return base64.urlsafe_b64encode(binary).rstrip(b'=')
