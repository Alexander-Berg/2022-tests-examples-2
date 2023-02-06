# pylint: disable=invalid-name
import datetime

import pytest

from taxi import discovery

from taxi_billing_buffer_proxy import stq_task
from taxi_billing_buffer_proxy.common import buffer


@pytest.fixture(name='pull')
def pull_fixture(request_headers, taxi_billing_buffer_proxy_client):
    async def wrapper_pull(request_id):
        return await taxi_billing_buffer_proxy_client.post(
            'v1/poll/taximeter',
            json={'request_id': request_id},
            headers=request_headers,
        )

    return wrapper_pull


@pytest.fixture(name='push')
def push_fixture(request_headers, taxi_billing_buffer_proxy_client):
    async def wrapper_push(data):
        return await taxi_billing_buffer_proxy_client.post(
            'v1/push/taximeter', json=data, headers=request_headers,
        )

    return wrapper_push


def patch_buffer_to_valid_partition(monkeypatch):
    monkeypatch.setattr(
        buffer.Buffer, 'is_valid_partition', lambda *x, **y: True,
    )


async def test_taximeter_task(
        taxi_billing_buffer_proxy_stq_context,
        pull,
        push,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
):
    patch_buffer_to_valid_partition(monkeypatch)
    await push(
        data={
            'request_id': 'request1',
            'request': {
                'foo': 'bar',
                'external_event_ref': 'external_event_ref1',
                'request_id': 'bar/external_event_ref1',
            },
        },
    )
    await push(
        data={
            'request_id': 'request2',
            'request': {
                'foo': 'taz',
                'external_event_ref': 'external_event_ref2',
                'request_id': 'taz/external_event_ref2',
            },
        },
    )

    @patch_aiohttp_session(discovery.find_service('taximeter').url, 'post')
    def patch_send_request(*args, **kwargs):
        data = kwargs['json']
        assert len(data) == 2
        assert 'foo' in data[0]
        assert 'foo' in data[1]
        return response_mock(
            status=200,
            json=[{'request_id': 'taz/external_event_ref2', 'quas': 'wex'}],
            text=None,
        )

    await stq_task.task(taxi_billing_buffer_proxy_stq_context, 'taximeter')

    assert len(patch_send_request.calls) == 1

    response = await pull(request_id='request1')
    assert response is not None
    assert response.status == 200
    assert await response.json() == {
        'status': 'sent',
        'response': {'http_status': 200, 'json': [], 'text': None},
    }

    response = await pull(request_id='request2')
    assert response is not None
    assert response.status == 200
    assert await response.json() == {
        'status': 'sent',
        'response': {
            'http_status': 200,
            'json': [{'request_id': 'taz/external_event_ref2', 'quas': 'wex'}],
            'text': None,
        },
    }


@pytest.mark.parametrize(
    ['buffer_request', 'taximeter_response', 'expected_poll_response'],
    [
        (
            {
                'request_id': 'request400',
                'request': {
                    'foo': 'bar',
                    'external_event_ref': 'external_event_ref400',
                    'request_id': 'bar/external_event_ref400',
                },
            },
            {'status': 400, 'json': None, 'text': 'Bad request'},
            {
                'status': 'sent',
                'response': {
                    'http_status': 400,
                    'text': 'Bad request',
                    'json': None,
                },
            },
        ),
        (
            {
                'request_id': 'request500',
                'request': {
                    'foo': 'bar',
                    'external_event_ref': 'external_event_ref500',
                    'request_id': 'bar/external_event_ref500',
                },
            },
            {'status': 500, 'json': None, 'text': 'Something went wrong'},
            {
                'status': 'sent',
                'response': {
                    'http_status': 500,
                    'text': 'Something went wrong',
                    'json': None,
                },
            },
        ),
    ],
)
async def test_taximeter_task_via_error_response(
        buffer_request,
        taximeter_response,
        expected_poll_response,
        pull,
        push,
        taxi_billing_buffer_proxy_stq_context,
        response_mock,
        patch_aiohttp_session,
        monkeypatch,
):
    patch_buffer_to_valid_partition(monkeypatch)
    await push(data=buffer_request)

    @patch_aiohttp_session(discovery.find_service('taximeter').url, 'post')
    def patch_send_request(*args, **kwargs):
        data = kwargs['json']
        assert len(data) == 1
        assert 'foo' in data[0]
        return response_mock(**taximeter_response)

    await stq_task.task(taxi_billing_buffer_proxy_stq_context, 'taximeter')

    assert len(patch_send_request.calls) == 1

    response = await pull(request_id=buffer_request['request_id'])
    assert response is not None
    assert response.status == 200
    assert await response.json() == expected_poll_response


@pytest.mark.config(BILLING_BUFFER_PROXY_BATCH_SIZE={'taximeter': 1})
async def test_limit(
        taxi_billing_buffer_proxy_stq_context,
        pull,
        push,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
):
    patch_buffer_to_valid_partition(monkeypatch)
    await push(
        data={
            'request_id': 'request1',
            'request': {
                'foo': 'bar',
                'external_event_ref': 'external_event_ref1',
                'request_id': 'bar/external_event_ref1',
            },
        },
    )
    await push(
        data={
            'request_id': 'request2',
            'request': {
                'foo': 'bar',
                'external_event_ref': 'external_event_ref2',
                'request_id': 'bar/external_event_ref2',
            },
        },
    )

    @patch_aiohttp_session(discovery.find_service('taximeter').url, 'post')
    def patch_send_request(*args, **kwargs):
        data = kwargs['json']
        assert len(data) == 1
        assert 'foo' in data[0]
        return response_mock(status=200, json={}, text='{}')

    await stq_task.task(taxi_billing_buffer_proxy_stq_context, 'taximeter')

    assert len(patch_send_request.calls) == 1

    response = await pull(request_id='request1')
    assert response is not None
    assert response.status == 200
    assert await response.json() == {
        'response': {'json': [], 'http_status': 200, 'text': None},
        'status': 'sent',
    }

    response = await pull(request_id='request2')
    assert response is not None
    assert response.status == 200
    assert await response.json() == {'status': 'new'}


async def test_taximeter_task_few_responses(
        taxi_billing_buffer_proxy_stq_context,
        pull,
        push,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
):
    patch_buffer_to_valid_partition(monkeypatch)
    await push(
        data={
            'request_id': 'request1',
            'request': {
                'foo': 'bar',
                'external_event_ref': 'external_event_ref1',
                'request_id': 'bar/external_event_ref1',
            },
        },
    )

    @patch_aiohttp_session(discovery.find_service('taximeter').url, 'post')
    def patch_send_request(*args, **kwargs):
        data = kwargs['json']
        assert len(data) == 1
        assert 'foo' in data[0]
        return response_mock(
            status=200,
            json=[
                {'request_id': 'bar/external_event_ref1', 'quas': 'wex'},
                {'request_id': 'bar/external_event_ref1', 'quas': 'exort'},
            ],
            text=None,
        )

    await stq_task.task(taxi_billing_buffer_proxy_stq_context, 'taximeter')

    assert len(patch_send_request.calls) == 1

    response = await pull(request_id='request1')
    assert response is not None
    assert response.status == 200
    assert await response.json() == {
        'status': 'sent',
        'response': {
            'http_status': 200,
            'json': [
                {'request_id': 'bar/external_event_ref1', 'quas': 'wex'},
                {'request_id': 'bar/external_event_ref1', 'quas': 'exort'},
            ],
            'text': None,
        },
    }


async def test_taximeter_task_partition(
        db,
        taxi_billing_buffer_proxy_stq_context,
        patch_aiohttp_session,
        response_mock,
):
    hex_letters = ['{:x}'.format(i) for i in range(16)]
    for i in hex_letters:
        await db.taximeter_buffer.insert(
            {
                '_id': '5a68200190e5d644b19b31c' + i,
                'request_id': i,
                'request': {'request_id': i},
                'status': 'new',
                'created_at': datetime.datetime.utcnow(),
            },
        )
    assert await db.taximeter_buffer.count() == 16

    for i in range(16):

        @patch_aiohttp_session(discovery.find_service('taximeter').url, 'post')
        def patch_send_request(*args, **kwargs):
            data = kwargs['json']
            assert len(data) == 1
            assert hex_letters[i] == data[0]['request_id']
            return response_mock(status=200, json=[], text=None)

        await stq_task.task(
            taxi_billing_buffer_proxy_stq_context,
            buffer_name='taximeter',
            partition_index=i,
        )
        assert len(patch_send_request.calls) == 1


@pytest.mark.config(
    BUFFER_PROXY_REQUESTS_SETTINGS={'__default__': 1, 'taximeter': 3},
)
async def test_taximeter_task_few_chunks(
        taxi_billing_buffer_proxy_stq_context,
        pull,
        push,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
):
    patch_buffer_to_valid_partition(monkeypatch)
    await push(
        data={
            'request_id': 'request1',
            'request': {
                'foo': 'bar',
                'external_event_ref': 'external_event_ref1',
                'request_id': 'bar/external_event_ref1',
            },
        },
    )
    await push(
        data={
            'request_id': 'request2',
            'request': {
                'foo': 'taz',
                'external_event_ref': 'external_event_ref2',
                'request_id': 'taz/external_event_ref2',
            },
        },
    )

    @patch_aiohttp_session(discovery.find_service('taximeter').url, 'post')
    def patch_send_request(*args, **kwargs):
        data = kwargs['json']
        assert len(data) == 1
        assert 'foo' in data[0]
        return response_mock(
            status=200,
            json=[{'request_id': 'taz/external_event_ref2', 'quas': 'wex'}],
            text=None,
        )

    await stq_task.task(taxi_billing_buffer_proxy_stq_context, 'taximeter')

    assert len(patch_send_request.calls) == 2

    response = await pull(request_id='request1')
    assert response is not None
    assert response.status == 200
    assert await response.json() == {
        'status': 'sent',
        'response': {'http_status': 200, 'json': [], 'text': None},
    }

    response = await pull(request_id='request2')
    assert response is not None
    assert response.status == 200
    assert await response.json() == {
        'status': 'sent',
        'response': {
            'http_status': 200,
            'json': [{'request_id': 'taz/external_event_ref2', 'quas': 'wex'}],
            'text': None,
        },
    }
