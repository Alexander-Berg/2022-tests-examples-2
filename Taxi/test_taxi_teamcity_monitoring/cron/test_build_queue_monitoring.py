import copy
import dataclasses
import re
from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

from aiohttp import web
import freezegun
import pytest

import juggler_client

from taxi_teamcity_monitoring.generated.cron import run_cron

REST_API_PREFIX = '/app/rest/'
BUILD_ID_PAT = re.compile(r'buildQueue/id:(\d+)')
AGENTS_POOL_PAT = re.compile(r'agentPools/id:(\d+)/agents')
BUILD_COMPAT_PAT = re.compile(r'compatible:\(build:\(id:(\d+)\)\)')
SOME_TAXI_PROJECT = 'Yandex Taxi Projects / Some Taxi Project'

DEFAULT_SOLOMON_REQUEST = {
    'sensors': [
        {
            'kind': 'IGAUGE',
            'labels': {
                'agent_pool': 'TaxiBackendMacPool',
                'application': 'taxi-build-queue-statistics-v1',
                'host': 'buildagent.teamcity.taxi.yandex-team.ru',
                'sensor': 'MaxTimeInQueue',
            },
            'value': 0,
        },
        {
            'kind': 'IGAUGE',
            'labels': {
                'agent_pool': 'TaxiBackendMacPoolSlow',
                'application': 'taxi-build-queue-statistics-v1',
                'host': 'buildagent.teamcity.taxi.yandex-team.ru',
                'sensor': 'MaxTimeInQueue',
            },
            'value': 0,
        },
        {
            'kind': 'IGAUGE',
            'labels': {
                'agent_pool': 'TaxiBackendStatistics',
                'application': 'taxi-build-queue-statistics-v1',
                'host': 'buildagent.teamcity.taxi.yandex-team.ru',
                'sensor': 'MaxTimeInQueue',
            },
            'value': 0,
        },
    ],
    'ts': 1602331200,
}

DEFAULT_BUILD_INFO = {
    'state': 'queued',
    'snapshot-dependencies': {'build': []},
    'buildType': {'projectName': SOME_TAXI_PROJECT},
}


def get_filled_solomon_response(
        pool_vals_dict: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    copied_resp = copy.deepcopy(DEFAULT_SOLOMON_REQUEST)
    if not pool_vals_dict:
        return copied_resp
    for pool, value in pool_vals_dict.items():
        if pool == 'TaxiBackendMacPool':
            pool_idx = 0
        elif pool == 'TaxiBackendMacPoolSlow':
            pool_idx = 1
        elif pool == 'TaxiBackendStatistics':
            pool_idx = 2
        else:
            pool_idx = 3

        sensors_seq = copied_resp['sensors']
        sensors_seq = cast(List[Dict[str, int]], sensors_seq)
        sensors_seq[pool_idx]['value'] = value
    return copied_resp


@dataclasses.dataclass
class BuildInfo:
    id_: int
    queued_date: str = ''
    web_url: str = ''
    finish_date: str = ''
    agent: dict = dataclasses.field(default_factory=lambda: ({}))
    composite: bool = False
    snapshot_dependencies: dict = dataclasses.field(
        default_factory=lambda: ({'build': []}),
    )
    state: str = 'queued'
    build_type: dict = dataclasses.field(
        default_factory=lambda: {'projectName': SOME_TAXI_PROJECT},
    )


class Params(NamedTuple):
    solomon_request: Dict[str, Any] = get_filled_solomon_response()
    build_queue: List[Dict[str, Any]] = []
    build_infos: Dict[str, BuildInfo] = {}
    comp_agents: Dict[str, List[Dict[str, str]]] = {}
    finished_dep_builds: List[Dict[str, Any]] = []
    juggler_response_file: str = 'juggler_calls.json'


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(Params(), id='empty_queue'),
        pytest.param(
            Params(
                solomon_request=get_filled_solomon_response(
                    {'TaxiBackendStatistics': 9398880},
                ),
                build_queue=[{'id': 1774183}],
                build_infos={
                    '1774183': BuildInfo(
                        id_=1774183,
                        queued_date='20200623T201200+0300',
                        web_url='some_url_1774183',
                    ),
                },
                comp_agents={
                    '1774183': [
                        {'name': 'buildagent-c16-xenial-066.buildfarm'},
                    ],
                },
            ),
            id='one_build',
        ),
        pytest.param(
            Params(
                build_queue=[{'id': 1774184}],
                build_infos={
                    '1774184': BuildInfo(
                        id_=1774184,
                        queued_date='20200708T221500+0300',
                        state='running',
                        web_url='some_url_1774184',
                    ),
                },
                comp_agents={'1774184': []},
            ),
            id='one_runned_build',
        ),
        pytest.param(
            Params(
                build_queue=[{'id': 1778888}],
                build_infos={
                    '1778888': BuildInfo(
                        id_=1778888,
                        queued_date='20210814T120800+0300',
                        web_url='some_url_1778888',
                    ),
                },
                comp_agents={'1778888': [{'name': 'eda-php-test-qyp-sas-01'}]},
            ),
            id='one_wrong_pool',
        ),
        pytest.param(
            Params(
                solomon_request=get_filled_solomon_response(
                    {'TaxiBackendMacPoolSlow': 1304760},
                ),
                build_queue=[{'id': 1778380}],
                build_infos={
                    '1778380': BuildInfo(
                        id_=1778380,
                        queued_date='20200925T123400+0300',
                        web_url='some_url_1778380',
                    ),
                },
                comp_agents={'1778380': [{'name': 'buildagent-mac-sas-02'}]},
            ),
            id='one_slow_pool',
        ),
        pytest.param(
            Params(
                solomon_request=get_filled_solomon_response(
                    {'TaxiBackendMacPool': 1297740},
                ),
                build_queue=[{'id': 1778402}],
                build_infos={
                    '1778402': BuildInfo(
                        id_=1778402,
                        queued_date='20200925T143100+0300',
                        web_url='some_url_1778402',
                    ),
                },
                comp_agents={
                    '1778402': [
                        {'name': 'buildagent-mac-iva-01'},
                        {'name': 'buildagent-mac-sas-02'},
                    ],
                },
            ),
            id='one_fast_pool',
        ),
        pytest.param(
            Params(
                build_queue=[
                    {'id': 1774183},
                    {'id': 1774184},
                    {'id': 1778379},
                    {'id': 1778380},
                    {'id': 1778389},
                    {'id': 1778402},
                ],
                build_infos={
                    '1774183': BuildInfo(
                        id_=1774183,
                        queued_date='20200521T232000+0300',
                        web_url='some_url_1774183',
                    ),
                    '1774184': BuildInfo(
                        id_=1774184,
                        queued_date='20200521T180000+0300',
                        web_url='some_url_1774184',
                    ),
                    '1778379': BuildInfo(
                        id_=1778379,
                        queued_date='20200521T110000+0300',
                        web_url='some_url_1778379',
                    ),
                    '1778380': BuildInfo(
                        id_=1778380,
                        queued_date='20200521T150000+0300',
                        web_url='some_url_1778380',
                    ),
                    '1778389': BuildInfo(
                        id_=1778389,
                        queued_date='20200521T160000+0300',
                        web_url='some_url_1778389',
                    ),
                    '1778402': BuildInfo(
                        id_=1778402,
                        queued_date='20200521T190000+0300',
                        web_url='some_url_1778402',
                    ),
                },
                comp_agents={
                    '1774183': [
                        {'name': 'buildagent-c16-xenial-066.buildfarm'},
                    ],
                    '1774184': [],
                    '1778379': [
                        {'name': 'buildagent-c16-xenial-001.buildfarm'},
                    ],
                    '1778380': [{'name': 'buildagent-mac-sas-02'}],
                    '1778389': [],
                    '1778402': [
                        {'name': 'buildagent-mac-iva-01'},
                        {'name': 'buildagent-mac-sas-02'},
                    ],
                },
                solomon_request=get_filled_solomon_response(
                    {
                        'TaxiBackendMacPool': 12254400,
                        'TaxiBackendMacPoolSlow': 12268800,
                        'TaxiBackendStatistics': 12238800,
                    },
                ),
                juggler_response_file='juggler_calls_all_cases.json',
            ),
            id='all_cases',
        ),
        pytest.param(
            Params(
                solomon_request=get_filled_solomon_response(
                    {'TaxiBackendStatistics': 0},
                ),
                build_queue=[{'id': 1774183}],
                build_infos={
                    '1774183': BuildInfo(
                        id_=1774183,
                        queued_date='20200623T201200+0300',
                        composite=True,
                        web_url='some_url_1774183',
                    ),
                },
                comp_agents={
                    '1774183': [
                        {'name': 'buildagent-c16-xenial-066.buildfarm'},
                    ],
                },
            ),
            id='composite_build',
        ),
        pytest.param(
            Params(
                solomon_request=get_filled_solomon_response(
                    {'TaxiBackendStatistics': 0},
                ),
                build_queue=[{'id': 1774183}],
                build_infos={
                    '1774183': BuildInfo(
                        id_=1774183,
                        queued_date='20200623T201200+0300',
                        composite=True,
                        snapshot_dependencies={
                            'build': [
                                {'state': 'queued'},
                                {'state': 'finished'},
                                {'state': 'running'},
                            ],
                        },
                        web_url='some_url_1774183',
                    ),
                },
                comp_agents={'1774183': []},
            ),
            id='composite_build_incompatible',
        ),
        pytest.param(
            Params(
                solomon_request=get_filled_solomon_response(
                    {'TaxiBackendStatistics': 0},
                ),
                build_queue=[{'id': 1774183}],
                build_infos={
                    '1774183': BuildInfo(
                        id_=1774183,
                        queued_date='20200623T201200+0300',
                        agent={'name': 'buildagent-c16-xenial-024.buildfarm'},
                        web_url='some_url_1774183',
                    ),
                },
                comp_agents={
                    '1774183': [
                        {'name': 'buildagent-c16-xenial-066.buildfarm'},
                    ],
                },
            ),
            id='specific_agent',
        ),
        pytest.param(
            Params(
                solomon_request=get_filled_solomon_response(
                    {'TaxiBackendStatistics': 0},
                ),
                build_queue=[{'id': 1774183}],
                build_infos={
                    '1774183': BuildInfo(
                        id_=1774183,
                        queued_date='20200623T201200+0300',
                        snapshot_dependencies={
                            'build': [
                                {'state': 'queued'},
                                {'state': 'finished'},
                                {'state': 'running'},
                            ],
                        },
                        web_url='some_url_1774183',
                    ),
                },
                comp_agents={
                    '1774183': [
                        {'name': 'buildagent-c16-xenial-066.buildfarm'},
                    ],
                },
            ),
            id='dependant_not_finished',
        ),
        pytest.param(
            Params(
                solomon_request=get_filled_solomon_response(
                    {'TaxiBackendStatistics': 6039330},
                ),
                build_queue=[{'id': 1774183}],
                build_infos={
                    '1774183': BuildInfo(
                        id_=1774183,
                        queued_date='20200623T201200+0300',
                        snapshot_dependencies={
                            'build': [
                                {'id': 2544728, 'state': 'finished'},
                                {'id': 4543713, 'state': 'finished'},
                            ],
                        },
                        web_url='some_url_1774183',
                    ),
                    '2544728': BuildInfo(
                        id_=2544728, finish_date='20200701T223400+0300',
                    ),
                    '4543713': BuildInfo(
                        id_=4543713, finish_date='20200801T172430+0300',
                    ),
                },
                comp_agents={
                    '1774183': [
                        {'name': 'buildagent-c16-xenial-066.buildfarm'},
                    ],
                },
                finished_dep_builds=[{'id': 2544728}, {'id': 4543713}],
            ),
            id='dependant_all_finished',
        ),
        pytest.param(
            Params(
                solomon_request=get_filled_solomon_response(
                    {'TaxiBackendStatistics': 0},
                ),
                build_queue=[{'id': 1774183}],
                build_infos={
                    '1774183': BuildInfo(
                        id_=1774183,
                        queued_date='20200623T201200+0300',
                        state='running',
                        web_url='some_url_1774183',
                    ),
                },
                comp_agents={
                    '1774183': [
                        {'name': 'buildagent-c16-xenial-066.buildfarm'},
                    ],
                },
            ),
            id='wrong_state',
        ),
        pytest.param(
            Params(
                build_queue=[{'id': 1774184}],
                build_infos={
                    '1774184': BuildInfo(
                        id_=1774184,
                        queued_date='20200708T221500+0300',
                        web_url='some_url_1774184',
                    ),
                },
                comp_agents={'1774184': []},
                juggler_response_file='juggler_calls_one_stalled_build.json',
            ),
            id='one_stalled_build',
        ),
        pytest.param(
            Params(
                build_queue=[{'id': 1774184}],
                build_infos={
                    '1774184': BuildInfo(
                        id_=1774184,
                        queued_date='20200708T221500+0300',
                        snapshot_dependencies={
                            'build': [
                                {'state': 'finished'},
                                {'state': 'finished'},
                                {'state': 'finished'},
                            ],
                        },
                        web_url='some_url_1774184',
                    ),
                },
                comp_agents={'1774184': []},
                juggler_response_file='juggler_calls_one_stalled_build.json',
            ),
            id='finished_dep_stalled_build',
        ),
        pytest.param(
            Params(
                build_queue=[{'id': 1774184}],
                build_infos={
                    '1774184': BuildInfo(
                        id_=1774184,
                        queued_date='20200708T221500+0300',
                        web_url='some_url_1774184',
                        build_type={'projectName': 'Some Other Project'},
                    ),
                },
                comp_agents={'1774184': []},
            ),
            id='filter_non_taxi_project',
        ),
        pytest.param(
            Params(
                build_queue=[
                    {'id': 1774183},
                    {'id': 1774184},
                    {'id': 1778379},
                ],
                build_infos={
                    '1774183': BuildInfo(
                        id_=1774183,
                        queued_date='20200521T232000+0300',
                        web_url='some_url_1774183',
                    ),
                    '1774184': BuildInfo(
                        id_=1774184,
                        queued_date='20200521T180000+0300',
                        web_url='some_url_1774184',
                    ),
                    '1778379': BuildInfo(
                        id_=1778379,
                        queued_date='20200521T110000+0300',
                        web_url='some_url_1778379',
                    ),
                },
                comp_agents={'1774183': [], '1774184': [], '1778379': []},
                juggler_response_file='juggler_calls_cut_stalled_build.json',
            ),
            id='cut_stalled_build_message',
        ),
    ],
)
@freezegun.freeze_time('2020-10-10T12:00:00')
@pytest.mark.config(TEAMCITY_MONITORING_BUILD_QUEUE_STAT_ENABLED=True)
@pytest.mark.config(
    TEAMCITY_MONITORING_BUILD_QUEUE_STAT_LONG_POOLS=['buildagent-mac-sas-02'],
)
@pytest.mark.config(
    TEAMCITY_MONITORING_BUILD_QUEUE_STAT_ALLOWED_POOLS=[
        'TaxiBackendStatistics',
        'TaxiBackendMacPool',
    ],
)
async def test_build_queue_statistics(
        load,
        load_json,
        mock_solomon,
        monkeypatch,
        mock_teamcity,
        params,
        patch_aiohttp_session,
):
    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.'
        'build_queue_monitoring.run_build_queue_monitoring.'
        'MAX_STALLED_BUILDS',
        2,
    )

    @mock_teamcity(REST_API_PREFIX, prefix=True)
    def teamcity_request(request):
        rest_api_suffix = request.path.split(REST_API_PREFIX, maxsplit=1)[-1]

        if rest_api_suffix == 'agentPools':
            resp_json = load_json('tc_agent_pools_response.json')
            return web.json_response(resp_json)
        agents_match = AGENTS_POOL_PAT.match(rest_api_suffix)

        if agents_match:
            pool_id = agents_match.group(1)
            if pool_id == '12':
                resp_json = load_json('tc_stat_pools_agents_response.json')
                return web.json_response(resp_json)
            if pool_id == '1':
                resp_json = load_json('tc_mac_pools_agents_response.json')
                return web.json_response(resp_json)
            assert False, f'Incorrect agent pool id: {pool_id}'

        if rest_api_suffix == 'buildQueue':
            resp_json = {'build': params.build_queue}
            return web.json_response(resp_json)

        build_id_match = BUILD_ID_PAT.match(rest_api_suffix)
        if build_id_match:
            build_id = build_id_match.group(1)

            build_info = params.build_infos.get(build_id)
            assert build_info, f'Incorrect id for build: {build_id}'
            return web.json_response(convert_buildinfo_to_dict(build_info))

        if rest_api_suffix == 'agents':
            locator = request.query['locator']
            build_id_match = BUILD_COMPAT_PAT.match(locator)
            assert build_id_match, 'Should be build_id in agents locator'
            build_id = build_id_match.group(1)
            comp_agents = params.comp_agents.get(build_id)
            assert (
                comp_agents is not None
            ), f'Incorrect id for comp_agents: {build_id}'
            resp_json = {'agent': comp_agents, 'count': len(comp_agents)}
            return web.json_response(resp_json)

        return web.json_response({})

    @mock_solomon('/api/v2/push')
    def handler(request):
        assert request.json == params.solomon_request
        return {'sensorsProcessed': len(request.json['sensors'])}

    events_json = None

    @patch_aiohttp_session(juggler_client.juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events_json
        events_json = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'build_queue_monitoring.run_build_queue_monitoring',
            '-t',
            '0',
            '--debug',
        ],
    )

    assert (
        teamcity_request.next_call()['request'].path_qs
        == '/teamcity/app/rest/agentPools?fields=agentPool(id,name)'
    )
    assert (
        teamcity_request.next_call()['request'].path_qs
        == '/teamcity/app/rest/agentPools/id:1/agents?fields=agent(name)'
    )
    assert (
        teamcity_request.next_call()['request'].path_qs
        == '/teamcity/app/rest/agentPools/id:12/agents?fields=agent(name)'
    )
    assert (
        teamcity_request.next_call()['request'].path_qs
        == '/teamcity/app/rest/buildQueue?fields=build(id)'
    )
    for build in params.build_queue:
        assert teamcity_request.next_call()['request'].path_qs == (
            '/teamcity/app/rest/agents?locator=compatible:'
            '(build:(id:{id}))&fields=agent(name),count'.format(**build)
        )
        assert teamcity_request.next_call()['request'].path_qs == (
            '/teamcity/app/rest/buildQueue/'
            'id:{id}?fields=queuedDate,composite,agent,'
            'snapshot-dependencies(build),finishDate,state,'
            'webUrl,buildType(projectName)'.format(**build)
        )
    for build in params.finished_dep_builds:
        assert teamcity_request.next_call()['request'].path_qs == (
            '/teamcity/app/rest/buildQueue/id:{id}?'
            'fields=queuedDate,composite,agent,snapshot-dependencies(build),'
            'finishDate,state,webUrl,buildType(projectName)'.format(**build)
        )
    assert not teamcity_request.has_calls
    assert handler.times_called == 1

    assert juggler_request.calls == load_json(params.juggler_response_file)


def convert_buildinfo_to_dict(build_info: BuildInfo) -> dict:
    json_body = {
        'id': build_info.id_,
        'queuedDate': build_info.queued_date,
        'webUrl': build_info.web_url,
        'composite': build_info.composite,
        'snapshot-dependencies': build_info.snapshot_dependencies,
        'state': build_info.state,
        'buildType': build_info.build_type,
    }
    if build_info.finish_date:
        json_body['finishDate'] = build_info.finish_date
    if build_info.agent:
        json_body['agent'] = build_info.agent

    return json_body
