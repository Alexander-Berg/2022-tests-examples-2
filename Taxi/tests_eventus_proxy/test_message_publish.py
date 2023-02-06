# flake8: noqa
import asyncio
import time

import pytest

# Generated via `tvmknife unittest service -s 111 -d 2345`
MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgUIbxCpEg:JPkTDF6JW2GWxCHNb8y1oSrjSpq_vezY5plDrow'
    'iA8wqKvAtObfxHuM1_tlq0PogdEfM7WjhVtTrZMLkRzcsxY7Sd20XxvIGax_58h4TSOCWd55D'
    'RQJzzBUILhnBx0fpt48p3-VDRRbA6Y72DT-SHK8yZOoFGu6sTVSStaojwbE'
)
MOCK_SERVICE_NAME = 'mock'


@pytest.mark.config(
    EVENTUS_PROXY_PUBLISHERS=[
        {
            'service_name': MOCK_SERVICE_NAME,
            'topics_and_event_names': [
                {
                    'topic': 'destination_topic',
                    'event_name': 'permitted_event',
                },
                {
                    'topic': 'destination_topic_timeout',
                    'event_name': 'permitted_event',
                },
            ],
        },
    ],
    EVENTUS_PROXY_TOPIC_PUBLISH_TIMEOUTS=[
        {'topic': 'destination_topic', 'timeout_ms': 100},
        {'topic': 'destination_topic_timeout', 'timeout_ms': 10},
    ],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': MOCK_SERVICE_NAME, 'dst': 'eventus-proxy'}],
)
@pytest.mark.parametrize(
    'dst_topic,event_name,status_code,inject_pub_timeout,is_message_published',
    (
        ('destination_topic', 'permitted_event', 200, False, True),
        ('destination_topic', 'not_permitted_event', 403, False, False),
        ('destination_topic_timeout', 'permitted_event', 504, True, True),
    ),
)
@pytest.mark.suspend_periodic_tasks('send-statistics-task')
async def test_message_publish(
        taxi_eventus_proxy,
        testpoint,
        logbroker,
        dst_topic,
        event_name,
        status_code,
        inject_pub_timeout,
        is_message_published,
):
    inject_pub_timeout_tp = None  # pylint: disable=unused-variable
    if inject_pub_timeout:

        @testpoint('logbroker_future_fault_injection')
        def inject_pub_timeout_tp_(data):
            pass

        inject_pub_timeout_tp = inject_pub_timeout_tp_

    await taxi_eventus_proxy.invalidate_caches()  # update configs

    response = await taxi_eventus_proxy.post(
        '/v1/topic/event/new/bulk',
        headers={'X-Ya-Service-Ticket': MOCK_TICKET},
        json={
            'topic': dst_topic,
            'events': [
                {
                    'idempotency_token': 'token1',
                    'created': '2000-01-01T00:00:00Z',
                    'name': event_name,
                    'some_other_field': ['array_item'],
                },
                {
                    'idempotency_token': 'token2',
                    'created': '2000-01-01T00:00:01Z',
                    'name': event_name,
                    'some_other_field': ['array_item'],
                },
            ],
        },
    )
    assert response.status_code == status_code

    if is_message_published:
        assert await logbroker.wait_publish(timeout=5)

        assert len(logbroker.data) == 2
        # For case of http code 504 there is not possible to stop publishing
        # of logbroker data, so, check it is ok.
        assert logbroker.data == [
            {
                'name': 'communal-events-producer',
                'data': {
                    'event': {
                        'created': '2000-01-01T00:00:00+00:00',
                        'idempotency_token': 'token1',
                        'name': event_name,
                        'some_other_field': ['array_item'],
                    },
                    'topic': dst_topic,
                    'source': MOCK_SERVICE_NAME,
                },
            },
            {
                'name': 'communal-events-producer',
                'data': {
                    'event': {
                        'created': '2000-01-01T00:00:01+00:00',
                        'idempotency_token': 'token2',
                        'name': event_name,
                        'some_other_field': ['array_item'],
                    },
                    'topic': dst_topic,
                    'source': MOCK_SERVICE_NAME,
                },
            },
        ]
    else:
        # Wait some time, about 25ms
        deadline = time.time() + 0.025
        while deadline > time.time() and not logbroker.data:
            await asyncio.sleep(0.002)
        assert not logbroker.data


@pytest.mark.skip(reason='skipped until second producer added')
@pytest.mark.config(
    EVENTUS_PROXY_PUBLISHERS=[
        {
            'service_name': MOCK_SERVICE_NAME,
            'topics_and_event_names': [
                {'topic': 'destination_topic_1', 'event_name': 'event'},
                {'topic': 'destination_topic_2', 'event_name': 'event'},
            ],
        },
    ],
    EVENTUS_PROXY_TOPIC_PUBLISH_TIMEOUTS=[
        {'topic': 'destination_topic_1', 'timeout_ms': 100},
        {'topic': 'destination_topic_2', 'timeout_ms': 100},
    ],
    EVENTUS_PROXY_TOPICS_PRODUCERS={
        '__default__': 'communal-events-producer',
        'destination_topic_2': 'test-producer',
    },
)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': MOCK_SERVICE_NAME, 'dst': 'eventus-proxy'}],
)
@pytest.mark.suspend_periodic_tasks('send-statistics-task')
async def test_message_publish_several_producers(
        taxi_eventus_proxy, logbroker,
):
    await taxi_eventus_proxy.invalidate_caches()  # update configs

    response = await taxi_eventus_proxy.post(
        '/v1/topic/event/new/bulk',
        headers={'X-Ya-Service-Ticket': MOCK_TICKET},
        json={
            'topic': 'destination_topic_1',
            'events': [
                {
                    'idempotency_token': 'token1',
                    'created': '2000-01-01T00:00:00Z',
                    'name': 'event',
                    'some_other_field': ['array_item'],
                },
                {
                    'idempotency_token': 'token2',
                    'created': '2000-01-01T00:00:01Z',
                    'name': 'event',
                    'some_other_field': ['array_item'],
                },
            ],
        },
    )
    assert response.status_code == 200

    response = await taxi_eventus_proxy.post(
        '/v1/topic/event/new/bulk',
        headers={'X-Ya-Service-Ticket': MOCK_TICKET},
        json={
            'topic': 'destination_topic_2',
            'events': [
                {
                    'idempotency_token': 'token1',
                    'created': '2000-01-01T00:00:00Z',
                    'name': 'event',
                    'some_other_field': ['array_item'],
                },
                {
                    'idempotency_token': 'token2',
                    'created': '2000-01-01T00:00:01Z',
                    'name': 'event',
                    'some_other_field': ['array_item'],
                },
            ],
        },
    )
    assert response.status_code == 200

    assert await logbroker.wait_publish(timeout=5)

    assert len(logbroker.data) == 4
    # For case of http code 504 there is not possible to stop publishing
    # of logbroker data, so, check it is ok.
    assert logbroker.data == [
        {
            'name': 'communal-events-producer',
            'data': {
                'event': {
                    'created': '2000-01-01T00:00:00+00:00',
                    'idempotency_token': 'token1',
                    'name': 'event',
                    'some_other_field': ['array_item'],
                },
                'topic': 'destination_topic_1',
                'source': MOCK_SERVICE_NAME,
            },
        },
        {
            'name': 'communal-events-producer',
            'data': {
                'event': {
                    'created': '2000-01-01T00:00:01+00:00',
                    'idempotency_token': 'token2',
                    'name': 'event',
                    'some_other_field': ['array_item'],
                },
                'topic': 'destination_topic_1',
                'source': MOCK_SERVICE_NAME,
            },
        },
        {
            'name': 'test-producer',
            'data': {
                'event': {
                    'created': '2000-01-01T00:00:00+00:00',
                    'idempotency_token': 'token1',
                    'name': 'event',
                    'some_other_field': ['array_item'],
                },
                'topic': 'destination_topic_2',
                'source': MOCK_SERVICE_NAME,
            },
        },
        {
            'name': 'test-producer',
            'data': {
                'event': {
                    'created': '2000-01-01T00:00:01+00:00',
                    'idempotency_token': 'token2',
                    'name': 'event',
                    'some_other_field': ['array_item'],
                },
                'topic': 'destination_topic_2',
                'source': MOCK_SERVICE_NAME,
            },
        },
    ]
