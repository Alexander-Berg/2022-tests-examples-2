import pytest

from taxi.clients import startrack

from taxi_approvals import queries
from taxi_approvals import settings as approvals_settings
from taxi_approvals.generated.cron import run_cron

ST_URL = approvals_settings.STARTREK_API_URL


@pytest.mark.config(
    APPROVALS_PROCESS_ERRORS={
        'enabled': True,
        'dry_run': False,
        'queue': 'DRAFTERRORS',
        'headers': ['Date', 'X-YaRequestId', 'X-YaSpanId', 'X-YaTraceId'],
        'service_settings': {
            '__default__': {
                '__default__': {
                    'enabled': True,
                    'denied_types': [],
                    'denied_status_codes': [],
                },
            },
        },
    },
)
@pytest.mark.pgsql('approvals', files=['init_data.sql'])
async def test_process_drafts(approvals_cron_app, patch, load_json):
    @patch('taxi.clients.startrack.StartrackAPIClient._request')
    async def _request(url, *_args, **kwargs):
        if url == 'issues':
            return {'key': 'TESTKEY-1'}
        if url == 'issues/_findByUnique':
            raise startrack.NotFoundError()
        if url == 'issues/TESTKEY-1/comments':
            if kwargs['method'] == 'GET':
                return [{'text': 'test_text'}]
            return {}
        raise NotImplementedError('Unexpected request')

    await run_cron.main(['taxi_approvals.stuff.process_errors', '-t', '0'])
    calls = _request.calls
    assert len(calls) == 12
    expected_calls = load_json('calls.json')
    for i, call in enumerate(expected_calls):
        if call['url'] == 'issues':
            assert calls[i]['kwargs']['json'].pop('description')
        assert calls[i]['url'] == call['url']
        assert calls[i]['kwargs'] == call['kwargs']

    pool = approvals_cron_app['pool']
    async with pool.acquire() as connection:
        result = await connection.fetch(queries.GET_UNPROCESSED_ERRORS)
        assert not result
