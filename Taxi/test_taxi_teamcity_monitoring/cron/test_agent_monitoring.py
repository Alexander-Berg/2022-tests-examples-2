# pylint: disable=redefined-outer-name
import json
from typing import NamedTuple

from aiohttp import web
import pytest


from taxi.clients import juggler as juggler_client

from taxi_teamcity_monitoring.generated.cron import run_cron


class Params(NamedTuple):
    teamcity_filename: str = ''
    juggler_filename: str = ''


@pytest.mark.now('2018-10-05T06:00:00')
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_1.json',
                juggler_filename='juggler_events_1.json',
            ),
            id='all ok',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_2.json',
                juggler_filename='juggler_events_2.json',
            ),
            id='one fail',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_3.json',
                juggler_filename='juggler_events_3.json',
            ),
            id='all fail',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_4.json',
                juggler_filename='juggler_events_4.json',
            ),
            id='cannot find commit',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_5.json',
                juggler_filename='juggler_events_5.json',
            ),
            id='canceled',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_6.json',
                juggler_filename='juggler_events_6.json',
            ),
            id='extra',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_7.json',
                juggler_filename='juggler_events_7.json',
            ),
            id='ignore agent_monitoring',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_8.json',
                juggler_filename='juggler_events_8.json',
            ),
            id='customs fail',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_9.json',
                juggler_filename='juggler_events_9.json',
            ),
            id='develop fail',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_10.json',
                juggler_filename='juggler_events_10.json',
            ),
            id='develop fail ignored',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_11.json',
                juggler_filename='juggler_events_11.json',
            ),
            id='agent_check ignore categories',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_12.json',
                juggler_filename='juggler_events_12.json',
            ),
            id='pr pull',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_13.json',
                juggler_filename='juggler_events_13.json',
            ),
            id='ignore builds from tst projects',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_14.json',
                juggler_filename='juggler_events_14.json',
            ),
            id='ignore develop',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_15.json',
                juggler_filename='juggler_events_15.json',
            ),
            id='no deps changelog',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_16.json',
                juggler_filename='juggler_events_16.json',
            ),
            id='ignore too-old-builds',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_17.json',
                juggler_filename='juggler_events_17.json',
            ),
            id='pr success on agent dont shadow another agent success',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_18.json',
                juggler_filename='juggler_events_18.json',
            ),
            id='one-pr not-warn',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_19.json',
                juggler_filename='juggler_events_19.json',
            ),
            id='ignore robot-taxi-builder',
        ),
        pytest.param(
            Params(
                teamcity_filename='teamcity_response_info_20.json',
                juggler_filename='juggler_events_20.json',
            ),
            id='trunk fail',
        ),
    ],
)
async def test_run_monitor(
        simple_secdist,
        load_json,
        load,
        patch_aiohttp_session,
        response_mock,
        params,
        mock_teamcity,
):
    build_template = load('teamcity_build.json.template')
    response_info = load_json(params.teamcity_filename)
    response_data = {'build': []}
    for build_info in response_info:
        build_string = build_template
        build_info['project_name'] = (
            f'Yandex Taxi Projects / {build_info.get("project_name", "Tools")}'
            ' / internal packages / yandex-taxi-dashboards'
        )
        build_info.setdefault('ignore_juggler_develop', '')
        build_info.setdefault('triggered', {})
        build_info['web_url'] = f'http://{build_info["build_type_id"]}'
        for info_key, info_value in build_info.items():
            build_string = build_string.replace(
                '%{}%'.format(info_key), json.dumps(info_value),
            )
        build_json = json.loads(build_string)
        response_data['build'].append(build_json)

    @mock_teamcity('/app/rest/builds', prefix=True)
    def teamcity_request(request):
        return web.json_response(response_data)

    events_json = None

    @patch_aiohttp_session(juggler_client.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events_json
        events_json = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        [
            (
                'taxi_teamcity_monitoring.crontasks'
                '.agent_monitoring.run_agent_monitoring'
            ),
            '-t',
            '0',
        ],
    )

    assert teamcity_request.next_call()['request'].path_qs == (
        '/teamcity/app/rest/builds?locator=affectedProject'
        '(id:YandexTaxiProjects),branch:default:any,failedToStart:any,'
        'count:100&fields=build(id,number,status,webUrl,branch:(name),'
        'agent:(properties(property)),buildType(id,name,projectName,'
        'parameters(*)),startDate,statusText,branchName,'
        'triggered(user(username)))'
    )
    assert not teamcity_request.has_calls
    assert len(juggler_request.calls) == 1

    events_json_expected = load_json(params.juggler_filename)
    assert events_json == events_json_expected
