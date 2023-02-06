# pylint: disable=invalid-name
import aiohttp

from taxi import discovery


async def test_client(
        taxi_billing_buffer_proxy_stq_context,
        taxi_billing_buffer_proxy_client,
        patch_aiohttp_session,
        response_mock,
        api_client,
):
    @patch_aiohttp_session(
        discovery.find_service('billing_buffer_proxy').url, 'post',
    )
    def patch_buffer_request(method, url, *args, **kwargs):
        # pylint: disable=no-else-return
        if 'push' in url:
            return response_mock(status=200, json={})
        elif 'poll' in url:
            return response_mock(
                status=200,
                json={
                    'status': 'sent',
                    'response': {
                        'http_status': 200,
                        'json': {
                            'request_id': 'transaction_id/event_ref',
                            'external_event_ref': 'event_ref',
                            'transaction_id': 'transaction_id',
                            'some_test_data': 'test_data',
                        },
                        'text': None,
                    },
                },
            )
        raise Exception(f'Unexpected url: {url}')

    response = await api_client.process_billing_events(
        kind='kind',
        transaction_id='transaction_id',
        event_at='2018-01-01T00:00:00',
        external_event_ref='event_ref',
        data={},
        request_id='transaction_id/event_ref',
    )
    assert len(patch_buffer_request.calls) == 2
    assert response == {
        'external_event_ref': 'event_ref',
        'transaction_id': 'transaction_id',
        'some_test_data': 'test_data',
        'request_id': 'transaction_id/event_ref',
    }


async def test_client_polls_few_times(
        taxi_billing_buffer_proxy_stq_context,
        taxi_billing_buffer_proxy_client,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        api_client,
):
    counter = 0

    @patch_aiohttp_session(
        discovery.find_service('billing_buffer_proxy').url, 'post',
    )
    def patch_send_request(method, url, *args, **kwargs):
        # pylint: disable=no-else-return
        nonlocal counter
        if 'push' in url:
            return response_mock(status=200, json={}, text=None)
        elif 'poll' in url:
            counter += 1
            if counter < 3:
                return response_mock(status=200, json={'status': 'new'})
            return response_mock(
                status=200,
                json={
                    'status': 'sent',
                    'response': {
                        'json': {
                            'request_id': 'transaction_id/event_ref',
                            'external_event_ref': 'event_ref',
                            'transaction_id': 'transaction_id',
                            'some_test_data': 'test_data',
                        },
                        'http_status': 200,
                        'text': None,
                    },
                },
            )
        raise Exception(f'Unexpected url: {url}')

    response = await api_client.process_billing_events(
        kind='kind',
        transaction_id='transaction_id',
        event_at='2018-01-01T00:00:00',
        external_event_ref='event_ref',
        data={},
        request_id='transaction_id/event_ref',
    )
    assert counter == 3
    assert len(patch_send_request.calls) == 4
    assert response == {
        'external_event_ref': 'event_ref',
        'transaction_id': 'transaction_id',
        'some_test_data': 'test_data',
        'request_id': 'transaction_id/event_ref',
    }


async def test_client_error(
        taxi_billing_buffer_proxy_stq_context,
        taxi_billing_buffer_proxy_client,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        api_client,
):
    @patch_aiohttp_session(
        discovery.find_service('billing_buffer_proxy').url, 'post',
    )
    def patch_send_request(method, url, *args, **kwargs):
        if 'push' in url:
            return response_mock(status=200, json={}, text=None)
        return response_mock(
            status=200,
            json={
                'status': 'sent',
                'response': {
                    'json': None,
                    'http_status': 400,
                    'text': 'Bad Request',
                },
            },
        )

    try:
        await api_client.process_billing_events(
            kind='kind',
            transaction_id='transaction_id',
            event_at='2018-01-01T00:00:00',
            external_event_ref='event_ref',
            data={},
            request_id='transaction_id/event_ref',
        )
    except aiohttp.ClientResponseError as exc:
        assert exc.code == 400
        assert exc.message == 'Bad Request'
    else:
        assert False and 'Must throw'
    assert len(patch_send_request.calls) == 2
