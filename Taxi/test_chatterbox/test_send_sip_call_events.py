# pylint: disable=unused-variable
import datetime

import pytest

from taxi import discovery
from taxi.clients import support_metrics

from chatterbox.crontasks import send_sip_call_events

NOW = datetime.datetime(2018, 5, 6, 12, 0, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'expected_request_data',
    [
        [
            {
                'events': [
                    {
                        'id': 'task_1_sip_call_0',
                        'created': '2018-05-06T04:22:33+0300',
                        'type': 'sip_call',
                        'payload': {
                            'action': 'failed_call',
                            'login': 'support_1',
                            'line': 'first',
                            'start_timestamp': None,
                        },
                    },
                    {
                        'id': 'task_1_sip_call_1',
                        'created': '2018-05-06T14:23:43+0300',
                        'type': 'sip_call',
                        'payload': {
                            'action': 'success_call',
                            'login': 'support_1',
                            'line': 'second',
                            'start_timestamp': '2018-05-06T11:22:43Z',
                        },
                    },
                    {
                        'id': 'task_1_sip_call_2',
                        'created': '2018-05-06T14:35:03+0300',
                        'type': 'sip_call',
                        'payload': {
                            'action': 'incoming_call',
                            'line': 'second',
                            'login': 'support_2',
                            'start_timestamp': '2018-05-06T11:32:43Z',
                        },
                    },
                    {
                        'id': 'task_2_sip_call_0',
                        'created': '2018-05-06T14:35:03+0300',
                        'type': 'sip_call',
                        'payload': {
                            'action': 'success_call',
                            'login': 'support_2',
                            'line': 'second',
                            'start_timestamp': '2018-05-06T11:32:43Z',
                        },
                    },
                    {
                        'id': 'task_2_sip_call_1',
                        'created': '2018-05-06T14:23:43+0300',
                        'type': 'sip_call',
                        'payload': {
                            'action': 'incoming_call',
                            'line': 'second',
                            'login': 'support_1',
                            'start_timestamp': '2018-05-06T11:22:43Z',
                        },
                    },
                    {
                        'id': 'task_3_sip_call_0',
                        'created': '2018-05-06T14:35:03+0300',
                        'type': 'sip_call',
                        'payload': {
                            'action': 'incoming_call',
                            'login': 'support_2',
                            'line': 'second',
                            'start_timestamp': '2018-05-06T11:32:43Z',
                        },
                    },
                    {
                        'id': 'task_3_sip_call_1',
                        'created': '2018-05-06T14:23:43+0300',
                        'type': 'sip_call',
                        'payload': {
                            'action': 'incoming_call',
                            'line': 'second',
                            'login': 'support_1',
                            'start_timestamp': '2018-05-06T11:22:43Z',
                        },
                    },
                ],
            },
            {
                'events': [
                    {
                        'id': 'task_1_sip_call_2',
                        'created': '2018-05-06T14:35:03+0300',
                        'type': 'sip_call',
                        'payload': {
                            'action': 'incoming_call',
                            'login': 'support_2',
                            'line': 'second',
                            'start_timestamp': '2018-05-06T11:32:43Z',
                        },
                    },
                    {
                        'id': 'task_2_sip_call_0',
                        'created': '2018-05-06T14:35:03+0300',
                        'type': 'sip_call',
                        'payload': {
                            'action': 'success_call',
                            'login': 'support_2',
                            'line': 'second',
                            'start_timestamp': '2018-05-06T11:32:43Z',
                        },
                    },
                    {
                        'id': 'task_3_sip_call_0',
                        'created': '2018-05-06T14:35:03+0300',
                        'type': 'sip_call',
                        'payload': {
                            'action': 'incoming_call',
                            'login': 'support_2',
                            'line': 'second',
                            'start_timestamp': '2018-05-06T11:32:43Z',
                        },
                    },
                ],
            },
        ],
    ],
)
@pytest.mark.config(
    CHATTERBOX_SEND_EVENTS_PARAMS={
        '__default__': {
            'enabled': True,
            'window': 86400,
            'delay': 15,
            'chunk_size': 1000,
        },
    },
)
async def test_send_sip_call_events(
        cbox_context,
        loop,
        response_mock,
        patch_aiohttp_session,
        expected_request_data,
):
    support_metrics_service = discovery.find_service('support_metrics')

    call_counter = 0

    # pylint: disable=unused-variable
    @patch_aiohttp_session(support_metrics_service.url, 'POST')
    def patch_request(method, url, **kwargs):
        nonlocal call_counter
        assert method == 'post'
        assert url == '%s/v1/bulk_process_event' % support_metrics_service.url
        kwargs['json']['events'] = sorted(
            kwargs['json']['events'], key=lambda d: d['id'],
        )
        assert kwargs['json'] == expected_request_data[call_counter]
        call_counter += 1
        return response_mock(json={})

    await send_sip_call_events.do_stuff(cbox_context, loop)

    await send_sip_call_events.do_stuff(cbox_context, loop)

    assert patch_request.calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'expected_request_data',
    [
        {
            'events': [
                {
                    'id': 'task_1_sip_call_0',
                    'created': '2018-05-06T04:22:33+0300',
                    'type': 'sip_call',
                    'payload': {
                        'action': 'failed_call',
                        'login': 'support_1',
                        'line': 'first',
                        'start_timestamp': None,
                    },
                },
                {
                    'id': 'task_1_sip_call_1',
                    'created': '2018-05-06T14:23:43+0300',
                    'type': 'sip_call',
                    'payload': {
                        'action': 'success_call',
                        'login': 'support_1',
                        'line': 'second',
                        'start_timestamp': '2018-05-06T11:22:43Z',
                    },
                },
                {
                    'id': 'task_1_sip_call_2',
                    'created': '2018-05-06T14:35:03+0300',
                    'type': 'sip_call',
                    'payload': {
                        'action': 'incoming_call',
                        'line': 'second',
                        'login': 'support_2',
                        'start_timestamp': '2018-05-06T11:32:43Z',
                    },
                },
                {
                    'id': 'task_2_sip_call_0',
                    'created': '2018-05-06T14:35:03+0300',
                    'type': 'sip_call',
                    'payload': {
                        'action': 'success_call',
                        'login': 'support_2',
                        'line': 'second',
                        'start_timestamp': '2018-05-06T11:32:43Z',
                    },
                },
                {
                    'id': 'task_2_sip_call_1',
                    'created': '2018-05-06T14:23:43+0300',
                    'type': 'sip_call',
                    'payload': {
                        'action': 'incoming_call',
                        'line': 'second',
                        'login': 'support_1',
                        'start_timestamp': '2018-05-06T11:22:43Z',
                    },
                },
                {
                    'id': 'task_3_sip_call_0',
                    'created': '2018-05-06T14:35:03+0300',
                    'type': 'sip_call',
                    'payload': {
                        'action': 'incoming_call',
                        'login': 'support_2',
                        'line': 'second',
                        'start_timestamp': '2018-05-06T11:32:43Z',
                    },
                },
                {
                    'id': 'task_3_sip_call_1',
                    'created': '2018-05-06T14:23:43+0300',
                    'type': 'sip_call',
                    'payload': {
                        'action': 'incoming_call',
                        'line': 'second',
                        'login': 'support_1',
                        'start_timestamp': '2018-05-06T11:22:43Z',
                    },
                },
            ],
        },
    ],
)
@pytest.mark.config(
    CHATTERBOX_SEND_EVENTS_PARAMS={
        '__default__': {
            'enabled': True,
            'window': 86400,
            'delay': 15,
            'chunk_size': 1000,
        },
    },
)
async def test_send_events_error(
        cbox_context,
        loop,
        response_mock,
        patch_aiohttp_session,
        expected_request_data,
):
    support_metrics_service = discovery.find_service('support_metrics')
    call_counter = 0

    @patch_aiohttp_session(support_metrics_service.url, 'POST')
    def patch_request(method, url, **kwargs):
        nonlocal call_counter
        assert method == 'post'
        assert url == '%s/v1/bulk_process_event' % support_metrics_service.url
        kwargs['json']['events'] = sorted(
            kwargs['json']['events'], key=lambda d: d['id'],
        )
        assert kwargs['json'] == expected_request_data
        if call_counter < 4:
            call_counter += 1
            return response_mock(status=500)
        return response_mock(json={})

    with pytest.raises(support_metrics.BaseError):
        await send_sip_call_events.do_stuff(cbox_context, loop)

    await send_sip_call_events.do_stuff(cbox_context, loop)
