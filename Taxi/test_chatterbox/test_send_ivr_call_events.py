# pylint: disable=unused-variable
import datetime

import pytest

from taxi import discovery

from chatterbox.crontasks import send_ivr_call_events

NOW = datetime.datetime(2018, 5, 6, 12, 0, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'expected_request_data',
    [
        [
            {
                'events': [
                    {
                        'created': '2018-05-05T15:34:56+0300',
                        'id': 'task_1_ivr_call_0',
                        'payload': {
                            'action': 'missed_call',
                            'answered_timestamp': None,
                            'completed_timestamp': '2018-05-06T01:22:33Z',
                            'line': 'first',
                            'start_timestamp': '2018-05-05T12:34:56+0000',
                        },
                        'type': 'ivr_call',
                    },
                    {
                        'created': '2018-05-05T15:34:56+0300',
                        'id': 'task_1_ivr_call_1',
                        'payload': {
                            'action': 'success_call',
                            'answered_timestamp': '2018-05-06T11:22:43Z',
                            'completed_timestamp': '2018-05-06T11:23:43Z',
                            'line': 'second',
                            'start_timestamp': '2018-05-05T12:34:56+0000',
                        },
                        'type': 'ivr_call',
                    },
                    {
                        'created': '2018-05-05T15:34:56+0300',
                        'id': 'task_1_ivr_call_2',
                        'payload': {
                            'action': 'success_call',
                            'answered_timestamp': '2018-05-06T11:32:43Z',
                            'completed_timestamp': '2018-05-06T11:35:03Z',
                            'line': 'second',
                            'start_timestamp': '2018-05-05T12:34:56+0000',
                        },
                        'type': 'ivr_call',
                    },
                    {
                        'created': '2018-05-05T15:34:56+0300',
                        'id': 'task_2_ivr_call_0',
                        'payload': {
                            'action': 'success_call',
                            'answered_timestamp': '2018-05-06T11:32:43Z',
                            'completed_timestamp': '2018-05-06T11:35:03Z',
                            'line': 'second',
                            'start_timestamp': '2018-05-05T12:34:56+0000',
                        },
                        'type': 'ivr_call',
                    },
                    {
                        'created': '2018-05-05T15:34:56+0300',
                        'id': 'task_2_ivr_call_1',
                        'payload': {
                            'action': 'success_call',
                            'answered_timestamp': '2018-05-06T11:22:43Z',
                            'completed_timestamp': '2018-05-06T11:23:43Z',
                            'line': 'second',
                            'start_timestamp': '2018-05-05T12:34:56+0000',
                        },
                        'type': 'ivr_call',
                    },
                    {
                        'created': '2018-05-05T15:34:56+0300',
                        'id': 'task_3_ivr_call_0',
                        'payload': {
                            'action': 'success_call',
                            'answered_timestamp': '2018-05-06T11:32:43Z',
                            'completed_timestamp': '2018-05-06T11:35:03Z',
                            'line': 'second',
                            'start_timestamp': '2018-05-05T12:34:56+0000',
                        },
                        'type': 'ivr_call',
                    },
                    {
                        'created': '2018-05-05T15:34:56+0300',
                        'id': 'task_3_ivr_call_1',
                        'payload': {
                            'action': 'success_call',
                            'answered_timestamp': '2018-05-06T11:22:43Z',
                            'completed_timestamp': '2018-05-06T11:23:43Z',
                            'line': 'second',
                            'start_timestamp': '2018-05-05T12:34:56+0000',
                        },
                        'type': 'ivr_call',
                    },
                ],
            },
            {
                'events': [
                    {
                        'created': '2018-05-05T15:34:56+0300',
                        'id': 'task_1_ivr_call_2',
                        'payload': {
                            'action': 'success_call',
                            'answered_timestamp': '2018-05-06T11:32:43Z',
                            'completed_timestamp': '2018-05-06T11:35:03Z',
                            'line': 'second',
                            'start_timestamp': '2018-05-05T12:34:56+0000',
                        },
                        'type': 'ivr_call',
                    },
                    {
                        'created': '2018-05-05T15:34:56+0300',
                        'id': 'task_2_ivr_call_0',
                        'payload': {
                            'action': 'success_call',
                            'answered_timestamp': '2018-05-06T11:32:43Z',
                            'completed_timestamp': '2018-05-06T11:35:03Z',
                            'line': 'second',
                            'start_timestamp': '2018-05-05T12:34:56+0000',
                        },
                        'type': 'ivr_call',
                    },
                    {
                        'created': '2018-05-05T15:34:56+0300',
                        'id': 'task_3_ivr_call_0',
                        'payload': {
                            'action': 'success_call',
                            'answered_timestamp': '2018-05-06T11:32:43Z',
                            'completed_timestamp': '2018-05-06T11:35:03Z',
                            'line': 'second',
                            'start_timestamp': '2018-05-05T12:34:56+0000',
                        },
                        'type': 'ivr_call',
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
async def test_send_ivr_call_events(
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

    await send_ivr_call_events.do_stuff(cbox_context, loop)

    await send_ivr_call_events.do_stuff(cbox_context, loop)

    assert patch_request.calls
