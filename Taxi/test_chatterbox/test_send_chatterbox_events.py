import datetime

import pytest

from taxi import discovery
from taxi.clients import support_metrics

from chatterbox.crontasks import send_chatterbox_events

NOW = datetime.datetime(2019, 6, 24, 9, 0, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'expected_request_data',
    [
        (
            [
                {
                    'events': [
                        {
                            'id': 'task_1_0',
                            'created': '2019-06-24T11:59:01+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': 'task_1',
                                'action': 'update_meta',
                                'login': 'superuser',
                                'line': 'first',
                                'in_addition': False,
                            },
                        },
                        {
                            'id': 'task_1_1',
                            'created': '2019-06-24T11:59:14+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': 'task_1',
                                'action': 'offer',
                                'login': 'admin1',
                                'line': 'first',
                                'in_addition': False,
                                'ready_to_send_at': '2019-06-24T12:00:00+0300',
                            },
                        },
                        {
                            'id': 'task_1_2',
                            'created': '2019-06-24T11:59:28+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': 'task_1',
                                'action': 'take',
                                'login': 'admin1',
                                'line': 'first',
                                'in_addition': False,
                            },
                        },
                        {
                            'id': 'task_2_1',
                            'created': '2019-06-24T11:59:29+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': 'task_2',
                                'action': 'forward',
                                'login': 'admin2',
                                'line': 'second',
                                'new_line': 'corp',
                                'in_addition': False,
                            },
                        },
                    ],
                },
                {
                    'events': [
                        {
                            'id': 'task_1_2',
                            'created': '2019-06-24T11:59:28+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': 'task_1',
                                'action': 'take',
                                'login': 'admin1',
                                'line': 'first',
                                'in_addition': False,
                            },
                        },
                        {
                            'id': 'task_2_1',
                            'created': '2019-06-24T11:59:29+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': 'task_2',
                                'action': 'forward',
                                'login': 'admin2',
                                'line': 'second',
                                'new_line': 'corp',
                                'in_addition': False,
                            },
                        },
                        {
                            'id': 'task_3_0',
                            'created': '2019-06-24T12:00:10+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': 'task_3',
                                'action': 'dismiss',
                                'login': 'admin2',
                                'line': 'first',
                                'in_addition': False,
                            },
                        },
                        {
                            'id': '5b2cae5cb2682a976914c2a2_0',
                            'created': '2019-06-24T12:00:10+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': '5b2cae5cb2682a976914c2a2',
                                'action': 'comment',
                                'in_addition': False,
                                'line': 'corp',
                                'login': 'superuser',
                            },
                        },
                        {
                            'id': '5b2cae5cb2682a976914c2a2_0_line_sla_fail',
                            'created': '2019-06-24T12:00:10+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': '5b2cae5cb2682a976914c2a2',
                                'action': 'line_sla_fail',
                                'in_addition': False,
                                'line': 'corp',
                                'login': 'superuser',
                            },
                        },
                        {
                            'id': (
                                '5b2cae5cb2682a976914c2a2_0_'
                                'supporter_sla_success'
                            ),
                            'created': '2019-06-24T12:00:10+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': '5b2cae5cb2682a976914c2a2',
                                'action': 'supporter_sla_success',
                                'in_addition': False,
                                'line': 'corp',
                                'login': 'superuser',
                            },
                        },
                        {
                            'id': '5b2cae5cb2682a976914c2a2_0_first_answer',
                            'type': 'chatterbox_action',
                            'created': '2019-06-24T12:00:10+0300',
                            'payload': {
                                'task_id': '5b2cae5cb2682a976914c2a2',
                                'action': 'first_answer',
                                'login': 'superuser',
                                'line': 'corp',
                                'in_addition': False,
                                'start_timestamp': '2019-06-24T11:59:50+0300',
                            },
                        },
                        {
                            'id': (
                                '5b2cae5cb2682a976914c2a2_0_'
                                'first_answer_in_line'
                            ),
                            'type': 'chatterbox_action',
                            'created': '2019-06-24T12:00:10+0300',
                            'payload': {
                                'task_id': '5b2cae5cb2682a976914c2a2',
                                'action': 'first_answer_in_line',
                                'login': 'superuser',
                                'line': 'corp',
                                'in_addition': False,
                                'start_timestamp': '2019-06-24T11:59:50+0300',
                            },
                        },
                        {
                            'created': '2019-06-24T12:00:10+0300',
                            'id': '5b2cae5cb2682a976914c2a3_0',
                            'payload': {
                                'action': 'comment',
                                'in_addition': False,
                                'task_id': '5b2cae5cb2682a976914c2a3',
                                'line': 'corp',
                                'login': 'superuser',
                            },
                            'type': 'chatterbox_action',
                        },
                        {
                            'created': '2019-06-24T12:00:10+0300',
                            'id': (
                                '5b2cae5cb2682a976914c2a3_0_'
                                'line_sla_success'
                            ),
                            'payload': {
                                'action': 'line_sla_success',
                                'in_addition': False,
                                'task_id': '5b2cae5cb2682a976914c2a3',
                                'line': 'corp',
                                'login': 'superuser',
                            },
                            'type': 'chatterbox_action',
                        },
                        {
                            'created': '2019-06-24T12:00:10+0300',
                            'id': '5b2cae5cb2682a976914c2a4_0',
                            'payload': {
                                'action': 'assign',
                                'in_addition': False,
                                'task_id': '5b2cae5cb2682a976914c2a4',
                                'line': 'corp',
                                'login': 'superuser',
                            },
                            'type': 'chatterbox_action',
                        },
                        {
                            'created': '2019-06-24T12:00:10+0300',
                            'id': '5b2cae5cb2682a976914c2a4_0_first_accept',
                            'payload': {
                                'action': 'first_accept',
                                'in_addition': False,
                                'task_id': '5b2cae5cb2682a976914c2a4',
                                'line': 'corp',
                                'login': 'superuser',
                            },
                            'type': 'chatterbox_action',
                        },
                        {
                            'created': '2019-06-24T12:00:10+0300',
                            'id': '5b2cae5cb2682a976914c2a4_1',
                            'payload': {
                                'action': 'comment',
                                'in_addition': False,
                                'task_id': '5b2cae5cb2682a976914c2a4',
                                'line': 'corp',
                                'login': 'superuser',
                            },
                            'type': 'chatterbox_action',
                        },
                        {
                            'id': '5b2cae5cb2682a976914c2a4_1_first_answer',
                            'type': 'chatterbox_action',
                            'created': '2019-06-24T12:00:10+0300',
                            'payload': {
                                'task_id': '5b2cae5cb2682a976914c2a4',
                                'action': 'first_answer',
                                'login': 'superuser',
                                'line': 'corp',
                                'in_addition': False,
                                'start_timestamp': '2019-06-24T11:59:50+0300',
                            },
                        },
                        {
                            'id': (
                                '5b2cae5cb2682a976914c2a4_1_'
                                'first_answer_in_line'
                            ),
                            'type': 'chatterbox_action',
                            'created': '2019-06-24T12:00:10+0300',
                            'payload': {
                                'task_id': '5b2cae5cb2682a976914c2a4',
                                'action': 'first_answer_in_line',
                                'login': 'superuser',
                                'line': 'corp',
                                'in_addition': False,
                                'start_timestamp': '2019-06-24T11:59:50+0300',
                            },
                        },
                        {
                            'created': '2019-06-24T12:00:10+0300',
                            'id': '5b2cae5cb2682a976914c2a4_2',
                            'payload': {
                                'action': 'close',
                                'in_addition': False,
                                'task_id': '5b2cae5cb2682a976914c2a4',
                                'line': 'corp',
                                'login': 'superuser',
                            },
                            'type': 'chatterbox_action',
                        },
                        {
                            'id': 'task_1_3',
                            'created': '2019-06-24T12:00:13+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': 'task_1',
                                'action': 'comment',
                                'login': 'admin1',
                                'line': 'first',
                                'in_addition': True,
                            },
                        },
                        {
                            'id': 'task_1_3_first_answer',
                            'created': '2019-06-24T12:00:13+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': 'task_1',
                                'action': 'first_answer',
                                'login': 'admin1',
                                'line': 'first',
                                'in_addition': True,
                                'start_timestamp': '2019-06-24T11:58:13+0300',
                            },
                        },
                        {
                            'id': 'task_1_3_first_answer_in_line',
                            'created': '2019-06-24T12:00:13+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': 'task_1',
                                'action': 'first_answer_in_line',
                                'login': 'admin1',
                                'line': 'first',
                                'in_addition': True,
                                'start_timestamp': '2019-06-24T11:58:13+0300',
                            },
                        },
                        {
                            'id': 'task_1_3_online_chat_processing',
                            'created': '2019-06-24T12:00:13+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': 'task_1',
                                'action': 'online_chat_processing',
                                'login': 'admin1',
                                'line': 'first',
                                'in_addition': True,
                                'start_timestamp': '2019-06-24T11:56:13+0300',
                            },
                        },
                        {
                            'id': 'task_1_3_speed_answer',
                            'created': '2019-06-24T12:00:13+0300',
                            'type': 'chatterbox_action',
                            'payload': {
                                'task_id': 'task_1',
                                'action': 'speed_answer',
                                'login': 'admin1',
                                'line': 'first',
                                'in_addition': True,
                                'start_timestamp': '2019-06-24T11:56:20+0300',
                            },
                        },
                    ],
                },
            ]
        ),
    ],
)
@pytest.mark.config(
    CHATTERBOX_SEND_EVENTS_PARAMS={
        '__default__': {
            'enabled': True,
            'window': 60,
            'delay': 15,
            'chunk_size': 1000,
        },
    },
)
async def test_send_chatterbox_events(
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
            kwargs['json']['events'], key=lambda d: d['created'],
        )
        assert kwargs['json'] == expected_request_data[call_counter]
        call_counter += 1
        return response_mock(json={})

    await send_chatterbox_events.do_stuff(cbox_context, loop)

    await send_chatterbox_events.do_stuff(cbox_context, loop)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'expected_request_data',
    [
        (
            {
                'events': [
                    {
                        'id': 'task_1_0',
                        'created': '2019-06-24T11:59:01+0300',
                        'type': 'chatterbox_action',
                        'payload': {
                            'task_id': 'task_1',
                            'action': 'update_meta',
                            'login': 'superuser',
                            'line': 'first',
                            'in_addition': False,
                        },
                    },
                    {
                        'id': 'task_1_1',
                        'created': '2019-06-24T11:59:14+0300',
                        'type': 'chatterbox_action',
                        'payload': {
                            'task_id': 'task_1',
                            'action': 'offer',
                            'login': 'admin1',
                            'line': 'first',
                            'in_addition': False,
                            'ready_to_send_at': '2019-06-24T12:00:00+0300',
                        },
                    },
                    {
                        'id': 'task_1_2',
                        'created': '2019-06-24T11:59:28+0300',
                        'type': 'chatterbox_action',
                        'payload': {
                            'task_id': 'task_1',
                            'action': 'take',
                            'login': 'admin1',
                            'line': 'first',
                            'in_addition': False,
                        },
                    },
                    {
                        'id': 'task_2_1',
                        'created': '2019-06-24T11:59:29+0300',
                        'type': 'chatterbox_action',
                        'payload': {
                            'task_id': 'task_2',
                            'action': 'forward',
                            'login': 'admin2',
                            'line': 'second',
                            'new_line': 'corp',
                            'in_addition': False,
                        },
                    },
                ],
            }
        ),
    ],
)
@pytest.mark.config(
    CHATTERBOX_SEND_EVENTS_PARAMS={
        '__default__': {
            'enabled': True,
            'window': 60,
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

    # pylint: disable=unused-variable
    @patch_aiohttp_session(support_metrics_service.url, 'POST')
    def patch_request(method, url, **kwargs):
        nonlocal call_counter
        assert method == 'post'
        assert url == '%s/v1/bulk_process_event' % support_metrics_service.url
        kwargs['json']['events'] = sorted(
            kwargs['json']['events'], key=lambda d: d['created'],
        )
        assert kwargs['json'] == expected_request_data
        if call_counter < 4:
            call_counter += 1
            return response_mock(status=500)
        return response_mock(json={})

    with pytest.raises(support_metrics.BaseError):
        await send_chatterbox_events.do_stuff(cbox_context, loop)

    await send_chatterbox_events.do_stuff(cbox_context, loop)
