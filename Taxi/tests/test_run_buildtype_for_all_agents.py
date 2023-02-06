import copy
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

import freezegun
import pytest

import run_buildtype_for_all_agents
import taxi_buildagent.clients.teamcity as teamcity_client


TEAMCITY_TOKEN = 'secret_token'
TEAMCITY_AUTH = teamcity_client.HTTPBearerAuth(TEAMCITY_TOKEN)


class Params(NamedTuple):
    agents_list: Optional[List[str]] = None
    agents_list_message: Optional[Dict[str, Dict[str, Any]]] = None
    build_type_trigger: Optional[Dict[str, str]] = None
    fail_message: str = ''
    argv: List[str] = ['--build-type-id', 'test-build-type']
    expected_properties: Optional[Dict[str, List[Dict[str, str]]]] = None
    are_incorrect_params: bool = False


@freezegun.freeze_time('2018-04-23 14:22:56', tz_offset=3)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                agents_list=['13', '16', '17'],
                agents_list_message={
                    'compatibleAgents': {
                        'count': '3',
                        'agent': [{'id': '13'}, {'id': '16'}, {'id': '17'}],
                    },
                },
                build_type_trigger={'some_field': 'some_text'},
            ),
        ),
        pytest.param(Params(agents_list=[], agents_list_message={})),
        pytest.param(
            Params(
                agents_list=['13'],
                agents_list_message={
                    'compatibleAgents': {
                        'count': '1',
                        'agent': [{'id': '13'}],
                    },
                },
                build_type_trigger={'some_field': 'some_text'},
                argv=[
                    '--build-type-id',
                    'test-build-type',
                    '--env-vars',
                    'k1=v1',
                ],
                expected_properties={
                    'property': [{'name': 'k1', 'value': 'v1'}],
                },
            ),
        ),
        pytest.param(
            Params(
                agents_list=['13'],
                agents_list_message={
                    'compatibleAgents': {
                        'count': '1',
                        'agent': [{'id': '13'}],
                    },
                },
                build_type_trigger={'some_field': 'some_text'},
                argv=[
                    '--build-type-id',
                    'test-build-type',
                    '--env-vars',
                    'k1=v1,k2=v2,k3=v3',
                ],
                expected_properties={
                    'property': [
                        {'name': 'k1', 'value': 'v1'},
                        {'name': 'k2', 'value': 'v2'},
                        {'name': 'k3', 'value': 'v3'},
                    ],
                },
            ),
        ),
        pytest.param(
            Params(
                agents_list=['13'],
                agents_list_message={
                    'compatibleAgents': {
                        'count': '1',
                        'agent': [{'id': '13'}],
                    },
                },
                build_type_trigger={'some_field': 'some_text'},
                argv=[
                    '--build-type-id',
                    'test-build-type',
                    '--env-vars',
                    'env.SOME_VAL=v1,env.OTHER_VAL=v2',
                ],
                expected_properties={
                    'property': [
                        {'name': 'env.SOME_VAL', 'value': 'v1'},
                        {'name': 'env.OTHER_VAL', 'value': 'v2'},
                    ],
                },
            ),
        ),
        pytest.param(
            Params(
                argv=[
                    '--build-type-id',
                    'test-build-type',
                    '--env-vars',
                    'env.SOME_VAL=v1,wrong',
                ],
                are_incorrect_params=True,
                fail_message='Wrong value \'wrong\', should be key=value',
            ),
        ),
        pytest.param(
            Params(
                argv=[
                    '--build-type-id',
                    'test-build-type',
                    '--env-vars',
                    '=v1',
                ],
                are_incorrect_params=True,
                fail_message='Key is empty in \'=v1\'',
            ),
        ),
    ],
)
def test_buildtype_for_all_agents(
        patch_requests, monkeypatch, teamcity_report_problems, params: Params,
):
    @patch_requests(
        'https://teamcity.taxi.yandex-team.ru/app/rest/buildTypes/',
    )
    def agents_list_request(method, url, **kwargs):
        return patch_requests.response(json=params.agents_list_message)

    @patch_requests('https://teamcity.taxi.yandex-team.ru/app/rest/buildQueue')
    def build_type_trigger(method, url, **kwargs):
        return patch_requests.response(json=params.build_type_trigger)

    timeout = teamcity_client.TIMEOUT
    allow_redirects = True
    verify = False
    headers = {
        'Origin': 'https://teamcity.taxi.yandex-team.ru/',
        'Accept': 'application/json',
    }

    monkeypatch.setenv('TEAMCITY_TOKEN', TEAMCITY_TOKEN)

    if params.are_incorrect_params:
        exc_class = run_buildtype_for_all_agents.IncorrectEnvVarsListError
        with pytest.raises(exc_class) as exc_info:
            run_buildtype_for_all_agents.main(params.argv)
        assert not agents_list_request.calls
        assert not build_type_trigger.calls
        assert params.fail_message == exc_info.value.subject
        return

    run_buildtype_for_all_agents.main(params.argv)

    assert agents_list_request.calls == [
        dict(
            method='GET',
            url='https://teamcity.taxi.yandex-team.ru/app/rest/buildTypes/'
            'id:test-build-type/?fields=compatibleAgents(*)',
            kwargs=dict(
                auth=TEAMCITY_AUTH,
                timeout=timeout,
                allow_redirects=allow_redirects,
                verify=verify,
                headers=headers,
            ),
        ),
    ]
    if not params.agents_list:
        assert not build_type_trigger.calls
        return

    json_data = {
        'triggeringOptions': {'queueAtTop': True},
        'branchName': '',
        'buildType': {'id': params.argv[1]},
    }
    if params.expected_properties:
        json_data['properties'] = params.expected_properties

    trigger_calls = []
    for agent_id in params.agents_list:
        json_entry = copy.deepcopy(json_data)
        json_entry['agent'] = {'id': agent_id}
        trigger_calls.append(
            {
                'method': 'POST',
                'url': (
                    'https://teamcity.taxi.yandex-team.ru/app/rest/buildQueue'
                ),
                'kwargs': {
                    'auth': TEAMCITY_AUTH,
                    'timeout': timeout,
                    'verify': verify,
                    'allow_redirects': allow_redirects,
                    'headers': headers,
                    'json': json_entry,
                },
            },
        )

    assert build_type_trigger.calls == trigger_calls
