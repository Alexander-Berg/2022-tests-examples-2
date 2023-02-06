# flake8: noqa

import pytest


@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.suspend_periodic_tasks('send-statistics-task')
async def test_statistic_component(taxi_eventus_proxy, testpoint, logbroker):
    await taxi_eventus_proxy.invalidate_caches()  # clear statistics

    @testpoint('call::statistics-component::send-statistics-task')
    def task_testpoint(data):
        pass

    await taxi_eventus_proxy.enable_testpoints()

    await taxi_eventus_proxy.run_periodic_task('send-statistics-task')
    data = await task_testpoint.wait_call()
    host = data['data']['host']

    assert await logbroker.wait_publish(timeout=5)

    assert len(logbroker.data) == 1
    assert logbroker.data == [
        {
            'data': {
                'event': {
                    'created': '2019-01-01T00:00:00+00:00',
                    'statistics': {
                        'host': host,
                        'no_tvm_events': 0,
                        'services': [],
                    },
                    'idempotency_token': '',
                    'name': 'statistics',
                },
                'source': 'eventus-proxy',
                'topic': '/topic/statistics',
            },
            'name': 'communal-events-producer',
        },
    ]


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.suspend_periodic_tasks('send-statistics-task')
async def test_statistic_component_no_tvm(
        taxi_eventus_proxy, testpoint, logbroker,
):
    await taxi_eventus_proxy.invalidate_caches()  # clear statistics

    response = await taxi_eventus_proxy.post(
        '/v1/topic/event/new/bulk',
        json={
            'topic': 'test',
            'events': [
                {
                    'idempotency_token': 'token1',
                    'created': '2000-01-01T00:00:00Z',
                    'name': 'test',
                    'some_other_field': ['array_item'],
                },
                {
                    'idempotency_token': 'token2',
                    'created': '2000-01-01T00:00:01Z',
                    'name': 'test',
                    'some_other_field': ['array_item'],
                },
            ],
        },
    )
    assert response.status_code == 400

    @testpoint('call::statistics-component::send-statistics-task')
    def task_testpoint(data):
        pass

    await taxi_eventus_proxy.enable_testpoints()

    await taxi_eventus_proxy.run_periodic_task('send-statistics-task')
    data = await task_testpoint.wait_call()
    host = data['data']['host']

    assert await logbroker.wait_publish(timeout=5)

    assert len(logbroker.data) == 1
    assert logbroker.data == [
        {
            'data': {
                'event': {
                    'created': '2019-01-01T00:00:00+00:00',
                    'statistics': {
                        'host': host,
                        'no_tvm_events': 2,
                        'services': [],
                    },
                    'idempotency_token': '',
                    'name': 'statistics',
                },
                'source': 'eventus-proxy',
                'topic': '/topic/statistics',
            },
            'name': 'communal-events-producer',
        },
    ]


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
@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.suspend_periodic_tasks('send-statistics-task')
async def test_statistic_component_other_cases(
        taxi_eventus_proxy, testpoint, logbroker,
):
    inject_pub_timeout_tp = None  # pylint: disable=unused-variable

    await taxi_eventus_proxy.invalidate_caches()

    response = await taxi_eventus_proxy.post(
        '/v1/topic/event/new/bulk',
        headers={'X-Ya-Service-Ticket': MOCK_TICKET},
        json={
            'topic': 'destination_topic',
            'events': [
                {
                    'idempotency_token': 'token1',
                    'created': '2000-01-01T00:00:00Z',
                    'name': 'permitted_event',
                    'some_other_field': ['array_item'],
                },
                {
                    'idempotency_token': 'token2',
                    'created': '2000-01-01T00:00:01Z',
                    'name': 'permitted_event',
                    'some_other_field': ['array_item'],
                },
            ],
        },
    )
    assert response.status_code == 200

    @testpoint('logbroker_future_fault_injection')
    def inject_pub_timeout_tp_(data):
        pass

    inject_pub_timeout_tp = inject_pub_timeout_tp_

    response = await taxi_eventus_proxy.post(
        '/v1/topic/event/new/bulk',
        headers={'X-Ya-Service-Ticket': MOCK_TICKET},
        json={
            'topic': 'destination_topic',
            'events': [
                {
                    'idempotency_token': 'token1',
                    'created': '2000-01-01T00:00:00Z',
                    'name': 'permitted_event',
                    'some_other_field': ['array_item'],
                },
                {
                    'idempotency_token': 'token2',
                    'created': '2000-01-01T00:00:01Z',
                    'name': 'permitted_event',
                    'some_other_field': ['array_item'],
                },
            ],
        },
    )
    assert response.status_code == 504

    response = await taxi_eventus_proxy.post(
        '/v1/topic/event/new/bulk',
        headers={'X-Ya-Service-Ticket': MOCK_TICKET},
        json={
            'topic': 'test',
            'events': [
                {
                    'idempotency_token': 'token1',
                    'created': '2000-01-01T00:00:00Z',
                    'name': 'test',
                    'some_other_field': ['array_item'],
                },
                {
                    'idempotency_token': 'token2',
                    'created': '2000-01-01T00:00:01Z',
                    'name': 'test',
                    'some_other_field': ['array_item'],
                },
            ],
        },
    )
    assert response.status_code == 403

    @testpoint('call::statistics-component::send-statistics-task')
    def task_testpoint(data):
        pass

    await taxi_eventus_proxy.enable_testpoints()

    await taxi_eventus_proxy.run_periodic_task('send-statistics-task')
    data = await task_testpoint.wait_call()
    host = data['data']['host']

    assert await logbroker.wait_publish(timeout=5)

    assert len(logbroker.data) == 5
    statistics_event = next(
        (
            x
            for x in logbroker.data
            if x['data']['event']['name'] == 'statistics'
        ),
        None,
    )
    assert statistics_event == {
        'data': {
            'event': {
                'created': '2019-01-01T00:00:00+00:00',
                'idempotency_token': '',
                'name': 'statistics',
                'statistics': {
                    'host': host,
                    'no_tvm_events': 0,
                    'services': [
                        {
                            'service_name': 'mock',
                            'fail_wait_commit_events': 2,
                            'not_allowed_events': 2,
                            'success': 2,
                        },
                    ],
                },
            },
            'source': 'eventus-proxy',
            'topic': '/topic/statistics',
        },
        'name': 'communal-events-producer',
    }
