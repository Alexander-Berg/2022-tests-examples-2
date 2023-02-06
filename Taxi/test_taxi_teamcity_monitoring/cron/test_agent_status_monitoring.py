from typing import NamedTuple

from aiohttp import web
import pytest

import juggler_client

from taxi_teamcity_monitoring.generated.cron import run_cron


class Params(NamedTuple):
    teamcity_api_response_file: str
    juggler_response_file: str


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                teamcity_api_response_file='tc_response.json',
                juggler_response_file='juggler_calls.json',
            ),
            id='normal-work',
        ),
        pytest.param(
            Params(
                teamcity_api_response_file='tc_response_broken_agent.json',
                juggler_response_file='juggler_calls_broken_agent.json',
            ),
            id='broken-agent',
        ),
    ],
)
async def test_agent_status_monitoring(
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        load_json,
        mock_teamcity,
        params,
):
    @mock_teamcity('/app/rest/agents', prefix=True)
    def teamcity_request(request):
        return web.json_response(
            data=load_json(params.teamcity_api_response_file),
        )

    events_json = None

    @patch_aiohttp_session(juggler_client.juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events_json
        events_json = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'agent_status_monitoring.run_agent_status_monitoring',
            '-t',
            '0',
            '--debug',
        ],
    )

    assert teamcity_request.has_calls
    assert teamcity_request.times_called == 1
    tc_request_args = teamcity_request.next_call()['request']
    assert tc_request_args.path_qs == (
        '/teamcity/app/rest/'
        'agents?locator=authorized:any,'
        'defaultFilter:false&fields=agent(id,name,connected,'
        'enabled,authorized,uptodate,pool(name),properties(*),'
        'enabledInfo(comment(*)))'
    )
    assert tc_request_args.headers['Authorization'] == 'Bearer foobar'

    assert tc_request_args.headers['Accept'] == 'application/json'

    assert juggler_request.calls == load_json(params.juggler_response_file)
