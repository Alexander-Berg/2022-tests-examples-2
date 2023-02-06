import json
import re
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from urllib import parse as urlparse

from aiohttp import web
import pytest

from generated.clients import github

from taxi_teamcity_monitoring.crontasks.automerge_cron import (
    run_automerge_cron,
)
from taxi_teamcity_monitoring.generated.cron import run_cron


GITHUB_API_PREFIX = '/api/v3/'
GITHUB_API_REPOS = f'{GITHUB_API_PREFIX}repos/'
GITHUB_API_BASE = f'$mockserver/github{GITHUB_API_PREFIX}'
GITHUB_ORG = 'taxi'
GITHUB_DWH_ORG = 'taxi-dwh'
GITHUB_REPO = 'some_repo'
ACCEPT_LABEL = 'automerge'
GITHUB_API_URL_PREFIX = '/'.join(
    [GITHUB_API_BASE.rstrip('/'), 'repos', '(.+?)', GITHUB_REPO, '(.+)'],
)

GITHUB_API_URL_PREFIX_PATTERN = re.compile(GITHUB_API_URL_PREFIX)


class Params(NamedTuple):
    issues_labels_response: List[Any]
    expected_calls: List[Dict[str, Any]]
    pulls_info: Dict[str, Dict[str, Any]] = {}
    commits_statuses_sha_info: Dict[str, Dict[str, Any]] = {}
    pulls_reviews_info: Dict[str, List[Dict[str, Any]]] = {}
    pulls_merge_info: Dict[str, Dict[str, Any]] = {}
    user_branches_info: Dict[str, Dict[str, Any]] = {}
    delete_user_branch_status: Dict[str, Any] = {}
    issues_labels_response_headers: Optional[List[Dict[str, str]]] = None
    logger_error_list: List[str] = []
    has_exit_code: bool = False
    collaborator_perm: Dict[str, Any] = {}
    branch_restriction: Dict[str, Any] = {}
    teams_members: Dict[str, List[Dict[str, str]]] = {}
    has_merge_timeout: bool = False


BRANCHES_DEVELOP_INFO = {
    'protection': {
        'required_status_checks': {
            'contexts': [
                'submodules-check',
                'continuous-integration/db_settings',
            ],
        },
    },
    'protected': False,
}
GITHUB_TOKEN = 'SIMPLE_TOKEN'


# pylint: disable=redefined-outer-name
@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update({'GITHUB_TOKEN': GITHUB_TOKEN})
    return simple_secdist


# pylint: disable=too-many-lines
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                issues_labels_response=[],
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/issues?labels={}'.format(
                                ACCEPT_LABEL,
                            )
                        ),
                    },
                ],
            ),
            id='not_labeled_issues',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {'url': 'some_url', 'user': {'login': 'somebody'}},
                ],
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/issues?labels={}'.format(
                                ACCEPT_LABEL,
                            )
                        ),
                    },
                ],
            ),
            id='not_pull_request',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'somebody'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                        'number': 1011,
                    },
                ],
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/issues?labels={}'.format(
                                ACCEPT_LABEL,
                            )
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/somebody/'
                            'permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'PATCH',
                        'url': 'repos/taxi/some_repo/issues/1011',
                        'json': {'labels': []},
                    },
                    {
                        'method': 'POST',
                        'url': 'repos/taxi/some_repo/issues/1011/comments',
                        'json': {'body': 'no_permission'},
                    },
                ],
                collaborator_perm={'somebody': {'permission': 'read'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                logger_error_list=[
                    'Failed to automerge issue some_url: '
                    'Pull request is created by not accepted '
                    'user: somebody in repo: some_repo',
                ],
                has_exit_code=True,
            ),
            id='not_accepted_user',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'somebody'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                        'number': 1011,
                    },
                ],
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/issues?labels={}'.format(
                                ACCEPT_LABEL,
                            )
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/somebody/'
                            'permission'
                        ),
                    },
                    {'method': 'GET', 'url': 'repos/taxi/some_repo'},
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/branches/develop/'
                            'protection'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'PATCH',
                        'url': 'repos/taxi/some_repo/issues/1011',
                        'json': {'labels': []},
                    },
                    {
                        'method': 'POST',
                        'url': 'repos/taxi/some_repo/issues/1011/comments',
                        'json': {'body': 'no_permission'},
                    },
                ],
                collaborator_perm={'somebody': {'permission': 'write'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                branch_restriction={
                    'restrictions': {'users': [{'login': 'mister_x'}]},
                },
                logger_error_list=[
                    'Failed to automerge issue some_url: '
                    'Pull request is created by not accepted '
                    'user: somebody in repo: some_repo',
                ],
                has_exit_code=True,
            ),
            marks=pytest.mark.config(
                TEAMCITY_MONITORING_AUTOMERGE_BRANCH_PROTECTION=['some_repo'],
            ),
            id='not_accepted_user_branch_restriction',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'somebody'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                        'number': 1011,
                    },
                ],
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/issues?labels={}'.format(
                                ACCEPT_LABEL,
                            )
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/somebody/'
                            'permission'
                        ),
                    },
                ],
                collaborator_perm={'somebody': {'fail': True}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                logger_error_list=[
                    'Failed to automerge issue some_url: '
                    'Cannot get info about permission for '
                    'user somebody in repo some_repo. Robot needs at least '
                    'write permission. '
                    'Exception: Not defined in schema github response, '
                    'status: 400, body: b\'\'',
                ],
                has_exit_code=True,
            ),
            id='user_branch_protection_fail',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'somebody'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                        'number': 1011,
                    },
                ],
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/issues?labels={}'.format(
                                ACCEPT_LABEL,
                            )
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/somebody/'
                            'permission'
                        ),
                    },
                    {'method': 'GET', 'url': 'repos/taxi/some_repo'},
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/branches/develop/'
                            'protection'
                        ),
                    },
                    {'method': 'GET', 'url': 'teams/1234/members'},
                    {'method': 'GET', 'url': 'teams/345/members'},
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'PATCH',
                        'url': 'repos/taxi/some_repo/issues/1011',
                        'json': {'labels': []},
                    },
                    {
                        'method': 'POST',
                        'url': 'repos/taxi/some_repo/issues/1011/comments',
                        'json': {'body': 'no_permission'},
                    },
                ],
                collaborator_perm={'somebody': {'permission': 'write'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                branch_restriction={
                    'restrictions': {'teams': [{'id': 1234}, {'id': 345}]},
                },
                logger_error_list=[
                    'Failed to automerge issue some_url: '
                    'Pull request is created by not accepted '
                    'user: somebody in repo: some_repo',
                ],
                teams_members={
                    '1234': [{'login': 'mister_x'}, {'login': 'segoon'}],
                    '345': [{'login': 'null'}, {'login': 'antoshkka'}],
                },
                has_exit_code=True,
            ),
            marks=pytest.mark.config(
                TEAMCITY_MONITORING_AUTOMERGE_BRANCH_PROTECTION=['some_repo'],
            ),
            id='not_accepted_team_branch_restriction',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'somebody'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                        'number': 1011,
                    },
                ],
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/issues?labels={}'.format(
                                ACCEPT_LABEL,
                            )
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/somebody/'
                            'permission'
                        ),
                    },
                    {'method': 'GET', 'url': 'repos/taxi/some_repo'},
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/branches/develop/'
                            'protection'
                        ),
                    },
                ],
                collaborator_perm={'somebody': {'permission': 'write'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                branch_restriction={'fail': True},
                logger_error_list=[
                    'Failed to automerge issue some_url: '
                    'Cannot get info about branch restriction '
                    'in repo some_repo. '
                    'Robot needs at least admin permission. '
                    'Exception: Not defined in schema github response, '
                    'status: 400, body: b\'\'',
                ],
                has_exit_code=True,
            ),
            marks=pytest.mark.config(
                TEAMCITY_MONITORING_AUTOMERGE_BRANCH_PROTECTION=['some_repo'],
            ),
            id='team_branch_restriction_fail',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': 'lolkek',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': '', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'failure',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {'state': 'success', 'context': 'other check'},
                        ],
                    },
                },
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/issues?labels={}'.format(
                                ACCEPT_LABEL,
                            )
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                ],
            ),
            id='tests_not_passed',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': 'lolkek',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': '', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                            {'state': 'success', 'context': 'other check'},
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'judge'}, 'state': 'DISMISSED'},
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                        {
                            'user': {'login': 'mister_x'},
                            'state': 'CHANGES_REQUESTED',
                        },
                        {'user': {'login': 'madam_x'}, 'state': 'APPROVED'},
                    ],
                },
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/issues?labels={}'.format(
                                ACCEPT_LABEL,
                            )
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                ],
            ),
            id='not_approved',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 200,
                        'data': {
                            'sha': 'cc2f73',
                            'merged': False,
                            'message': 'Pull Request was not merged!!',
                        },
                    },
                },
                user_branches_info={'TAXICOMMON-893': {'protected': False}},
                delete_user_branch_status={'TAXICOMMON-893': 204},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                ],
                logger_error_list=[
                    'Failed to automerge issue some_url: '
                    'Failed to merge pull request 1011: '
                    'Pull Request was not merged!!',
                ],
                has_exit_code=True,
            ),
            id='error_merge',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 422,
                        'data': {
                            'message': 'Pull Request was not merged!!',
                            'documentation_url': 'documentation_url',
                        },
                    },
                },
                user_branches_info={'TAXICOMMON-893': {'protected': False}},
                delete_user_branch_status={'TAXICOMMON-893': 204},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'PATCH',
                        'url': 'repos/taxi/some_repo/issues/1011',
                        'json': {'labels': []},
                    },
                    {
                        'method': 'POST',
                        'url': 'repos/taxi/some_repo/issues/1011/comments',
                        'json': {
                            'body': (
                                'GithubError(message=\''
                                'Pull Request was not merged!!\', '
                                'documentation_url=\'documentation_url\', '
                                'url=None, status=None, errors=None)'
                            ),
                        },
                    },
                ],
                logger_error_list=[
                    'Failed to automerge issue some_url: '
                    'Cannot merge pull request from repo some_repo: '
                    'github response, status: 422, '
                    'body: GithubError('
                    'message=\'Pull Request was not merged!!\', '
                    'documentation_url=\'documentation_url\', url=None, '
                    'status=None, errors=None)',
                ],
                has_exit_code=True,
            ),
            id='failed_merge',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 405,
                        'data': {
                            'message': 'Pull Request was not merged!!',
                            'documentation_url': 'documentation_url',
                        },
                    },
                },
                user_branches_info={'TAXICOMMON-893': {'protected': False}},
                delete_user_branch_status={'TAXICOMMON-893': 204},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                ],
                logger_error_list=[
                    'Failed to automerge issue some_url: '
                    'Cannot merge pull request from repo some_repo: '
                    'Not defined in schema github response, status: 405, '
                    'body: b\'{"message": "Pull Request was not merged!!", '
                    '"documentation_url": "documentation_url"}\'',
                ],
                has_exit_code=True,
            ),
            id='base_branch_modified_merge',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                                'target_url': '',
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                                'target_url': '',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                                'target_url': '',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 200,
                        'data': {
                            'sha': 'cc2f73',
                            'merged': True,
                            'message': 'Pull Request was merged!!',
                        },
                    },
                },
                user_branches_info={
                    'TAXICOMMON-893': {
                        'protected': True,
                        'protection': {
                            'required_status_checks': {'contexts': []},
                        },
                    },
                },
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/some_genius/some_repo/branches/'
                            'TAXICOMMON-893'
                        ),
                    },
                ],
            ),
            id='delete_protected_branch',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 200,
                        'data': {
                            'sha': 'cc2f73',
                            'merged': True,
                            'message': 'Pull Request was merged!!',
                        },
                    },
                },
                user_branches_info={
                    'TAXICOMMON-893': {
                        'protected': False,
                        'protection': {
                            'required_status_checks': {'contexts': []},
                        },
                    },
                },
                delete_user_branch_status={'TAXICOMMON-893': 404},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/some_genius/some_repo/branches/'
                            'TAXICOMMON-893'
                        ),
                    },
                    {
                        'method': 'DELETE',
                        'url': (
                            'repos/some_genius/some_repo/git/refs/heads/'
                            'TAXICOMMON-893'
                        ),
                    },
                ],
            ),
            id='cannot_delete_branch',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 200,
                        'data': {
                            'sha': 'cc2f73',
                            'merged': True,
                            'message': 'Pull Request was merged!!',
                        },
                    },
                },
                user_branches_info={
                    'TAXICOMMON-893': {
                        'protected': False,
                        'protection': {
                            'required_status_checks': {'contexts': []},
                        },
                    },
                },
                delete_user_branch_status={'TAXICOMMON-893': 422},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/some_genius/some_repo/branches/'
                            'TAXICOMMON-893'
                        ),
                    },
                    {
                        'method': 'DELETE',
                        'url': (
                            'repos/some_genius/some_repo/git/refs/heads/'
                            'TAXICOMMON-893'
                        ),
                    },
                ],
            ),
            id='cannot_delete_already_deleted_branch',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready for quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'judge'}, 'state': 'DISMISSED'},
                        {'user': {'login': 'judge'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 200,
                        'data': {
                            'sha': 'cc2f73',
                            'merged': True,
                            'message': 'Pull Request was merged!!',
                        },
                    },
                },
                user_branches_info={
                    'TAXICOMMON-893': {
                        'protected': False,
                        'protection': {
                            'required_status_checks': {'contexts': []},
                        },
                    },
                },
                delete_user_branch_status={'TAXICOMMON-893': 204},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready for quorum '
                                'commit (#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/some_genius/some_repo/branches/'
                            'TAXICOMMON-893'
                        ),
                    },
                    {
                        'method': 'DELETE',
                        'url': (
                            'repos/some_genius/some_repo/git/refs/heads/'
                            'TAXICOMMON-893'
                        ),
                    },
                ],
            ),
            id='correct_merge',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'first_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                    {
                        'url': 'second_url',
                        'user': {'login': 'dumb'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/5763',
                        },
                        'number': 5763,
                    },
                    {'url': 'third_url', 'user': {'login': 'aselutin'}},
                    {
                        'url': 'forth_url',
                        'user': {'login': 'mister_x'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/666',
                        },
                    },
                ],
                collaborator_perm={
                    'some_genius': {'permission': 'admin'},
                    'dumb': {'permission': 'read'},
                    'mister_x': {'permission': 'write'},
                },
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                    '5763': {
                        'number': 5763,
                        'html_url': 'some_url',
                        'title': 'feat dumb: just remove label here',
                        'body': '* Remove\r\n* Automerge label\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-496', 'sha': 'ct267d'},
                    },
                    '666': {
                        'number': 666,
                        'html_url': 'some_url',
                        'title': 'feat some: some title',
                        'body': 'Some body',
                        'labels': [{'id': 789953, 'name': 'automerge'}],
                        'head': {'ref': 'TAXIQUEUE-1', 'sha': 'ee8538'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                    'ee8538': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {'state': 'success', 'context': 'tests'},
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '666': [
                        {
                            'user': {'login': 'mister_x'},
                            'state': 'CHANGES_REQUESTED',
                        },
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                    ],
                    '1011': [
                        {'user': {'login': 'judge'}, 'state': 'DISMISSED'},
                        {'user': {'login': 'judge'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 200,
                        'data': {
                            'sha': 'cc2f73',
                            'merged': True,
                            'message': 'Pull Request was merged!!',
                        },
                    },
                    '666': {
                        'status': 200,
                        'data': {
                            'sha': 'ee8538',
                            'merged': True,
                            'message': 'Pull Request successfully merged',
                        },
                    },
                },
                user_branches_info={
                    'TAXICOMMON-893': {
                        'protected': False,
                        'protection': {
                            'required_status_checks': {'contexts': []},
                        },
                    },
                    'TAXIQUEUE-1': {
                        'protected': True,
                        'protection': {
                            'required_status_checks': {'contexts': []},
                        },
                    },
                },
                delete_user_branch_status={'TAXICOMMON-893': 204},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/some_genius/some_repo/branches/'
                            'TAXICOMMON-893'
                        ),
                    },
                    {
                        'method': 'DELETE',
                        'url': (
                            'repos/some_genius/some_repo/git/refs/heads/'
                            'TAXICOMMON-893'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'dumb/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/5763',
                    },
                    {
                        'method': 'PATCH',
                        'url': 'repos/taxi/some_repo/issues/5763',
                        'json': {'labels': []},
                    },
                    {
                        'method': 'POST',
                        'url': 'repos/taxi/some_repo/issues/5763/comments',
                        'json': {'body': 'no_permission'},
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'mister_x/permission'
                        ),
                    },
                    {'method': 'GET', 'url': 'repos/taxi/some_repo/pulls/666'},
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/ee8538/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/666/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/666/merge',
                        'json': {
                            'commit_message': 'Some body',
                            'commit_title': 'feat some: some title (#666)',
                            'merge_method': 'squash',
                            'sha': 'ee8538',
                        },
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/mister_x/some_repo/branches/TAXIQUEUE-1',
                    },
                ],
                has_exit_code=True,
                logger_error_list=[
                    'Failed to automerge issue second_url: '
                    'Pull request is created by not accepted '
                    'user: dumb in repo: some_repo',
                ],
            ),
            id='several_pull_requests',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    [{'url': 'first_url', 'user': {'login': 'first_genius'}}],
                    [
                        {
                            'url': 'second_url',
                            'user': {'login': 'second_genius'},
                        },
                    ],
                    [{'url': 'third_url', 'user': {'login': 'third_genius'}}],
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                issues_labels_response_headers=[
                    {
                        'Link': (
                            '<https://some_addr/api/v3/repos/taxi/'
                            'some_repo/issues?page=2&labels=automerge>; '
                            'rel="next", '
                            '<https://some_addr/api/v3/repos/taxi/'
                            'some_repo/issues?page=3>; '
                            'rel="last"'
                        ),
                    },
                    {
                        'Link': (
                            '<https://some_addr/api/v3/repos/taxi/'
                            'some_repo/issues?labels=automerge&page=1>; '
                            'rel="prev", '
                            '<https://some_addr/api/v3/repos/taxi/'
                            'some_repo/issues?page=3>; '
                            'rel="next", '
                            '<https://some_addr/api/v3/repos/taxi/'
                            'some_repo/issues?page=3>; '
                            'rel="last", '
                            '<https://some_addr/api/v3/repos/taxi/'
                            'some_repo/issues?page=1>; '
                            'rel="first"'
                        ),
                    },
                    {
                        'Link': (
                            '<https://some_addr/api/v3/repos/taxi/'
                            'some_repo/issues?page=2&labels=automerge>; '
                            'rel="prev", '
                            '<https://some_addr/api/v3/repos/taxi/'
                            'some_repo/issues?page=1>; '
                            'rel="first"'
                        ),
                    },
                ],
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/issues?labels={}'.format(
                                ACCEPT_LABEL,
                            )
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/issues?labels=automerge'
                            '&page=2'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/issues?labels=automerge'
                            '&page=3'
                        ),
                    },
                ],
            ),
            id='not_pull_request_several_pages',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi-dwh/dwh/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready for quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'judge'}, 'state': 'DISMISSED'},
                        {'user': {'login': 'judge'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 200,
                        'data': {
                            'sha': 'cc2f73',
                            'merged': True,
                            'message': 'Pull Request was merged!!',
                        },
                    },
                },
                user_branches_info={
                    'TAXICOMMON-893': {
                        'protected': False,
                        'protection': {
                            'required_status_checks': {'contexts': []},
                        },
                    },
                },
                delete_user_branch_status={'TAXICOMMON-893': 204},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi-dwh/dwh/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi-dwh/dwh/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {'method': 'GET', 'url': 'repos/taxi-dwh/dwh/pulls/1011'},
                    {
                        'method': 'GET',
                        'url': 'repos/taxi-dwh/dwh/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi-dwh/dwh/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi-dwh/dwh/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi-dwh/dwh/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready for quorum '
                                'commit (#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/some_genius/dwh/branches/' 'TAXICOMMON-893'
                        ),
                    },
                    {
                        'method': 'DELETE',
                        'url': (
                            'repos/some_genius/dwh/git/refs/heads/'
                            'TAXICOMMON-893'
                        ),
                    },
                ],
            ),
            id='other_org_correct_merge',
            marks=pytest.mark.config(
                TEAMCITY_MONITORING_AUTOMERGE_REPOS=['taxi-dwh/dwh'],
            ),
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 200,
                        'data': {
                            'sha': 'cc2f73',
                            'merged': True,
                            'message': 'Pull Request was merged!!',
                        },
                    },
                },
                user_branches_info={'TAXICOMMON-893': {'status': 404}},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum '
                                'commit (#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/some_genius/some_repo/branches/'
                            'TAXICOMMON-893'
                        ),
                    },
                ],
            ),
            id='no_branch_deleted',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': (
                            '* <b>Very</b> important commit message\r\n'
                            '<span id="devexp-content-start"></span>\r\n'
                            '****\r\n'
                            '<div class="devexp content"></div>\r\n'
                            '<span id="devexp-content-start"></span>\r\n'
                        ),
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 200,
                        'data': {
                            'sha': 'cc2f73',
                            'merged': True,
                            'message': 'Pull Request was merged!!',
                        },
                    },
                },
                user_branches_info={'TAXICOMMON-893': {'status': 404}},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': (
                                '* <b>Very</b> important commit message'
                            ),
                            'commit_title': (
                                'feat postgres: get ready'
                                ' quorum commit (#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/some_genius/some_repo/branches/'
                            'TAXICOMMON-893'
                        ),
                    },
                ],
            ),
            id='sanitize_pr_body',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 422,
                        'data': {
                            'message': (
                                'Could not merge because a Git pre-receive '
                                'hook failed.\n\nbackend/bootstrap.sh: '
                                'execution exceeded 10s timeout\n'
                            ),
                            'documentation_url': 'documentation_url',
                        },
                    },
                },
                user_branches_info={'TAXICOMMON-893': {'protected': False}},
                delete_user_branch_status={'TAXICOMMON-893': 204},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                ],
                logger_error_list=[
                    'Failed to automerge issue some_url: '
                    'Cannot merge pull request from repo '
                    'some_repo: github response, status: 422, body: '
                    'GithubError('
                    'message=\'Could not merge because a Git pre-receive hook '
                    'failed.\\n\\nbackend/bootstrap.sh: '
                    'execution exceeded 10s timeout\\n\', '
                    'documentation_url=\'documentation_url\', url=None, '
                    'status=None, errors=None)',
                ],
                has_exit_code=True,
            ),
            id='style_check_timeout',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={'1011': {'is_timeout': True}},
                user_branches_info={'TAXICOMMON-893': {'protected': False}},
                delete_user_branch_status={'TAXICOMMON-893': 204},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                ],
                logger_error_list=[
                    'Failed to automerge issue some_url: '
                    'Cannot merge pull request from repo some_repo: '
                    'Timeout Error',
                ],
                has_exit_code=True,
                has_merge_timeout=True,
            ),
            id='timeout_merge',
        ),
        pytest.param(
            Params(
                issues_labels_response=[
                    {
                        'url': 'some_url',
                        'user': {'login': 'some_genius'},
                        'pull_request': {
                            'url': 'repos/taxi/some_repo/pulls/1011',
                        },
                    },
                ],
                collaborator_perm={'some_genius': {'permission': 'admin'}},
                pulls_info={
                    '1011': {
                        'number': 1011,
                        'html_url': 'some_url',
                        'title': 'feat postgres: get ready quorum commit',
                        'body': '* Don\'t use slaves\r\n* Treat\r\n',
                        'labels': [{'name': 'automerge'}],
                        'head': {'ref': 'TAXICOMMON-893', 'sha': 'cc2f73'},
                    },
                },
                commits_statuses_sha_info={
                    'cc2f73': {
                        'statuses': [
                            {
                                'state': 'success',
                                'context': (
                                    'continuous-integration/db_settings'
                                ),
                            },
                            {
                                'state': 'success',
                                'context': 'submodules-check',
                            },
                            {
                                'state': 'success',
                                'context': 'additional check',
                            },
                        ],
                    },
                },
                pulls_reviews_info={
                    '1011': [
                        {'user': {'login': 'mister_x'}, 'state': 'APPROVED'},
                    ],
                },
                pulls_merge_info={
                    '1011': {
                        'status': 500,
                        'data': {
                            'message': 'Pull Request was not merged!!',
                            'documentation_url': 'documentation_url',
                        },
                    },
                },
                user_branches_info={'TAXICOMMON-893': {'protected': False}},
                delete_user_branch_status={'TAXICOMMON-893': 204},
                expected_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/issues?labels=automerge',
                    },
                    {
                        'method': 'GET',
                        'url': (
                            'repos/taxi/some_repo/collaborators/'
                            'some_genius/permission'
                        ),
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/commits/cc2f73/status',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches/develop',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls/1011/reviews',
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                    {
                        'method': 'PUT',
                        'url': 'repos/taxi/some_repo/pulls/1011/merge',
                        'json': {
                            'commit_message': '* Don\'t use slaves\n* Treat',
                            'commit_title': (
                                'feat postgres: get ready quorum commit '
                                '(#1011)'
                            ),
                            'merge_method': 'squash',
                            'sha': 'cc2f73',
                        },
                    },
                ],
                logger_error_list=[
                    'Failed to automerge issue some_url: '
                    'Cannot merge pull request from repo some_repo: '
                    'Not defined in schema github response, status: 500, '
                    'body: b\'{"message": "Pull Request was not merged!!", '
                    '"documentation_url": "documentation_url"}\'',
                ],
                has_exit_code=True,
            ),
            id='internal_server_error_merge',
        ),
    ],
)
@pytest.mark.config(
    TEAMCITY_MONITORING_AUTOMERGE_ENABLED=True,
    TEAMCITY_MONITORING_AUTOMERGE_REQUIRED_CHECKS={
        GITHUB_REPO: ('additional check',),
    },
    TEAMCITY_MONITORING_AUTOMERGE_MERGE_FAIL_MESSAGE='{exception}',
    TEAMCITY_MONITORING_AUTOMERGE_PERMISSION_ABSENSE_MESSAGE='no_permission',
    TEAMCITY_MONITORING_AUTOMERGE_BRANCH_PROTECTION=['userver'],
    TEAMCITY_MONITORING_AUTOMERGE_REPOS=[GITHUB_REPO],
)
def test_automerge_cron(
        monkeypatch,
        patch_aiohttp_session,
        response_mock,
        mock_github,
        params: Params,
):
    @mock_github(GITHUB_API_PREFIX, prefix=True)
    async def github_request(request):
        if GITHUB_API_REPOS in request.path:
            github_api_suffix = request.path.split(GITHUB_API_REPOS)[1]
        else:
            github_api_suffix = request.path.split(GITHUB_API_PREFIX)[1]

        if github_api_suffix in ('taxi/some_repo', 'taxi-dwh/dwh'):
            return web.json_response({'default_branch': 'develop'})
        if github_api_suffix.startswith('teams'):
            command_parts = github_api_suffix.split('/')
            team_id = command_parts[1]
            last_part = command_parts[-1]
            if last_part == 'members':
                return web.json_response(params.teams_members[team_id])

        owner, _, command = github_api_suffix.split('/', maxsplit=2)
        auth_token = request.headers['Authorization']
        assert auth_token == 'Token ' + GITHUB_TOKEN, 'Incorrect token'
        if owner not in (GITHUB_ORG, GITHUB_DWH_ORG):
            if command.startswith('branches'):
                pr_branch = command.split('/')[1]
                branch_info = params.user_branches_info[pr_branch]
                status = branch_info.get('status', 200)
                return web.json_response(branch_info, status=status)
            if command.startswith('git/refs/heads'):
                pr_branch = command.split('/')[-1]
                return web.json_response(
                    status=params.delete_user_branch_status[pr_branch],
                    data={
                        'message': 'Some message',
                        'documentation_url': 'documentation_url',
                    },
                )
        if command.startswith('issues/'):
            method = request.method
            if method == 'POST':
                return web.json_response(
                    status=201, data={'body': 'some_text'},
                )
            if method == 'PATCH':
                return web.json_response({'url': 'u', 'user': {'login': 's'}})
            assert False, '%s is unknown command' % command
        if command.startswith('issues'):
            assert request.args['labels'] == ACCEPT_LABEL
            if not params.issues_labels_response_headers:
                return web.json_response(data=params.issues_labels_response)
            request_url = request.url
            query = urlparse.urlparse(request_url).query
            parsed_query = urlparse.parse_qs(query)

            if 'page' not in parsed_query:
                page_no = 0
            else:
                page_no = int(parsed_query['page'][0]) - 1
            return web.json_response(
                data=params.issues_labels_response[page_no],
                headers=params.issues_labels_response_headers[page_no],
            )
        if command.startswith('pulls'):
            command_parts = command.split('/')
            pr_number = command_parts[1]
            last_part = command_parts[-1]
            if last_part == 'reviews':
                return web.json_response(params.pulls_reviews_info[pr_number])
            if last_part == 'merge':
                merge_info = params.pulls_merge_info[pr_number]
                return web.json_response(
                    status=merge_info['status'], data=merge_info['data'],
                )
            return web.json_response(params.pulls_info[pr_number])
        if command.startswith('commits'):
            sha = command.split('/')[1]
            return web.json_response(params.commits_statuses_sha_info[sha])
        if command == 'branches/develop':
            return web.json_response(BRANCHES_DEVELOP_INFO)
        if command.startswith('collaborators'):
            user = command.split('/')[1]
            user_perm = params.collaborator_perm[user]
            if user_perm.get('fail'):
                return web.json_response(status=400)
            return web.json_response(user_perm)
        if command == 'branches/develop/protection':
            if params.branch_restriction.get('fail'):
                return web.json_response(status=400)
            return web.json_response(params.branch_restriction)

        assert False, '%s is unknown path' % github_api_suffix

    monkeypatch.setattr(
        'taxi.settings.Settings.GITHUB_API_URL', GITHUB_API_BASE,
    )

    if params.has_merge_timeout:

        def fail_merge_mock(*args, **kwargs):
            raise github.ClientException('Timeout Error')

        monkeypatch.setattr(
            github.GithubClient, 'merge_pull_request', fail_merge_mock,
        )

    _logger_error_messages = []
    original_logger_error = run_automerge_cron.logger.error

    def _wrapper_logger_error(*args, **kwargs):
        log_str = args[0]
        output_string = log_str % args[1:]
        _logger_error_messages.append(output_string)
        return original_logger_error(*args, **kwargs)

    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.'
        'automerge_cron.run_automerge_cron.logger.error',
        _wrapper_logger_error,
    )

    if params.has_exit_code:
        with pytest.raises(run_automerge_cron.AutomergeError):
            run_cron.main(
                [
                    'taxi_teamcity_monitoring.crontasks.'
                    'automerge_cron.run_automerge_cron',
                    '-t',
                    '0',
                ],
            )
    else:
        run_cron.main(
            [
                'taxi_teamcity_monitoring.crontasks.'
                'automerge_cron.run_automerge_cron',
                '-t',
                '0',
            ],
        )

    github_calls = []
    while github_request.has_calls:
        gh_req = github_request.next_call()['request']
        short_url = str(gh_req.url).split('/', maxsplit=6)[6]
        data = {'method': gh_req.method, 'url': short_url}
        gh_req_json = None
        try:
            gh_req_json = gh_req.json
        except json.JSONDecodeError:
            pass
        if gh_req_json:
            data['json'] = gh_req_json

        github_calls.append(data)

    assert github_calls == params.expected_calls

    assert _logger_error_messages == params.logger_error_list


@pytest.mark.config(
    TEAMCITY_MONITORING_AUTOMERGE_ENABLED=True,
    TEAMCITY_MONITORING_AUTOMERGE_REQUIRED_CHECKS={
        GITHUB_REPO: ('additional check',),
    },
    TEAMCITY_MONITORING_AUTOMERGE_PERMISSION_ABSENSE_MESSAGE='no_permission',
    TEAMCITY_MONITORING_AUTOMERGE_BRANCH_PROTECTION=['userver'],
    TEAMCITY_MONITORING_AUTOMERGE_REPOS=[GITHUB_REPO],
)
def test_token_absence(
        monkeypatch,
        patch_aiohttp_session,
        response_mock,
        mock_github,
        simple_secdist,
):
    simple_secdist['settings_override'].pop('GITHUB_TOKEN')

    @mock_github(GITHUB_API_PREFIX, prefix=True)
    async def github_request(request):
        auth_token = request.headers.get('Authorization', None)
        assert not auth_token, 'There should not be any token'
        return []

    run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'automerge_cron.run_automerge_cron',
            '-t',
            '0',
        ],
    )

    assert github_request.times_called == 1
    gh_req = github_request.next_call()['request']
    short_url = str(gh_req.url).split('/', maxsplit=6)[6]
    assert short_url == 'repos/taxi/some_repo/issues?labels=automerge'


@pytest.mark.parametrize(
    'source,result',
    [
        pytest.param('a < b > c', 'a < b > c', id='not-a-tag'),
        pytest.param('<\n\n\n>', '<\n\n\n>', id='multiline not-a-tag'),
        pytest.param('foo\n  ****  \n', 'foo', id='match stars'),
        pytest.param('foo\n<\n>\n', 'foo\n<\n>', id='newlines'),
        pytest.param('foo\n<div>\n', 'foo', id='match tag'),
        pytest.param(
            'foo\n<div></div>  \n **** \n <bar>', 'foo', id='match complex',
        ),
        pytest.param(
            '**** foo \nfoo ****  \n <p> foo \nfoo <p>\n',
            '**** foo \nfoo ****  \n <p> foo \nfoo <p>',
            id='not match complex',
        ),
        pytest.param(
            'foo\n* [foo](http://bar/)', 'foo\n* foo', id='replace links',
        ),
    ],
)
def test_sanitize_body(source, result):
    assert run_automerge_cron.sanitize_body(source) == result
