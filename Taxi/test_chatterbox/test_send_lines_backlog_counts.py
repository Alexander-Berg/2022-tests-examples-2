import pytest

from taxi import discovery

from chatterbox.crontasks import send_lines_backlog_counts


@pytest.mark.config(
    CHATTERBOX_SEND_EVENTS_PARAMS={
        'chatterbox_line_backlog': {
            'enabled': True,
            'window': 60,
            'delay': 60,
            'chunk_size': 100,
        },
    },
    CHATTERBOX_LINES={
        'eda_first': {
            'name': 'Первая линия Еды',
            'types': ['client_eats'],
            'projects': ['eats'],
        },
        'first': {
            'name': 'Первая линия',
            'autoreply': True,
            'projects': ['taxi'],
        },
        'urgent': {'name': 'Ургент', 'mode': 'offline'},
    },
)
@pytest.mark.now('2019-11-13T12:00:00')
@pytest.mark.parametrize(
    'expected_request_data',
    [
        (
            {
                'events': [
                    {
                        'id': 'eda_first_accepted_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'eda_first',
                            'projects': ['eats'],
                            'status': 'accepted',
                            'count': 0,
                        },
                    },
                    {
                        'id': (
                            'eda_first_autoreply_in_progress_2019-11-13T'
                            '12:00:00UTC'
                        ),
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'eda_first',
                            'projects': ['eats'],
                            'status': 'autoreply_in_progress',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'eda_first_deferred_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'eda_first',
                            'projects': ['eats'],
                            'status': 'deferred',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'eda_first_forwarded_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'eda_first',
                            'projects': ['eats'],
                            'status': 'forwarded',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'eda_first_in_progress_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'eda_first',
                            'projects': ['eats'],
                            'status': 'in_progress',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'eda_first_new_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'eda_first',
                            'projects': ['eats'],
                            'status': 'new',
                            'count': 1,
                        },
                    },
                    {
                        'id': 'eda_first_offered_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'eda_first',
                            'projects': ['eats'],
                            'status': 'offered',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'eda_first_predispatch_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'eda_first',
                            'projects': ['eats'],
                            'status': 'predispatch',
                            'count': 0,
                        },
                    },
                    {
                        'id': (
                            'eda_first_ready_to_offer_2019-11-13T12:00:00UTC'
                        ),
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'eda_first',
                            'projects': ['eats'],
                            'status': 'ready_to_offer',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'eda_first_reopened_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'eda_first',
                            'projects': ['eats'],
                            'status': 'reopened',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'eda_first_routing_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'eda_first',
                            'projects': ['eats'],
                            'status': 'routing',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'eda_first_waiting_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'eda_first',
                            'projects': ['eats'],
                            'status': 'waiting',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'first_accepted_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'accepted',
                            'count': 0,
                        },
                    },
                    {
                        'id': (
                            'first_autoreply_in_progress_2019-11-13T'
                            '12:00:00UTC'
                        ),
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'autoreply_in_progress',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'first_deferred_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'deferred',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'first_forwarded_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'forwarded',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'first_in_progress_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'in_progress',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'first_new_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'new',
                            'count': 2,
                        },
                    },
                    {
                        'id': 'first_offered_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'offered',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'first_predispatch_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'predispatch',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'first_ready_to_offer_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'ready_to_offer',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'first_reopened_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'reopened',
                            'count': 1,
                        },
                    },
                    {
                        'id': 'first_routing_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'routing',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'first_waiting_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'first',
                            'projects': ['taxi'],
                            'status': 'waiting',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'urgent_accepted_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'urgent',
                            'projects': ['taxi'],
                            'status': 'accepted',
                            'count': 0,
                        },
                    },
                    {
                        'id': (
                            'urgent_autoreply_in_progress_2019-11-13T'
                            '12:00:00UTC'
                        ),
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'urgent',
                            'projects': ['taxi'],
                            'status': 'autoreply_in_progress',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'urgent_deferred_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'urgent',
                            'projects': ['taxi'],
                            'status': 'deferred',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'urgent_forwarded_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'urgent',
                            'projects': ['taxi'],
                            'status': 'forwarded',
                            'count': 1,
                        },
                    },
                    {
                        'id': 'urgent_in_progress_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'urgent',
                            'projects': ['taxi'],
                            'status': 'in_progress',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'urgent_new_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'urgent',
                            'projects': ['taxi'],
                            'status': 'new',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'urgent_offered_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'urgent',
                            'projects': ['taxi'],
                            'status': 'offered',
                            'count': 1,
                        },
                    },
                    {
                        'id': 'urgent_predispatch_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'urgent',
                            'projects': ['taxi'],
                            'status': 'predispatch',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'urgent_ready_to_offer_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'urgent',
                            'projects': ['taxi'],
                            'status': 'ready_to_offer',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'urgent_reopened_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'urgent',
                            'projects': ['taxi'],
                            'status': 'reopened',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'urgent_routing_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'urgent',
                            'projects': ['taxi'],
                            'status': 'routing',
                            'count': 0,
                        },
                    },
                    {
                        'id': 'urgent_waiting_2019-11-13T12:00:00UTC',
                        'type': 'chatterbox_line_backlog',
                        'created': '2019-11-13T15:00:00+0300',
                        'payload': {
                            'line': 'urgent',
                            'projects': ['taxi'],
                            'status': 'waiting',
                            'count': 0,
                        },
                    },
                ],
            }
        ),
    ],
)
async def test_send_lines_backlog_counts(
        cbox_context,
        loop,
        response_mock,
        patch_aiohttp_session,
        expected_request_data,
):
    support_metrics_service = discovery.find_service('support_metrics')

    @patch_aiohttp_session(support_metrics_service.url, 'POST')
    def _patch_request(method, url, **kwargs):
        assert method == 'post'
        assert url == '{0}/v1/bulk_process_event'.format(
            support_metrics_service.url,
        )
        kwargs['json']['events'] = sorted(
            kwargs['json']['events'], key=lambda d: d['id'],
        )
        assert kwargs['json'] == expected_request_data
        return response_mock(json={})

    await send_lines_backlog_counts.do_stuff(cbox_context, loop)


@pytest.mark.parametrize('chunk, calls_number', [(10, 1), (1, 3)])
async def test_num_of_calls(
        cbox_context,
        loop,
        response_mock,
        patch_aiohttp_session,
        chunk,
        calls_number,
):
    config = cbox_context.data.config.CHATTERBOX_SEND_EVENTS_PARAMS
    config['chatterbox_line_backlog'] = {'chunk_size': chunk}
    support_metrics_service = discovery.find_service('support_metrics')

    @patch_aiohttp_session(support_metrics_service.url, 'POST')
    def _patch_request(method, url, **kwargs):
        return response_mock(json={})

    await send_lines_backlog_counts.do_stuff(cbox_context, loop)
    assert len(_patch_request.calls) == calls_number
