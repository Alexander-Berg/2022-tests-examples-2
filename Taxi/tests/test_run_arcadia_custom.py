# pylint: disable=too-many-lines
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

import freezegun
import pytest

import run_arcadia_custom
from taxi_buildagent.clients import arcadia as arcadia_client
from tests.plugins import arc
from tests.utils.examples import arcadia


class Params(NamedTuple):
    arc_calls: List[str]
    log_json: str
    exp_changelog: str
    base_changelog: str
    arcadia_prs: str
    exp_arcadia_calls: List[Dict[str, Any]] = [
        {
            'kwargs': {
                'headers': {'Authorization': 'OAuth some-token'},
                'params': {
                    'fields': (
                        'review_requests(id,author,summary,'
                        'vcs(from_branch,to_branch),'
                        'checks(system,type,status,updated_at,alias),labels,'
                        'description)'
                    ),
                    'query': (
                        'label(taxi/deploy:testing);open();path(/taxi|/'
                        'schemas/schemas)'
                    ),
                    'limit': 10000,
                },
            },
            'method': 'get',
            'url': arcadia_client.API_URL + 'v1/review-requests',
        },
    ]
    changed_files_by_commit: Dict[str, List[str]] = {}
    tc_report_build_number: List[Dict[str, Any]] = [
        {'build_number': '0.0.0testing123'},
    ]
    tc_set_parameters: List[Dict[str, Any]] = []
    tc_report_problems: List[Dict[str, Any]] = []
    build_number: int = 123
    deploy_branch: str = 'testing'
    pr_label: Optional[str] = None
    service_name: str = 'test-service'
    are_all_prs: bool = True
    is_several_projects: bool = False
    rebase_fails: List[Tuple[str, bool]] = []
    versioning: str = 'changelog'
    test_contexts: List[str] = []


@freezegun.freeze_time('2020-09-01 20:59:59', tz_offset=3)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                arc_calls=[
                    'arc info --json',
                    'arc info --json',
                    'arc info --json',
                    'arc checkout trunk',
                    'arc checkout -b '
                    'users/robot-taxi-teamcity/uservices/test-service '
                    'arcadia/trunk -f',
                    'arc info',
                    'arc info --json',
                    'arc fetch trunk',
                    'arc info --json',
                    'arc merge-base'
                    ' arcadia/users/robot-taxi-teamcity/uservices/test-service'
                    ' arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5'
                    ' arcadia/users/robot-taxi-teamcity/uservices/test-service'
                    '..arcadia/trunk $workdir',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service..arcadia/trunk $schemas_dir',
                ],
                exp_arcadia_calls=[
                    {
                        'kwargs': {
                            'headers': {'Authorization': 'OAuth some-token'},
                            'params': {
                                'fields': (
                                    'review_requests(id,author,summary,'
                                    'vcs(from_branch,to_branch),'
                                    'checks(system,type,status,updated_at,'
                                    'alias),labels,description)'
                                ),
                                'limit': 10000,
                                'query': (
                                    'label(taxi/deploy:tanker);open();'
                                    'path(/taxi|/schemas/schemas)'
                                ),
                            },
                        },
                        'method': 'get',
                        'url': (
                            'http://a.yandex-team.ru/api/v1/review-requests'
                        ),
                    },
                ],
                log_json='log1.json',
                exp_changelog='exp_changelog1.txt',
                base_changelog='base_changelog.txt',
                arcadia_prs='arcadia_no_prs.json',
                deploy_branch='tanker',
                tc_report_build_number=[{'build_number': '0.0.0tanker123'}],
            ),
            id='no_commits_custom_branch',
        ),
        pytest.param(
            Params(
                arc_calls=[
                    'arc info --json',
                    'arc info --json',
                    'arc info --json',
                    'arc checkout trunk',
                    'arc checkout -b '
                    'users/robot-taxi-teamcity/uservices/test-service '
                    'arcadia/trunk -f',
                    'arc info',
                    'arc info --json',
                    'arc fetch trunk',
                    'arc fetch users/dteterin/edit-README-only users/'
                    'alberist/ololo',
                    'arc branch -f tmp users/dteterin/edit-README-only',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/dteterin/edit-README-only '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat README: edit\n\n\n\n'
                    'REVIEW: 1234 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc branch -D tmp',
                    'arc branch -f tmp users/alberist/ololo',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/alberist/ololo '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat ololo: ololo\n\n\n\n'
                    'REVIEW: 5678 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc branch -D tmp',
                    'arc merge-base arcadia/trunk arcadia/users/'
                    'dteterin/edit-README-only',
                    'arc rev-parse arcadia/users/dteterin/edit-README-only',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users'
                    '/dteterin/edit-README-only '
                    '$workdir',
                    'arc merge-base arcadia/trunk arcadia/users/'
                    'alberist/ololo',
                    'arc rev-parse arcadia/users/alberist/ololo',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/'
                    'alberist/ololo '
                    '$workdir',
                    'arc info --json',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$workdir',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$schemas_dir',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 45329c^ 45329c $workdir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 98989f^ 98989f $schemas_dir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 12345a^ 12345a $schemas_dir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 98989f^ 98989f $schemas_dir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                    'arc diff 75757d^ 75757d $schemas_dir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                ],
                changed_files_by_commit={
                    '12345a': [
                        'taxi/services/test-service/service.yaml',
                        'taxi/services/test-service/src/main.cpp',
                    ],
                    '98989f': ['taxi/services/driver-authorizer/service.yaml'],
                    '75757d': ['taxi/services.yaml'],
                    '45329c': ['taxi/services/test-service/debian/changelog'],
                    'aaaaa': ['taxi/services.yaml'],
                },
                log_json='log2.json',
                exp_changelog='exp_changelog2.txt',
                base_changelog='base_changelog.txt',
                arcadia_prs='arcadia_prs1.json',
                tc_set_parameters=[
                    {
                        'name': 'env.AFFECTED_USERS',
                        'value': 'alberist dteterin',
                    },
                    {
                        'name': 'env.CUSTOM_MERGED_PULL_REQUESTS_REPORT',
                        'value': (
                            '[{"number": 1234, "url": '
                            '"https://a.yandex-team.ru/review/1234", '
                            '"staff_user": "dteterin", "title": '
                            '"feat README: edit", '
                            '"labels": ["custom/label"], '
                            '"from_branch": "users/dteterin/edit-README-only"'
                            '}, {"number": 5678, "url": '
                            '"https://a.yandex-team.ru/review/5678", '
                            '"staff_user": "alberist", "title": '
                            '"feat ololo: ololo", '
                            '"labels": ["custom/label"], '
                            '"from_branch": "users/alberist/ololo"}]'
                        ),
                    },
                ],
            ),
            id='main_case',
        ),
        pytest.param(
            Params(
                pr_label='custom/label',
                exp_arcadia_calls=[
                    {
                        'kwargs': {
                            'headers': {'Authorization': 'OAuth some-token'},
                            'params': {
                                'fields': (
                                    'review_requests(id,author,summary,'
                                    'vcs(from_branch,to_branch),'
                                    'checks(system,type,status,updated_at,'
                                    'alias),labels,description)'
                                ),
                                'query': (
                                    'label(custom/label);open();path(/taxi|'
                                    '/schemas/schemas)'
                                ),
                                'limit': 10000,
                            },
                        },
                        'method': 'get',
                        'url': arcadia_client.API_URL + 'v1/review-requests',
                    },
                ],
                arc_calls=[
                    'arc info --json',
                    'arc info --json',
                    'arc info --json',
                    'arc checkout trunk',
                    'arc checkout -b '
                    'users/robot-taxi-teamcity/uservices/test-service '
                    'arcadia/trunk -f',
                    'arc info',
                    'arc info --json',
                    'arc fetch trunk',
                    'arc fetch users/dteterin/edit-README-only users/'
                    'alberist/ololo',
                    'arc merge-base arcadia/trunk users/dteterin/'
                    'edit-README-only',
                    'arc diff cbabc1 users/dteterin/edit-README-only '
                    '$workdir '
                    '--name-only',
                    'arc merge-base arcadia/trunk users/alberist/ololo',
                    'arc diff cbabc1 users/alberist/ololo '
                    '$workdir '
                    '--name-only',
                    'arc branch -f tmp users/dteterin/edit-README-only',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/dteterin/edit-README-only '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat README: edit\n\n\n\n'
                    'REVIEW: 1234 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc branch -D tmp',
                    'arc branch -f tmp users/alberist/ololo',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/alberist/ololo '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat ololo: ololo\n\n\n\n'
                    'REVIEW: 5678 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc checkout users/robot-taxi-teamcity/uservices'
                    '/test-service',
                    'arc branch -D tmp',
                    'arc merge-base arcadia/trunk arcadia/users/dteterin/'
                    'edit-README-only',
                    'arc rev-parse arcadia/users/dteterin/edit-README-only',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/dteterin/'
                    'edit-README-only '
                    '$workdir',
                    'arc merge-base arcadia/trunk arcadia/users/'
                    'alberist/ololo',
                    'arc rev-parse arcadia/users/alberist/ololo',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/'
                    'alberist/ololo '
                    '$workdir',
                    'arc info --json',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$workdir',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$schemas_dir',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 45329c^ 45329c $workdir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 98989f^ 98989f $schemas_dir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 12345a^ 12345a $schemas_dir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 98989f^ 98989f $schemas_dir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                    'arc diff 75757d^ 75757d $schemas_dir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                ],
                changed_files_by_commit={
                    '12345a': [
                        'taxi/services/test-service/service.yaml',
                        'taxi/services/test-service/src/main.cpp',
                    ],
                    '98989f': ['taxi/services/driver-authorizer/service.yaml'],
                    '75757d': ['taxi/services.yaml'],
                    '45329c': ['taxi/services/test-service/debian/changelog'],
                    'aaaaa': ['taxi/services.yaml'],
                    'users/dteterin/edit-README-only': [
                        'taxi/services/test-service/src/some.cpp',
                    ],
                    'users/alberist/ololo': ['taxi/services.yml'],
                },
                log_json='log2.json',
                exp_changelog='exp_changelog3.txt',
                base_changelog='base_changelog.txt',
                arcadia_prs='arcadia_prs1.json',
                tc_set_parameters=[
                    {
                        'name': 'env.AFFECTED_USERS',
                        'value': 'alberist dteterin',
                    },
                    {
                        'name': 'env.CUSTOM_MERGED_PULL_REQUESTS_REPORT',
                        'value': (
                            '[{"number": 1234, "url": '
                            '"https://a.yandex-team.ru/review/1234", '
                            '"staff_user": "dteterin", "title": '
                            '"feat README: edit", "labels": ["custom/label"],'
                            ' "from_branch": "users/dteterin/edit-README-only"'
                            '}, {"number": 5678, "url": '
                            '"https://a.yandex-team.ru/review/5678", '
                            '"staff_user": "alberist", "title": '
                            '"feat ololo: ololo", "labels": '
                            '["custom/label"], "from_branch": '
                            '"users/alberist/ololo"}]'
                        ),
                    },
                ],
                are_all_prs=False,
            ),
            id='filter_some_prs',
        ),
        pytest.param(
            Params(
                arc_calls=[
                    'arc info --json',
                    'arc info --json',
                    'arc info --json',
                    'arc checkout trunk',
                    'arc checkout -b '
                    'users/robot-taxi-teamcity/uservices/telematics '
                    'arcadia/trunk -f',
                    'arc info',
                    'arc info --json',
                    'arc fetch trunk',
                    'arc fetch users/dteterin/edit-some-telematics users/'
                    'alberist/graph '
                    'users/abc/driver-authorizer',
                    'arc merge-base arcadia/trunk users/dteterin/'
                    'edit-some-telematics',
                    'arc diff cbabc1 users/dteterin/edit-some-telematics '
                    '$workdir '
                    '--name-only',
                    'arc merge-base arcadia/trunk users/alberist/graph',
                    'arc diff cbabc1 users/alberist/graph '
                    '$workdir '
                    '--name-only',
                    'arc merge-base arcadia/trunk users/abc/driver-authorizer',
                    'arc diff cbabc1 users/abc/driver-authorizer '
                    '$workdir '
                    '--name-only',
                    'arc branch -f tmp users/dteterin/edit-some-telematics',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/dteterin/edit-some-telematics '
                    'users/robot-taxi-teamcity/uservices/telematics',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat telematics: edit\n\n\n\n'
                    'REVIEW: 4893 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'telematics tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/telematics tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'telematics',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'telematics',
                    'arc branch -D tmp',
                    'arc branch -f tmp users/alberist/graph',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/alberist/graph '
                    'users/robot-taxi-teamcity/uservices/telematics',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat graph: otdelenie\n\n\n\n'
                    'REVIEW: 3846 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'telematics tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/telematics tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'telematics',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'telematics',
                    'arc branch -D tmp',
                    'arc branch -f tmp users/abc/driver-authorizer',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/abc/driver-authorizer '
                    'users/robot-taxi-teamcity/uservices/telematics',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat driver-authorizer: qwerty\n'
                    '\n'
                    '\n'
                    '\n'
                    'REVIEW: 3846 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'telematics tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/telematics tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'telematics',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'telematics',
                    'arc branch -D tmp',
                    'arc merge-base arcadia/trunk arcadia/users/dteterin/'
                    'edit-some-telematics',
                    'arc rev-parse arcadia/users/dteterin/'
                    'edit-some-telematics',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/dteterin/'
                    'edit-some-telematics '
                    '$workdir',
                    'arc merge-base arcadia/trunk arcadia/users/'
                    'alberist/graph',
                    'arc rev-parse arcadia/users/alberist/graph',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/'
                    'alberist/graph '
                    '$workdir',
                    'arc merge-base arcadia/trunk arcadia/users/abc/'
                    'driver-authorizer',
                    'arc rev-parse arcadia/users/abc/driver-authorizer',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/abc/'
                    'driver-authorizer '
                    '$workdir',
                    'arc info --json',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/telematics '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'telematics..arcadia/trunk '
                    '$workdir',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/telematics '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'telematics..arcadia/trunk '
                    '$graphdir',
                    'arc merge-base arcadia/users/robot-taxi-teamcity'
                    '/uservices/telematics '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'telematics..arcadia/trunk '
                    '$servicedir',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 45329c^ 45329c $workdir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                ],
                changed_files_by_commit={
                    '12345a': [
                        'taxi/services/test-service/service.yaml',
                        'taxi/services/test-service/src/main.cpp',
                    ],
                    '98989f': ['taxi/services/driver-authorizer/service.yaml'],
                    '75757d': ['taxi/services.yaml'],
                    '45329c': ['taxi/services/test-service/debian/changelog'],
                    'aaaaa': ['taxi/services.yaml'],
                    'users/dteterin/edit-some-only': [
                        'taxi/services/test-service/src/some.cpp',
                    ],
                    'users/dteterin/edit-some-telematics': [
                        'taxi/telematics/some.cpp',
                    ],
                    'users/alberist/graph': ['taxi/graph/other.yml'],
                    'users/abc/driver-authorizer': [
                        'taxi/services/driver-authorizer/another.yaml',
                    ],
                },
                service_name='telematics',
                log_json='log2.json',
                exp_changelog='exp_changelog_telematics.txt',
                base_changelog='base_changelog.txt',
                arcadia_prs='arcadia_telematics_prs.json',
                exp_arcadia_calls=[
                    {
                        'kwargs': {
                            'headers': {'Authorization': 'OAuth some-token'},
                            'params': {
                                'fields': (
                                    'review_requests(id,author,summary,'
                                    'vcs(from_branch,to_branch),'
                                    'checks(system,type,status,updated_at,'
                                    'alias),labels,description)'
                                ),
                                'query': (
                                    'label(taxi/deploy:testing);open();'
                                    'path(/taxi/telematics|/taxi/graph|'
                                    '/taxi/services/driver-authorizer)'
                                ),
                                'limit': 10000,
                            },
                        },
                        'method': 'get',
                        'url': arcadia_client.API_URL + 'v1/review-requests',
                    },
                ],
                tc_set_parameters=[
                    {
                        'name': 'env.AFFECTED_USERS',
                        'value': 'alberist dteterin vitja',
                    },
                    {
                        'name': 'env.CUSTOM_MERGED_PULL_REQUESTS_REPORT',
                        'value': (
                            '[{"number": 4893, '
                            '"url": "https://a.yandex-team.ru/review/4893", '
                            '"staff_user": "dteterin", '
                            '"title": "feat telematics: edit", '
                            '"labels": [], '
                            '"from_branch": '
                            '"users/dteterin/edit-some-telematics"}, '
                            '{"number": 3846, '
                            '"url": "https://a.yandex-team.ru/review/3846", '
                            '"staff_user": "alberist", '
                            '"title": "feat graph: otdelenie", '
                            '"labels": [], '
                            '"from_branch": "users/alberist/graph"}, '
                            '{"number": 3846, "url": '
                            '"https://a.yandex-team.ru/review/3846", '
                            '"staff_user": "vitja", '
                            '"title": "feat driver-authorizer: qwerty", '
                            '"labels": [], '
                            '"from_branch": "users/abc/driver-authorizer"}]'
                        ),
                    },
                ],
                are_all_prs=False,
                is_several_projects=True,
            ),
            id='additional_projects_case',
        ),
        pytest.param(
            Params(
                arc_calls=[
                    'arc info --json',
                    'arc info --json',
                    'arc info --json',
                    'arc checkout trunk',
                    'arc checkout -b '
                    'users/robot-taxi-teamcity/uservices/test-service '
                    'arcadia/trunk -f',
                    'arc info',
                    'arc info --json',
                    'arc fetch trunk',
                    'arc fetch users/dteterin/edit-README-only users/'
                    'gilfanovii/s-th '
                    'users/alberist/ololo',
                    'arc branch -f tmp users/dteterin/edit-README-only',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/dteterin/edit-README-only '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat README: edit\n\n\n\n'
                    'REVIEW: 1234 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc branch -D tmp',
                    'arc branch -f tmp users/gilfanovii/s-th',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/gilfanovii/s-th '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat s-th: s-th\n\n\n\n'
                    'REVIEW: 9012 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc rebase --abort',
                    'arc reset --hard --force',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc branch -D tmp',
                    'arc info --json',
                    'arc checkout -b tmp_trunk trunk -f',
                    'arc branch -f tmp users/gilfanovii/s-th',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/gilfanovii/s-th tmp_trunk',
                    'arc reset --soft cbabc1',
                    'arc commit --message Squash branch users/gilfanovii/s-th '
                    'to merge base with branch tmp_trunk --force',
                    'arc info --json',
                    'arc rebase tmp_trunk tmp --force',
                    'arc rebase --abort',
                    'arc reset --hard --force',
                    'arc checkout tmp_trunk',
                    'arc branch -D tmp',
                    'arc info --json',
                    'arc branch -f tmp users/alberist/ololo',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/alberist/ololo '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat ololo: ololo\n\n\n\n'
                    'REVIEW: 5678 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc branch -D tmp',
                    'arc merge-base arcadia/trunk arcadia/users/dteterin/'
                    'edit-README-only',
                    'arc rev-parse arcadia/users/dteterin/edit-README-only',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/dteterin/'
                    'edit-README-only '
                    '$workdir',
                    'arc merge-base arcadia/trunk arcadia/users/'
                    'alberist/ololo',
                    'arc rev-parse arcadia/users/alberist/ololo',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/'
                    'alberist/ololo '
                    '$workdir',
                    'arc info --json',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$workdir',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$schemas_dir',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 45329c^ 45329c $workdir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 98989f^ 98989f $schemas_dir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                    'arc diff 90909g^ 90909g $workdir --name-only',
                    'arc diff 90909g^ 90909g $schemas_dir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 12345a^ 12345a $schemas_dir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 98989f^ 98989f $schemas_dir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                    'arc diff 75757d^ 75757d $schemas_dir --name-only',
                    'arc diff 90909g^ 90909g $workdir --name-only',
                    'arc diff 90909g^ 90909g $schemas_dir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                ],
                changed_files_by_commit={
                    '12345a': [
                        'taxi/services/test-service/service.yaml',
                        'taxi/services/test-service/src/main.cpp',
                    ],
                    '98989f': ['taxi/services/driver-authorizer/service.yaml'],
                    '90909g': ['taxi/services/driver-authorizer/service.yaml'],
                    '75757d': ['taxi/services.yaml'],
                    '45329c': ['taxi/services/test-service/debian/changelog'],
                    'aaaaa': ['taxi/services.yaml'],
                },
                log_json='log3.json',
                exp_changelog='exp_changelog2.txt',
                base_changelog='base_changelog.txt',
                arcadia_prs='arcadia_prs3.json',
                tc_set_parameters=[
                    {
                        'name': 'env.AFFECTED_USERS',
                        'value': 'alberist dteterin gilfanovii',
                    },
                    {
                        'name': 'env.CUSTOM_BUILD_REPORT',
                        'value': (
                            '[{"pull_request": {"number": 9012, '
                            '"url": "https://a.yandex-team.ru/review/9012", '
                            '"staff_user": "gilfanovii", '
                            '"title": "feat s-th: s-th", "labels": [], '
                            '"from_branch": "users/gilfanovii/s-th"}, '
                            '"reason": "conflict with develop", '
                            '"category": 3, "other_pr": null}]'
                        ),
                    },
                    {
                        'name': 'env.CUSTOM_MERGED_PULL_REQUESTS_REPORT',
                        'value': (
                            '[{"number": 1234, "url": '
                            '"https://a.yandex-team.ru/review/1234", '
                            '"staff_user": "dteterin", "title": '
                            '"feat README: edit", "labels": [], '
                            '"from_branch": "users/dteterin/edit-README-only"'
                            '}, {"number": 5678, "url": '
                            '"https://a.yandex-team.ru/review/5678", '
                            '"staff_user": "alberist", "title": '
                            '"feat ololo: ololo", "labels": [], '
                            '"from_branch": "users/alberist/ololo"}]'
                        ),
                    },
                ],
                rebase_fails=[
                    ('rabase of users/dteterin/edit-README-only', False),
                    ('rabase of users/gilfanovii/s-th', True),
                    ('rabase on trunk', True),
                    ('rabase of users/alberist/ololo', False),
                ],
            ),
            id='conflict_with_develop',
        ),
        pytest.param(
            Params(
                arc_calls=[
                    'arc info --json',
                    'arc info --json',
                    'arc info --json',
                    'arc checkout trunk',
                    'arc checkout -b '
                    'users/robot-taxi-teamcity/uservices/test-service '
                    'arcadia/trunk -f',
                    'arc info',
                    'arc info --json',
                    'arc fetch trunk',
                    'arc fetch users/dteterin/edit-README-only users/'
                    'gilfanovii/s-th '
                    'users/alberist/ololo',
                    'arc branch -f tmp users/dteterin/edit-README-only',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/dteterin/edit-README-only '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat README: edit\n\n\n\n'
                    'REVIEW: 1234 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/'
                    'uservices/test-service',
                    'arc checkout users/robot-taxi-teamcity/'
                    'uservices/test-service',
                    'arc branch -D tmp',
                    'arc branch -f tmp users/gilfanovii/s-th',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/gilfanovii/s-th '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat s-th: s-th\n\n\n\n'
                    'REVIEW: 9012 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc rebase --abort',
                    'arc reset --hard --force',
                    'arc checkout users/robot-taxi-teamcity/'
                    'uservices/test-service',
                    'arc branch -D tmp',
                    'arc info --json',
                    'arc checkout -b tmp_trunk trunk -f',
                    'arc branch -f tmp users/gilfanovii/s-th',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/gilfanovii/s-th tmp_trunk',
                    'arc reset --soft cbabc1',
                    'arc commit --message Squash branch users/gilfanovii/s-th'
                    ' to merge base with branch tmp_trunk --force',
                    'arc info --json',
                    'arc rebase tmp_trunk tmp --force',
                    'arc rebase --abort',
                    'arc reset --hard --force',
                    'arc checkout tmp_trunk',
                    'arc branch -D tmp',
                    'arc info --json',
                    'arc branch -f tmp users/alberist/ololo',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/alberist/ololo '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat ololo: ololo\n\n\n\n'
                    'REVIEW: 5678 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc rebase --abort',
                    'arc reset --hard --force',
                    'arc checkout users/robot-taxi-teamcity/'
                    'uservices/test-service',
                    'arc branch -D tmp',
                    'arc info --json',
                    'arc checkout -b tmp_trunk trunk -f',
                    'arc branch -f tmp users/alberist/ololo',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/alberist/ololo tmp_trunk',
                    'arc reset --soft cbabc1',
                    'arc commit --message Squash branch users/alberist/ololo '
                    'to merge base with branch tmp_trunk --force',
                    'arc info --json',
                    'arc rebase tmp_trunk tmp --force',
                    'arc diff --name-status tmp_trunk tmp',
                    'arc branch -f tmp_trunk',
                    'arc checkout tmp_trunk',
                    'arc branch -D tmp',
                    'arc info --json',
                    'arc checkout -b conflicting_branch trunk -f',
                    'arc branch -f tmp users/alberist/ololo',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/alberist/ololo conflicting_branch',
                    'arc reset --soft cbabc1',
                    'arc commit --message Squash branch users/alberist/ololo'
                    ' to merge base with branch conflicting_branch --force',
                    'arc info --json',
                    'arc rebase conflicting_branch tmp --force',
                    'arc diff --name-status conflicting_branch tmp',
                    'arc branch -f conflicting_branch',
                    'arc checkout conflicting_branch',
                    'arc branch -D tmp',
                    'arc info --json',
                    'arc checkout -b tmp_conflicting_branch '
                    'conflicting_branch -f',
                    'arc branch -f tmp users/dteterin/edit-README-only',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/dteterin/edit-README-only '
                    'tmp_conflicting_branch',
                    'arc reset --soft cbabc1',
                    'arc commit --message Squash branch users/dteterin/edit'
                    '-README-only to merge base with branch '
                    'tmp_conflicting_branch --force',
                    'arc info --json',
                    'arc rebase tmp_conflicting_branch tmp --force',
                    'arc rebase --abort',
                    'arc reset --hard --force',
                    'arc checkout tmp_conflicting_branch',
                    'arc branch -D tmp',
                    'arc info --json',
                    'arc info --json',
                ],
                changed_files_by_commit={
                    '12345a': [
                        'taxi/services/test-service/service.yaml',
                        'taxi/services/test-service/src/main.cpp',
                    ],
                    '98989f': ['taxi/services/driver-authorizer/service.yaml'],
                    '90909g': ['taxi/services/driver-authorizer/service.yaml'],
                    '75757d': ['taxi/services.yaml'],
                    '45329c': ['taxi/services/test-service/debian/changelog'],
                    'aaaaa': ['taxi/services.yaml'],
                },
                log_json='log3.json',
                exp_changelog='base_changelog.txt',
                base_changelog='base_changelog.txt',
                arcadia_prs='arcadia_prs3.json',
                tc_set_parameters=[
                    {
                        'name': 'env.AFFECTED_USERS',
                        'value': 'alberist dteterin gilfanovii',
                    },
                    {
                        'name': 'env.CUSTOM_BUILD_REPORT',
                        'value': (
                            '[{"pull_request": {"number": 9012, '
                            '"url": "https://a.yandex-team.ru/review/9012", '
                            '"staff_user": "gilfanovii", "title": '
                            '"feat s-th: s-th", "labels": [], "from_branch": '
                            '"users/gilfanovii/s-th"}, "reason": '
                            '"conflict with develop", "category": 3, '
                            '"other_pr": null}, {"pull_request": {"number": '
                            '5678, "url": '
                            '"https://a.yandex-team.ru/review/5678", '
                            '"staff_user": "alberist", "title": '
                            '"feat ololo: ololo", "labels": [], '
                            '"from_branch": "users/alberist/ololo"}, '
                            '"reason": "conflict with PR", "category": 2, '
                            '"other_pr": {"number": 1234, "url": '
                            '"https://a.yandex-team.ru/review/1234", '
                            '"staff_user": "dteterin", "title": '
                            '"feat README: edit", "labels": [], '
                            '"from_branch": '
                            '"users/dteterin/edit-README-only"}}]'
                        ),
                    },
                    {
                        'name': 'env.BUILD_PROBLEM',
                        'value': (
                            'Failed to merge PR '
                            'https://a.yandex-team.ru/review/5678'
                        ),
                    },
                ],
                rebase_fails=[
                    ('rabase of users/dteterin/edit-README-only', False),
                    ('rabase of users/gilfanovii/s-th', True),
                    ('rabase gilfanovii on trunk', True),
                    ('rabase of users/alberist/ololo', True),
                    ('rabase alberist on trunk', False),
                    ('rabase dteterin branch on alberist branch', True),
                ],
                tc_report_problems=[
                    {
                        'description': (
                            'Failed to merge PR '
                            'https://a.yandex-team.ru/review/5678'
                        ),
                        'identity': None,
                    },
                ],
            ),
            id='conflicting_prs',
        ),
        pytest.param(
            Params(
                arc_calls=[
                    'arc info --json',
                    'arc info --json',
                    'arc info --json',
                    'arc checkout trunk',
                    'arc checkout -b '
                    'users/robot-taxi-teamcity/uservices/test-service '
                    'arcadia/trunk -f',
                    'arc info',
                    'arc info --json',
                    'arc fetch trunk',
                    'arc fetch users/dteterin/edit-README-only users/'
                    'alberist/ololo',
                    'arc branch -f tmp users/dteterin/edit-README-only',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/dteterin/edit-README-only '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat README: edit\n\n\n\n'
                    'REVIEW: 1234 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/'
                    'uservices/test-service',
                    'arc checkout users/robot-taxi-teamcity/'
                    'uservices/test-service',
                    'arc branch -D tmp',
                    'arc branch -f tmp users/alberist/ololo',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/alberist/ololo '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat ololo: ololo\n\n\n\n'
                    'REVIEW: 5678 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc branch -D tmp',
                    'arc merge-base arcadia/trunk arcadia/users/'
                    'dteterin/edit-README-only',
                    'arc rev-parse arcadia/users/dteterin/edit-README-only',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/'
                    'dteterin/edit-README-only '
                    '$workdir',
                    'arc merge-base arcadia/trunk arcadia/users/'
                    'alberist/ololo',
                    'arc rev-parse arcadia/users/alberist/ololo',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/'
                    'alberist/ololo '
                    '$workdir',
                    'arc info --json',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$workdir',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$schemas_dir',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 45329c^ 45329c $workdir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 98989f^ 98989f $schemas_dir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 12345a^ 12345a $schemas_dir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 98989f^ 98989f $schemas_dir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                    'arc diff 75757d^ 75757d $schemas_dir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                ],
                changed_files_by_commit={
                    '12345a': [
                        'taxi/services/test-service/service.yaml',
                        'taxi/services/test-service/src/main.cpp',
                    ],
                    '98989f': ['taxi/services/driver-authorizer/service.yaml'],
                    '75757d': ['taxi/services.yaml'],
                    '45329c': ['taxi/services/test-service/debian/changelog'],
                    'aaaaa': ['taxi/services.yaml'],
                },
                log_json='log2.json',
                exp_changelog='revision_exp_changelog.txt',
                base_changelog='revision_base_changelog.txt',
                arcadia_prs='arcadia_prs1.json',
                tc_set_parameters=[
                    {
                        'name': 'env.AFFECTED_USERS',
                        'value': 'alberist dteterin',
                    },
                    {
                        'name': 'env.CUSTOM_MERGED_PULL_REQUESTS_REPORT',
                        'value': (
                            '[{"number": 1234, "url": '
                            '"https://a.yandex-team.ru/review/1234", '
                            '"staff_user": "dteterin", "title": '
                            '"feat README: edit", "labels": ["custom/label"], '
                            '"from_branch": "users/dteterin/edit-README-only"'
                            '}, {"number": 5678, "url": '
                            '"https://a.yandex-team.ru/review/5678", '
                            '"staff_user": "alberist", "title": '
                            '"feat ololo: ololo", "labels": '
                            '["custom/label"], "from_branch": '
                            '"users/alberist/ololo"}]'
                        ),
                    },
                ],
                tc_report_build_number=[{'build_number': '7270531testing123'}],
            ),
            id='main_case_revision',
        ),
        pytest.param(
            Params(
                arc_calls=[
                    'arc info --json',
                    'arc info --json',
                    'arc info --json',
                    'arc checkout trunk',
                    'arc checkout -b '
                    'users/robot-taxi-teamcity/uservices/test-service '
                    'arcadia/trunk -f',
                    'arc info',
                    'arc info --json',
                    'arc fetch trunk',
                    'arc fetch users/dteterin/edit-README-only users/'
                    'alberist/ololo',
                    'arc branch -f tmp users/dteterin/edit-README-only',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/dteterin/edit-README-only '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat README: edit\n\n\n\n'
                    'REVIEW: 1234 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc branch -D tmp',
                    'arc branch -f tmp users/alberist/ololo',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/alberist/ololo '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat ololo: ololo\n\n\n\n'
                    'REVIEW: 5678 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc branch -D tmp',
                    'arc merge-base arcadia/trunk arcadia/users/'
                    'dteterin/edit-README-only',
                    'arc rev-parse arcadia/users/dteterin/edit-README-only',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/'
                    'dteterin/edit-README-only '
                    '$workdir',
                    'arc merge-base arcadia/trunk arcadia/users/'
                    'alberist/ololo',
                    'arc rev-parse arcadia/users/alberist/ololo',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/'
                    'alberist/ololo '
                    '$workdir',
                    'arc info --json',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$workdir',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$schemas_dir',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 12345a^ 12345a $schemas_dir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 98989f^ 98989f $schemas_dir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                ],
                changed_files_by_commit={
                    '12345a': [
                        'schemas/schemas/mongo/lavka_isr_invoices.yaml',
                        'schemas/schemas/services/nirvana/client.yaml',
                    ],
                    '98989f': [
                        'schemas/schemas/postgresql/surge/surge/'
                        'V01__create_db.sql',
                    ],
                },
                log_json='schemas_log.json',
                exp_changelog='exp_schemas_changelog.txt',
                base_changelog='base_changelog.txt',
                arcadia_prs='arcadia_prs1.json',
                tc_set_parameters=[
                    {
                        'name': 'env.AFFECTED_USERS',
                        'value': 'alberist dteterin',
                    },
                    {
                        'name': 'env.CUSTOM_MERGED_PULL_REQUESTS_REPORT',
                        'value': (
                            '[{"number": 1234, "url": '
                            '"https://a.yandex-team.ru/review/1234", '
                            '"staff_user": "dteterin", "title": '
                            '"feat README: edit", "labels": ["custom/label"], '
                            '"from_branch": "users/dteterin/edit-README-only"'
                            '}, {"number": 5678, "url": '
                            '"https://a.yandex-team.ru/review/5678", '
                            '"staff_user": "alberist", "title": '
                            '"feat ololo: ololo", "labels": ["custom/label"], '
                            '"from_branch": "users/alberist/ololo"}]'
                        ),
                    },
                ],
            ),
            id='schemas_commit',
        ),
        pytest.param(
            Params(
                arc_calls=[
                    'arc info --json',
                    'arc info --json',
                    'arc info --json',
                    'arc checkout trunk',
                    'arc checkout -b '
                    'users/robot-taxi-teamcity/uservices/test-service '
                    'arcadia/trunk -f',
                    'arc info',
                    'arc info --json',
                    'arc fetch trunk',
                    'arc fetch users/dteterin/edit-README-only users/'
                    'alberist/ololo',
                    'arc branch -f tmp users/dteterin/edit-README-only',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/dteterin/edit-README-only '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat README: edit\n\n\n\n'
                    'REVIEW: 1234 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc branch -D tmp',
                    'arc branch -f tmp users/alberist/ololo',
                    'arc info --json',
                    'arc checkout tmp',
                    'arc merge-base users/alberist/ololo '
                    'users/robot-taxi-teamcity/uservices/test-service',
                    'arc reset --soft cbabc1',
                    'arc commit --message feat ololo: ololo\n\n\n\n'
                    'REVIEW: 5678 --force',
                    'arc info --json',
                    'arc rebase users/robot-taxi-teamcity/uservices/'
                    'test-service tmp --force',
                    'arc diff --name-status users/robot-taxi-teamcity/'
                    'uservices/test-service tmp',
                    'arc branch -f users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc checkout users/robot-taxi-teamcity/uservices/'
                    'test-service',
                    'arc branch -D tmp',
                    'arc merge-base arcadia/trunk arcadia/users/'
                    'dteterin/edit-README-only',
                    'arc rev-parse arcadia/users/dteterin/edit-README-only',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/'
                    'dteterin/edit-README-only '
                    '$workdir',
                    'arc merge-base arcadia/trunk arcadia/users/'
                    'alberist/ololo',
                    'arc rev-parse arcadia/users/alberist/ololo',
                    'arc log -n1 --json cbabc1',
                    'arc log --json arcadia/trunk..arcadia/users/'
                    'alberist/ololo '
                    '$workdir',
                    'arc info --json',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$workdir',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$schemas_dir',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 45329c^ 45329c $workdir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 98989f^ 98989f $schemas_dir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 12345a^ 12345a $schemas_dir --name-only',
                    'arc diff 98989f^ 98989f $workdir --name-only',
                    'arc diff 98989f^ 98989f $schemas_dir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                    'arc diff 75757d^ 75757d $schemas_dir --name-only',
                    'arc diff 12345a^ 12345a $workdir --name-only',
                    'arc diff 75757d^ 75757d $workdir --name-only',
                ],
                versioning='none',
                changed_files_by_commit={
                    '12345a': [
                        'taxi/services/test-service/service.yaml',
                        'taxi/services/test-service/src/main.cpp',
                    ],
                    '98989f': ['taxi/services/driver-authorizer/service.yaml'],
                    '75757d': ['taxi/services.yaml'],
                    '45329c': ['taxi/services/test-service/debian/changelog'],
                    'aaaaa': ['taxi/services.yaml'],
                },
                log_json='log2.json',
                exp_changelog='base_changelog.txt',
                base_changelog='base_changelog.txt',
                arcadia_prs='arcadia_prs1.json',
                tc_set_parameters=[
                    {
                        'name': 'env.AFFECTED_USERS',
                        'value': 'alberist dteterin',
                    },
                    {
                        'name': 'env.CUSTOM_MERGED_PULL_REQUESTS_REPORT',
                        'value': (
                            '[{"number": 1234, "url": '
                            '"https://a.yandex-team.ru/review/1234", '
                            '"staff_user": "dteterin", "title": '
                            '"feat README: edit", "labels": ["custom/label"], '
                            '"from_branch": "users/dteterin/edit-README-only"'
                            '}, {"number": 5678, "url": '
                            '"https://a.yandex-team.ru/review/5678", '
                            '"staff_user": "alberist", "title": '
                            '"feat ololo: ololo", "labels": ["custom/label"], '
                            '"from_branch": "users/alberist/ololo"}]'
                        ),
                    },
                ],
                tc_report_build_number=[],
            ),
            id='no_changelog_update',
        ),
        pytest.param(
            Params(
                arc_calls=[
                    'arc info --json',
                    'arc info --json',
                    'arc info --json',
                    'arc checkout trunk',
                    'arc checkout -b '
                    'users/robot-taxi-teamcity/uservices/test-service '
                    'arcadia/trunk -f',
                    'arc info',
                    'arc info --json',
                    'arc fetch trunk',
                    'arc fetch users/dteterin/edit-README-only users/'
                    'alberist/ololo',
                    'arc info --json',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$workdir',
                    'arc merge-base arcadia/users/robot-taxi-teamcity/'
                    'uservices/test-service '
                    'arcadia/trunk',
                    'arc rev-parse arcadia/trunk',
                    'arc log -n1 --json cbabc1',
                    'arc log --json -n5 '
                    'arcadia/users/robot-taxi-teamcity/uservices/'
                    'test-service..arcadia/trunk '
                    '$schemas_dir',
                ],
                exp_arcadia_calls=[
                    {
                        'kwargs': {
                            'headers': {'Authorization': 'OAuth some-token'},
                            'params': {
                                'fields': (
                                    'review_requests(id,author,summary,'
                                    'vcs(from_branch,to_branch),'
                                    'checks(system,type,status,updated_at,'
                                    'alias),labels,description)'
                                ),
                                'limit': 10000,
                                'query': (
                                    'label(taxi/deploy:tanker);open();'
                                    'path(/taxi|/schemas/schemas)'
                                ),
                            },
                        },
                        'method': 'get',
                        'url': (
                            'http://a.yandex-team.ru/api/v1/review-requests'
                        ),
                    },
                ],
                log_json='log1.json',
                exp_changelog='exp_changelog1.txt',
                base_changelog='base_changelog.txt',
                arcadia_prs='arcadia_prs4.json',
                deploy_branch='tanker',
                tc_set_parameters=[
                    {
                        'name': 'env.AFFECTED_USERS',
                        'value': 'alberist dteterin',
                    },
                ],
                tc_report_build_number=[{'build_number': '0.0.0tanker123'}],
                test_contexts=[
                    (
                        'teamcity-taxi/YandexTaxiProjects'
                        '_TaxiBackendPy3_PullRequests_CheckSchemas'
                    ),
                    (
                        'teamcity-taxi/YandexTaxiProjects'
                        '_TaxiBackendPy3_PullRequests_pr'
                    ),
                ],
            ),
            id='text_contexts_checks',
        ),
    ],
)
def test_run_arcadia_custom(
        params: Params,
        commands_mock,
        tmpdir,
        monkeypatch,
        load,
        teamcity_report_build_number,
        teamcity_set_parameters,
        teamcity_report_problems,
        patch_requests,
        load_json,
):
    rebase_iter = -1

    @commands_mock('arc')
    def arc_mock(args, **kwargs):
        command = args[1]
        if command == 'info':
            return '{"branch": "users/robot-taxi-teamcity/uservices/%s"}' % (
                params.service_name,
            )
        if command == 'merge-base':
            return 'cbabc1'
        if command == 'rev-parse':
            return 'aaaaab'
        if command == 'log':
            if args[-2].endswith('trunk'):
                return load(params.log_json)
            return (
                '[{"author":"noname","commit":"aaaaa","message":'
                '"junk pr commit","parents":["23456b"],"date":'
                '"2021-03-18T20:23:22+03:00"}]'
            )
        if command == 'diff':
            if args[2] == '--name-status':
                return ''
            commit = args[3]
            return '\n'.join(params.changed_files_by_commit[commit])
        if (
                command == 'rebase'
                and params.rebase_fails
                and not args[2] in ('--abort', 'conflicting_branch')
        ):
            nonlocal rebase_iter
            rebase_iter += 1
            if params.rebase_fails[rebase_iter][-1]:
                return 1
        return 0

    @patch_requests(arcadia_client.API_URL + 'v1/review-requests')
    def arcadia_mock(method, url, **kwargs):
        return patch_requests.response(json=load_json(params.arcadia_prs))

    if params.is_several_projects:
        work_dir = arcadia.init_telematics(
            tmpdir, changelog_content=load(params.base_changelog),
        )
        arcadia.init_graph(
            tmpdir, changelog_content=load(params.base_changelog),
        )
        arcadia.init_uservices(
            tmpdir,
            main_service='my-new-service',
            changelog_content=load(params.base_changelog),
            versioning=params.versioning,
        )
        graph_dir = (work_dir / '..' / 'graph').resolve()
        service_dir = (
            work_dir / '..' / 'services' / 'driver-authorizer'
        ).resolve()
        substitute_dict = {
            'workdir': work_dir,
            'graphdir': graph_dir,
            'servicedir': service_dir,
        }
        changelog_path = work_dir / 'debian' / 'changelog'
        monkeypatch.setenv(
            'MASTER_BRANCH', 'users/robot-taxi-teamcity/uservices/telematics',
        )
    else:
        work_dir = arcadia.init_uservices(
            tmpdir,
            main_service=params.service_name,
            changelog_content=load(params.base_changelog),
            versioning=params.versioning,
        )
        schemas_dir = (work_dir / '..' / 'schemas' / 'schemas').resolve()
        changelog_path = (
            work_dir
            / 'services'
            / params.service_name
            / 'debian'
            / 'changelog'
        )
        substitute_dict = {'workdir': work_dir, 'schemas_dir': schemas_dir}

    monkeypatch.setenv('ARCADIA_TOKEN', 'some-token')
    if params.are_all_prs:
        monkeypatch.setenv('ADD_ALL_PULL_REQUESTS_TO_CUSTOM', '1')
        monkeypatch.setenv('CUSTOM_REPORTS_CHAT_ID', '')
    monkeypatch.chdir(work_dir)

    argv = [
        '--build-number',
        str(params.build_number),
        '--deploy-branch',
        params.deploy_branch,
    ]
    if params.pr_label:
        argv.extend(('--pr-label', params.pr_label))
    if params.test_contexts:
        argv.extend(('--test-contexts', *params.test_contexts))
    run_arcadia_custom.main(argv)

    expected_arc_calls = [
        arc.replace_paths(command, substitute_dict)
        for command in params.arc_calls
    ]
    arc_calls = [' '.join(call['args']) for call in arc_mock.calls]
    assert arc_calls == expected_arc_calls
    assert teamcity_report_build_number.calls == params.tc_report_build_number
    assert teamcity_set_parameters.calls == params.tc_set_parameters
    assert teamcity_report_problems.calls == params.tc_report_problems
    assert changelog_path.read_text() == load(params.exp_changelog)
    assert params.exp_arcadia_calls == arcadia_mock.calls
