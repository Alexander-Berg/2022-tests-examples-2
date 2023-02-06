import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from urllib import parse as urlparse

from aiohttp import web
import freezegun
import pytest

from taxi_teamcity_monitoring.crontasks.handle_huge_pr import (
    run_handle_huge_pr,
)
from taxi_teamcity_monitoring.generated.cron import run_cron

ARCANUM_API_PREFIX = '/api/v1/'
TC_API_PREFIX = '/app/rest/'
MAC_TYPE = 'YandexTaxiProjects_Uservices_PullRequestsMacOS'
PR_NUMBER = 1011


class Params(NamedTuple):
    issues_labels_response: List[Any]
    arcanum_expected_calls: List[Dict[str, str]]
    teamcity_expected_calls: List[Dict[str, str]]
    time: datetime.datetime = datetime.datetime(2020, 1, 13, 1)
    pulls_info: Dict[str, Dict[str, Any]] = {}
    queued_builds: Dict[str, List[Dict[str, Any]]] = {}
    comment: str = ''


class ArcanumCalls:
    get_labels = {
        'method': 'GET',
        'url': (
            'review-requests?query=open()%3Blabel('
            f'{run_handle_huge_pr.ACCEPT_LABEL})%3B'
            f'path(/taxi/uservices)&fields=review_requests(id)'
        ),
    }

    @staticmethod
    def get_pr():
        return {
            'method': 'GET',
            'url': (
                f'review-requests/{PR_NUMBER}?fields=url,id,checks'
                f'(system,type,status,system_check_uri),'
                'labels,policies(auto_merge)'
            ),
        }

    @staticmethod
    def update_comment():
        return {
            'method': 'POST',
            'url': f'review-requests/{PR_NUMBER}/comments',
        }

    @staticmethod
    def update_labels_for_pr():
        return {'method': 'PUT', 'url': f'review-requests/{PR_NUMBER}/labels'}

    @staticmethod
    def update_automerge_pr():
        return {
            'method': 'PATCH',
            'url': f'review-requests/{PR_NUMBER}/policies',
        }


class TeamcityCalls:
    add_build = {'method': 'POST', 'url': 'buildQueue?moveToTop=true'}

    @staticmethod
    def get_build(_id):
        return {'method': 'GET', 'url': f'buildQueue/id:{_id}'}

    @staticmethod
    def get_builds(_type):
        return {
            'method': 'GET',
            'url': (
                f'buildQueue?locator=buildType:{_type}&'
                f'fields=build(id,branchName)'
            ),
        }

    @staticmethod
    def get_running_builds():
        branch = f'users/robot-stark/taxi/uservices/{PR_NUMBER}/head'
        return {
            'method': 'GET',
            'url': (
                f'builds?locator=buildType:type_1,branch:{branch},'
                f'running:true&fields=build(id)'
            ),
        }

    @staticmethod
    def get_build_agent(_id):
        return {
            'method': 'GET',
            'url': (
                f'builds?locator=id:{_id}&fields=build(agent(id),finishDate)'
            ),
        }

    @staticmethod
    def get_comment(_id):
        return {
            'method': 'GET',
            'url': f'buildQueue/id:{_id}?fields=comment(text)',
        }

    @staticmethod
    def delete_build(_id):
        return {'method': 'DELETE', 'url': f'buildQueue/id:{_id}'}


def issue_resp(ids: List[Any]) -> List[Dict[str, Any]]:
    return [{'id': _id} for _id in ids]


def pulls_info(
        checks: Optional[List[Dict[str, Optional[str]]]] = None,
) -> Dict[str, Dict[str, Any]]:
    if checks is None:
        checks = [{}]
    response: Dict[str, Dict[str, Any]] = {}

    if not checks:
        return response
    pr_entry: Dict[str, Any] = dict(id=PR_NUMBER)

    entry_checks: List[Dict[str, Optional[str]]] = []
    for i, check in enumerate(checks):
        check_entry: Dict[str, Optional[str]] = {
            'system': 'teamcity-taxi',
            'status': 'success',
            'type': f'some_buildtype_{i}',
            'system_check_uri': f'http://some?buildId={i + 1}',
        }
        check_entry.update(check)
        entry_checks.append(check_entry)

    pr_entry['checks'] = entry_checks
    response[str(PR_NUMBER)] = pr_entry
    response[str(PR_NUMBER)]['labels'] = [
        {'name': run_handle_huge_pr.ACCEPT_LABEL},
    ]
    return response


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                issues_labels_response=[],
                arcanum_expected_calls=[ArcanumCalls.get_labels],
                teamcity_expected_calls=[],
                pulls_info=pulls_info([]),
            ),
            id='no_labeled_issues',
        ),
        pytest.param(
            Params(
                issues_labels_response=issue_resp([PR_NUMBER]),
                time=datetime.datetime(2020, 1, 13, 10),
                arcanum_expected_calls=[
                    ArcanumCalls.get_labels,
                    ArcanumCalls.get_pr(),
                    ArcanumCalls.update_automerge_pr(),
                ],
                teamcity_expected_calls=[],
                pulls_info=pulls_info(),
            ),
            id='remove_automerge_if_day',
        ),
        pytest.param(
            Params(
                issues_labels_response=issue_resp([PR_NUMBER]),
                arcanum_expected_calls=[
                    ArcanumCalls.get_labels,
                    ArcanumCalls.get_pr(),
                    ArcanumCalls.update_automerge_pr(),
                ],
                teamcity_expected_calls=[],
                pulls_info=pulls_info(),
            ),
            id='apply_automerge_if_all_success',
        ),
        pytest.param(
            Params(
                issues_labels_response=issue_resp([PR_NUMBER]),
                arcanum_expected_calls=[
                    ArcanumCalls.get_labels,
                    ArcanumCalls.get_pr(),
                ],
                teamcity_expected_calls=[],
                pulls_info=pulls_info([{'status': 'unknown'}]),
            ),
            id='wait_if_unknown',
        ),
        pytest.param(
            Params(
                issues_labels_response=issue_resp([PR_NUMBER]),
                arcanum_expected_calls=[
                    ArcanumCalls.get_labels,
                    ArcanumCalls.get_pr(),
                ],
                teamcity_expected_calls=[
                    TeamcityCalls.get_builds(MAC_TYPE),
                    TeamcityCalls.delete_build(123),
                    TeamcityCalls.get_comment(124),
                    TeamcityCalls.delete_build(124),
                    TeamcityCalls.add_build,
                ],
                pulls_info=pulls_info(
                    [{'status': 'pending', 'type': MAC_TYPE}],
                ),
                queued_builds={
                    MAC_TYPE: [
                        {
                            'id': 123,
                            'buildTypeId': MAC_TYPE,
                            'branchName': (
                                'users/robot-stark/taxi/uservices/'
                                f'{PR_NUMBER}/head'
                            ),
                        },
                        {
                            'id': 124,
                            'buildTypeId': MAC_TYPE,
                            'branchName': (
                                'users/robot-stark/taxi/uservices/'
                                f'{PR_NUMBER}/head'
                            ),
                        },
                        {
                            'id': 125,
                            'buildTypeId': MAC_TYPE,
                            'branchName': (
                                'users/robot-stark/taxi/uservices/1012/' 'head'
                            ),
                        },
                    ],
                },
            ),
            id='restart_mac_build_wo_comment',
        ),
        pytest.param(
            Params(
                issues_labels_response=issue_resp([PR_NUMBER]),
                arcanum_expected_calls=[
                    ArcanumCalls.get_labels,
                    ArcanumCalls.get_pr(),
                ],
                teamcity_expected_calls=[TeamcityCalls.get_builds('type_1')],
                pulls_info=pulls_info(
                    [{'status': 'failure', 'type': 'type_1'}],
                ),
                queued_builds={
                    'type_1': [
                        {
                            'id': 9991,
                            'buildTypeId': 'type_1',
                            'branchName': (
                                'users/robot-stark/taxi/uservices/'
                                f'{PR_NUMBER}/head'
                            ),
                        },
                    ],
                },
            ),
            id='skip_restart_failed_build_if_in_queue',
        ),
        pytest.param(
            Params(
                issues_labels_response=issue_resp([PR_NUMBER]),
                arcanum_expected_calls=[
                    ArcanumCalls.get_labels,
                    ArcanumCalls.get_pr(),
                ],
                teamcity_expected_calls=[
                    TeamcityCalls.get_builds('type_1'),
                    TeamcityCalls.get_running_builds(),
                    TeamcityCalls.get_comment(9991),
                    TeamcityCalls.get_build_agent(9991),
                    TeamcityCalls.add_build,
                ],
                pulls_info=pulls_info(
                    [
                        {
                            'status': 'pending',
                            'type': 'type_1',
                            'system_check_uri': f'http://some?buildId=9991',
                        },
                        {
                            'status': 'pending',
                            'type': MAC_TYPE,
                            'system_check_uri': None,
                        },
                    ],
                ),
            ),
            id='add_mac_build_if_trouble_with_tc',
        ),
        pytest.param(
            Params(
                issues_labels_response=issue_resp([PR_NUMBER]),
                arcanum_expected_calls=[
                    ArcanumCalls.get_labels,
                    ArcanumCalls.get_pr(),
                ],
                teamcity_expected_calls=[
                    TeamcityCalls.get_builds('type_1'),
                    TeamcityCalls.get_running_builds(),
                    TeamcityCalls.get_comment(9991),
                    TeamcityCalls.get_build_agent(9991),
                    TeamcityCalls.add_build,
                ],
                pulls_info=pulls_info(
                    [
                        {
                            'status': 'failure',
                            'type': 'type_1',
                            'system_check_uri': f'http://some?buildId=9991',
                        },
                        {
                            'status': 'failure',
                            'type': 'type_skip',
                            'system_check_uri': f'http://some?buildId=9992',
                        },
                    ],
                ),
            ),
            id='restart_failed',
        ),
        pytest.param(
            Params(
                issues_labels_response=issue_resp([PR_NUMBER]),
                arcanum_expected_calls=[
                    ArcanumCalls.get_labels,
                    ArcanumCalls.get_pr(),
                    ArcanumCalls.update_labels_for_pr(),
                    ArcanumCalls.update_comment(),
                ],
                teamcity_expected_calls=[
                    TeamcityCalls.get_builds('type_1'),
                    TeamcityCalls.get_running_builds(),
                    TeamcityCalls.get_comment(9991),
                ],
                pulls_info=pulls_info(
                    [
                        {
                            'status': 'failure',
                            'type': 'type_1',
                            'system_check_uri': f'http://some?buildId=9991',
                        },
                    ],
                ),
                comment=run_handle_huge_pr.RESTARTED + '3',
            ),
            id='build_fails_max_times',
        ),
    ],
)
@pytest.mark.config(
    TEAMCITY_MONITORING_AUTOMERGE_HUGE_ENABLED=True,
    TEAMCITY_MONITORING_AUTOMERGE_HUGE_BUILDS=[MAC_TYPE],
    TEAMCITY_MONITORING_AUTOMERGE_HUGE_IGNORED_FAILED_BUILDS=['type_skip'],
)
def test_huge_automerge(params: Params, mock_arcanum, mock_teamcity, mock):
    @mock_arcanum(ARCANUM_API_PREFIX, prefix=True)
    async def arcanum_request(request):
        arcanum_api_suffix = request.path.split(ARCANUM_API_PREFIX)[1]
        command = arcanum_api_suffix.split('/', maxsplit=2)
        len_command = len(command)
        if command[0] == 'review-requests':
            if len_command == 1:
                return web.json_response(
                    data={
                        'data': {
                            'review_requests': params.issues_labels_response,
                        },
                    },
                )
            if len_command == 3:
                if command[2] in ('policies', 'labels'):
                    return web.json_response(status=204)
            return web.json_response({'data': params.pulls_info[command[1]]})
        assert False, 'this should not happened, command: %s' % command

    @mock_teamcity(TC_API_PREFIX, prefix=True)
    def teamcity_request(request):
        method = request.method
        if method == 'GET':
            query = urlparse.urlparse(request.url).query
            locator = urlparse.parse_qs(query).get('locator', [''])[-1]
            fields = urlparse.parse_qs(query).get('fields', [''])[-1]
            if fields and 'comment' in fields:
                resp = {}
                if params.comment:
                    resp = {'comment': {'text': params.comment}}
                return web.json_response(resp)
            if 'buildType:' in locator:
                build_type = locator.split('buildType:')[-1]
                return web.json_response(
                    {'build': params.queued_builds.get(build_type, [])},
                )
        elif method == 'POST':
            return web.json_response({'id': 1})
        return None

    with freezegun.freeze_time(params.time):
        run_cron.main(
            [
                'taxi_teamcity_monitoring.crontasks.'
                'handle_huge_pr.run_handle_huge_pr',
                '-t',
                '0',
            ],
        )

    arcanum_calls = []
    teamcity_calls = []

    while arcanum_request.has_calls:
        req = arcanum_request.next_call()['request']
        cuted_url = req.url.split('/arcanum/api/v1/')[-1]
        arcanum_calls.append({'method': req.method, 'url': cuted_url})

    while teamcity_request.has_calls:
        req = teamcity_request.next_call()['request']
        cuted_url = req.url.split('teamcity/app/rest/')[-1]
        teamcity_calls.append({'method': req.method, 'url': cuted_url})

    assert arcanum_calls == params.arcanum_expected_calls
    assert teamcity_calls == params.teamcity_expected_calls
