import datetime

import pytest

from taxi import discovery

from chatterbox.crontasks import send_supporter_statuses


@pytest.mark.now(datetime.datetime(2019, 8, 13, 12, 0, 0).isoformat())
@pytest.mark.parametrize(
    'expected_request_data',
    [
        (
            {
                'events': [
                    {
                        'id': (
                            'supporter_status'
                            '_f7ae5ee66d8a5907c6fc9a9e2e2d215ea4adfe7e'
                        ),
                        'created': '2019-08-13T15:00:00+0300',
                        'type': 'supporter_status',
                        'payload': {
                            'status': 'online',
                            'login': 'user_1',
                            'lines': ['first'],
                            'projects': ['taxi'],
                            'in_addition': False,
                            'start_timestamp': '2019-08-13T14:49:25+0300',
                            'finish_timestamp': '2019-08-13T15:00:00+0300',
                        },
                    },
                    {
                        'id': (
                            'supporter_status'
                            '_cbfd7accce5c2c80595103c8948994a56c358655'
                        ),
                        'created': '2019-08-13T15:00:00+0300',
                        'type': 'supporter_status',
                        'payload': {
                            'status': 'online',
                            'login': 'user_2',
                            'lines': ['first', 'second'],
                            'projects': ['taxi'],
                            'in_addition': True,
                            'start_timestamp': '2019-08-13T02:55:00+0300',
                            'finish_timestamp': '2019-08-13T03:00:00+0300',
                        },
                    },
                    {
                        'id': (
                            'supporter_status'
                            '_2d248dccdddd774dc54c5c21db8bbf524dda48ad'
                        ),
                        'created': '2019-08-13T15:00:00+0300',
                        'type': 'supporter_status',
                        'payload': {
                            'status': 'online',
                            'login': 'user_2',
                            'lines': ['first', 'second'],
                            'projects': ['taxi'],
                            'in_addition': True,
                            'start_timestamp': '2019-08-13T03:00:00+0300',
                            'finish_timestamp': '2019-08-13T15:00:00+0300',
                        },
                    },
                    {
                        'id': (
                            'supporter_status'
                            '_4eaa9e91e4b8b61fa5a6090d4a99632f3a8d78cf'
                        ),
                        'created': '2019-08-13T15:00:00+0300',
                        'type': 'supporter_status',
                        'payload': {
                            'status': 'offline',
                            'login': 'user_3',
                            'lines': ['first'],
                            'projects': ['taxi'],
                            'in_addition': False,
                            'start_timestamp': '2019-08-13T13:00:00+0300',
                            'finish_timestamp': '2019-08-13T15:00:00+0300',
                        },
                    },
                ],
            }
        ),
    ],
)
async def test_send_supporter_statuses(
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
        assert url == '%s/v1/bulk_process_event' % support_metrics_service.url
        kwargs['json']['events'] = sorted(
            kwargs['json']['events'], key=lambda d: d['created'],
        )
        assert kwargs['json'] == expected_request_data
        return response_mock(json={})

    await send_supporter_statuses.do_stuff(cbox_context, loop)
