import pytest

from clowny_gideon.lib.components import gideon_client


@pytest.mark.usefixtures('clown_cache_mocks')
@pytest.mark.parametrize(
    'gideon_response_json, events_files',
    [
        ('gideon_response.json', ['/dev/tty']),
        ('gideon_response_no_events.json', []),
    ],
)
async def test_get_open_at_events(
        load_json,
        mock_gideon,
        cron_context,
        gideon_response_json,
        events_files,
):
    @mock_gideon('/api/query')
    def _handler(request):
        return load_json(gideon_response_json)

    client = gideon_client.Client(cron_context)
    events = await client.get_open_at_events('taxi%', '-1h')
    assert [str(x.filename) for x in events] == events_files
    call = _handler.next_call()
    assert call['request'].json == {
        'filter': [
            {'key': 'kind', 'operator': '==', 'values': ['OpenAt']},
            {'key': 'time', 'operator': '>=', 'values': ['-1h']},
            {'key': 'pod_set_id', 'operator': '~=', 'values': ['taxi%']},
        ],
    }
    assert not _handler.has_calls
