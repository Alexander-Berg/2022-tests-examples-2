import pytest

from taxi.clients import startrack

from taxi_approvals import settings as approvals_settings
from taxi_approvals.generated.cron import run_cron

ST_URL = approvals_settings.STARTREK_API_URL


EXPECTED_CALLS = [
    {'body': {}, 'params': {}, 'url': 'myself'},
    {
        'url': 'issues/_search',
        'params': {'page': 1, 'perPage': 100},
        'body': {
            'filter': {
                'tags': 'approvals_created_ticket',
                'resolution': 'empty()',
            },
        },
    },
    {
        'body': {
            'resolution': 'won\'tFix',
            'comment': 'Ticket seems to be forgotten and closed by robot',
        },
        'params': {},
        'url': 'issues/RUPRICING-5729/transitions/close/_execute',
    },
    {
        'body': {
            'resolution': 'fixed',
            'comment': 'Ticket seems to be forgotten and closed by robot',
        },
        'params': {},
        'url': 'issues/RUPRICING-5729/transitions/close/_execute',
    },
    {
        'body': {},
        'params': {'perPage': 250},
        'url': 'issues/RUPRICING-5729/comments',
    },
    {
        'body': {'summonees': []},
        'params': {},
        'url': 'issues/RUPRICING-5729/comments/60081a43a09f60468b70c787',
    },
    {
        'body': {
            'filter': {
                'resolution': 'empty()',
                'tags': 'approvals_created_ticket',
            },
        },
        'params': {'page': 2, 'perPage': 100},
        'url': 'issues/_search',
    },
    {
        'body': {
            'resolution': 'won\'tFix',
            'comment': 'Ticket seems to be forgotten and closed by robot',
        },
        'params': {},
        'url': 'issues/RUPRICING-5727/transitions/close/_execute',
    },
    {
        'body': {},
        'params': {'perPage': 250},
        'url': 'issues/RUPRICING-5727/comments',
    },
    {
        'body': {'summonees': []},
        'params': {},
        'url': 'issues/RUPRICING-5727/comments/60081a43a09f60468b70c787',
    },
    {
        'body': {
            'resolution': 'won\'tFix',
            'comment': 'Ticket seems to be forgotten and closed by robot',
        },
        'params': {},
        'url': 'issues/TAXIADMIN-73/transitions/close/_execute',
    },
    {
        'body': {},
        'params': {'perPage': 250},
        'url': 'issues/TAXIADMIN-73/comments',
    },
    {
        'body': {'summonees': []},
        'params': {},
        'url': 'issues/TAXIADMIN-73/comments/60081a43a09f60468b70c787',
    },
    {
        'body': {
            'filter': {
                'resolution': 'empty()',
                'tags': 'approvals_created_ticket',
            },
        },
        'params': {'page': 3, 'perPage': 100},
        'url': 'issues/_search',
    },
]


@pytest.mark.config(
    APPROVALS_FORGOTTEN_TICKETS_WATCHER={
        'enabled': True,
        'ignore_queues': [],
        'resolutions_by_order': ['won\'tFix', 'fixed'],
        'max_request_count': 10,
        'page_size': 100,
        'time_sleep_sec': 0.01,
    },
)
@pytest.mark.pgsql('approvals', files=['init_data.sql'])
async def test_forgotten_tickets_watcher(approvals_cron_app, patch, load_json):
    @patch('taxi.clients.startrack.StartrackAPIClient._request')
    async def _request(url, *_args, **kwargs):
        params = kwargs.get('params')
        body = kwargs.get('json')
        if url == 'issues/_search':
            if params['page'] == 1:
                return load_json('first_response.json')
            if params['page'] == 2:
                return load_json('second_response.json')
            return []
        if url == 'issues/RUPRICING-5729/transitions/close/_execute':
            if body['resolution'] != 'fixed':
                raise startrack.BaseError('Not fixed')
        if '/transitions/close/_execute' in url:
            return {}
        if url == 'myself':
            return {'login': 'karachevda'}
        if url.endswith('comments'):
            return load_json('comments.json')
        if '/comments/' in url:
            return {}
        raise NotImplementedError(f'Unexpected request: {url}')

    await run_cron.main(
        ['taxi_approvals.stuff.forgotten_tickets_watcher', '-t', '0'],
    )
    calls = _request.calls
    assert len(calls) == 14
    formatted_calls = [
        {
            'url': call['url'],
            'params': call['kwargs'].get('params', {}),
            'body': call['kwargs'].get('json', {}),
        }
        for call in calls
    ]
    assert formatted_calls == EXPECTED_CALLS
