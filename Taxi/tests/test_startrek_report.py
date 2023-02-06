import dataclasses
import json
import os
from typing import Optional
from typing import Sequence

import freezegun
import pytest

import startrek_report
from taxi_buildagent.clients import startrek as startrek_client
from taxi_buildagent.clients import teamcity as teamcity_client
from tests.utils import repository

TEAMCITY_URL = 'https://teamcity.taxi.yandex-team.ru/'
TEAMCITY_API_PREFIX = f'{TEAMCITY_URL}app/rest/'
TEAMCITY_TOKEN = 'secret_token'
TEAMCITY_AUTH = teamcity_client.HTTPBearerAuth(TEAMCITY_TOKEN)


@dataclasses.dataclass
class Params:
    user_id: str = ''
    password: str = ''
    teamcity_request: list = dataclasses.field(default_factory=list)
    teamcity_status_response: Optional[bytes] = None
    teamcity_tests_csv_requests: Sequence[dict] = ()
    teamcity_tests_csv_response: Optional[bytes] = None
    startrek_issue_request: Optional[dict] = None
    attachment_file_pool: Sequence[str] = ()
    startrek_attach_requests: Sequence[dict] = ()
    startrek_attach_responses: Sequence[dict] = ()
    env_status: Optional[str] = None
    argv: Optional[Sequence[str]] = None
    err_message: str = ''
    teamcity_build_response: Optional[dict] = None


# pylint: disable=too-many-lines
# pylint: disable=inconsistent-return-statements
@freezegun.freeze_time('2018-04-23 14:22:56', tz_offset=3)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                user_id='test-user',
                password='test-password',
                argv=[
                    '--name',
                    'TestName',
                    '--build',
                    '111222',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                    'debian/changelog',
                ],
                teamcity_status_response=b'SUCCESS',
                teamcity_request=[
                    {
                        'method': 'GET',
                        'url': f'{TEAMCITY_URL}app/rest/builds/111222/status',
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': None,
                        },
                    },
                ],
                startrek_issue_request={
                    'method': 'POST',
                    'url': (
                        startrek_client.get_issues_url()
                        + '/SUPERTAXIREL-123/comments'
                    ),
                    'kwargs': {
                        'data': (
                            b'{'
                            b'"text": '
                            b'"Teamcity build finished.\\n\\n'
                            b'Name: TestName\\n'
                            b'Source: new-project (1.0.22) unstable; '
                            b'urgency=low\\n'
                            b'Commit: 78efd47f3d7cf98eccdd45c'
                            b'91faa771558e0e63a\\n'
                            b'Build: 111222\\n'
                            b'Status: !!(green)SUCCESS!!\\n\\n'
                            b'((https://teamcity.taxi.yandex-team.ru/'
                            b'viewLog.html?buildId=111222 '
                            b'[teamcity build]))\\n"'
                            b'}'
                        ),
                        'json': None,
                        'headers': {
                            'Authorization': 'OAuth stoken',
                            'Content-Type': 'application/json',
                        },
                        'timeout': 5,
                        'verify': False,
                    },
                },
            ),
            id='release queue teamcity success',
        ),
        pytest.param(
            Params(
                user_id='test-user',
                password='test-password',
                argv=[
                    '--name',
                    'TestName',
                    '--build',
                    '111222',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                ],
                teamcity_status_response=b'SUCCESS',
                teamcity_request=[
                    {
                        'method': 'GET',
                        'url': f'{TEAMCITY_URL}app/rest/builds/111222/status',
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': None,
                        },
                    },
                ],
                startrek_issue_request={
                    'method': 'POST',
                    'url': (
                        startrek_client.get_issues_url()
                        + '/SUPERTAXIREL-123/comments'
                    ),
                    'kwargs': {
                        'data': (
                            b'{'
                            b'"text": '
                            b'"Teamcity build finished.\\n\\n'
                            b'Name: TestName\\n'
                            b'Source: new-project (1.0.22) unstable; '
                            b'urgency=low\\n'
                            b'Commit: 78efd47f3d7cf98eccdd45c'
                            b'91faa771558e0e63a\\n'
                            b'Build: 111222\\n'
                            b'Status: !!(green)SUCCESS!!\\n\\n'
                            b'((https://teamcity.taxi.yandex-team.ru/'
                            b'viewLog.html?buildId=111222 '
                            b'[teamcity build]))\\n"'
                            b'}'
                        ),
                        'json': None,
                        'headers': {
                            'Authorization': 'OAuth stoken',
                            'Content-Type': 'application/json',
                        },
                        'timeout': 5,
                        'verify': False,
                    },
                },
            ),
            id='release queue teamcity success without changelog',
        ),
        pytest.param(
            Params(
                user_id='new-test-user',
                password='new-test-password',
                argv=[
                    '--name',
                    'ImportantProject',
                    '--build',
                    '333555',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                    'debian/changelog',
                ],
                teamcity_status_response=b'FAILURE',
                teamcity_request=[
                    {
                        'method': 'GET',
                        'url': f'{TEAMCITY_URL}app/rest/builds/333555/status',
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': None,
                        },
                    },
                ],
                startrek_issue_request={
                    'method': 'POST',
                    'url': (
                        startrek_client.get_issues_url()
                        + '/SUPERTAXIREL-123/comments'
                    ),
                    'kwargs': {
                        'data': (
                            b'{'
                            b'"text": '
                            b'"Teamcity build finished.\\n\\n'
                            b'Name: ImportantProject\\n'
                            b'Source: new-project (1.0.22) unstable; '
                            b'urgency=low\\n'
                            b'Commit: 78efd47f3d7cf98eccdd45c91faa'
                            b'771558e0e63a\\n'
                            b'Build: 333555\\n'
                            b'Status: !!(red)FAILURE!!\\n\\n'
                            b'More information about fail on: '
                            b'((https://wiki.yandex-team.ru/taxi/backend/auto'
                            b'matization/faq/#rerun-failed-tests wiki))\\n\\n'
                            b'((https://teamcity.taxi.yandex-team.ru/'
                            b'viewLog.html?buildId=333555 '
                            b'[teamcity build]))\\n"'
                            b'}'
                        ),
                        'json': None,
                        'headers': {
                            'Authorization': 'OAuth stoken',
                            'Content-Type': 'application/json',
                        },
                        'timeout': 5,
                        'verify': False,
                    },
                },
            ),
            id='release queue teamcity failure',
        ),
        pytest.param(
            Params(
                user_id='test-user',
                password='test-password',
                attachment_file_pool=['some_full_file.txt'],
                env_status='SUCCESS',
                argv=[
                    '--name',
                    'TestName',
                    '--build',
                    '111222',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                    '--attachments_wildcard',
                    '*_file.txt',
                    '--attach_tests_info',
                    '--status-variable',
                    'BUILD_STATUS',
                    'debian/changelog',
                ],
                teamcity_tests_csv_requests=[
                    {
                        'method': 'GET',
                        'url': (
                            f'{TEAMCITY_URL}get/tests/'
                            'buildId/111222/tests.csv'
                        ),
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': None,
                        },
                    },
                ],
                teamcity_tests_csv_response=b'header1,header2\n1,2',
                teamcity_request=[
                    {
                        'method': 'GET',
                        'url': f'{TEAMCITY_URL}app/rest/builds/111222',
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': {
                                'Accept': 'application/json',
                                'Origin': (
                                    'https://teamcity.taxi.' 'yandex-team.ru/'
                                ),
                            },
                        },
                    },
                ],
                startrek_issue_request={
                    'method': 'POST',
                    'url': (
                        startrek_client.get_issues_url()
                        + '/SUPERTAXIREL-123/comments'
                    ),
                    'kwargs': {
                        'data': json.dumps(
                            {
                                'text': (
                                    'Teamcity build finished.\n\n'
                                    'Name: TestName\n'
                                    'Source: new-project (1.0.22) unstable; '
                                    'urgency=low\n'
                                    'Commit: 78efd47f3d7cf98eccdd45c91'
                                    'faa771558e0e63a\n'
                                    'Build: 111222\n'
                                    'Status: !!(green)SUCCESS!!\n\n'
                                    '((https://teamcity.taxi.yandex-team.ru/'
                                    'viewLog.html?buildId=111222 '
                                    '[teamcity build]))\n'
                                ),
                                'attachmentIds': [1234, 1235],
                            },
                        ).encode('utf-8'),
                        'json': None,
                        'headers': {
                            'Authorization': 'OAuth stoken',
                            'Content-Type': 'application/json',
                        },
                        'timeout': 5,
                        'verify': False,
                    },
                },
                startrek_attach_requests=[
                    {
                        'method': 'POST',
                        'url': startrek_client.API_URL + 'attachments',
                        'kwargs': {
                            'data': None,
                            'json': None,
                            'headers': {'Authorization': 'OAuth stoken'},
                            'files': {'file': 'some_full_file.txt'},
                            'params': {'filename': 'some_full_file.txt'},
                            'timeout': 30,
                            'verify': False,
                        },
                    },
                    {
                        'method': 'POST',
                        'url': startrek_client.API_URL + 'attachments',
                        'kwargs': {
                            'data': None,
                            'json': None,
                            'headers': {'Authorization': 'OAuth stoken'},
                            'files': {'file': 'test_info.csv'},
                            'params': {'filename': 'test_info.csv'},
                            'timeout': 30,
                            'verify': False,
                        },
                    },
                ],
                # 1 from disk + 1 from teamcity tests
                startrek_attach_responses=[{'id': '1234'}, {'id': '1235'}],
            ),
            id='startrack report with attachments and test report environ',
        ),
        pytest.param(
            Params(
                user_id='new-test-user',
                password='new-test-password',
                env_status='FAILURE',
                argv=[
                    '--name',
                    'ImportantProject',
                    '--build',
                    '333555',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                    '--status-variable',
                    'BUILD_STATUS',
                    'debian/changelog',
                ],
                startrek_issue_request={
                    'method': 'POST',
                    'url': (
                        startrek_client.get_issues_url()
                        + '/SUPERTAXIREL-123/comments'
                    ),
                    'kwargs': {
                        'data': json.dumps(
                            {
                                'text': (
                                    'Teamcity build finished.\n\n'
                                    'Name: ImportantProject\n'
                                    'Source: new-project (1.0.22) unstable; '
                                    'urgency=low\n'
                                    'Commit: 78efd47f3d7cf98eccdd45c91'
                                    'faa771558e0e63a\n'
                                    'Build: 333555\n'
                                    'Status: !!(red)FAILURE!!\n\n'
                                    'More information about fail on: '
                                    '((https://wiki.yandex-team.ru/taxi'
                                    '/backend/automatization/faq/'
                                    '#rerun-failed-tests wiki))\n\n'
                                    '((https://teamcity.taxi.yandex-team.ru/'
                                    'viewLog.html?buildId=333555 '
                                    '[teamcity build]))\n'
                                ),
                            },
                        ).encode('utf-8'),
                        'json': None,
                        'headers': {
                            'Authorization': 'OAuth stoken',
                            'Content-Type': 'application/json',
                        },
                        'timeout': 5,
                        'verify': False,
                    },
                },
            ),
            id='release queue teamcity failure environ',
        ),
        pytest.param(
            Params(
                user_id='test-user',
                password='test-password',
                attachment_file_pool=[
                    'empty_file.txt',
                    'some_full_file.txt',
                    'some_full_other_file.txt',
                    'random.txt',
                ],
                argv=[
                    '--name',
                    'TestName',
                    '--build',
                    '111222',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                    '--attachments_wildcard',
                    '*_file.txt',
                    'debian/changelog',
                ],
                teamcity_status_response=b'SUCCESS',
                teamcity_request=[
                    {
                        'method': 'GET',
                        'url': f'{TEAMCITY_URL}app/rest/builds/111222/status',
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': None,
                        },
                    },
                ],
                startrek_issue_request={
                    'method': 'POST',
                    'url': (
                        startrek_client.get_issues_url()
                        + '/SUPERTAXIREL-123/comments'
                    ),
                    'kwargs': {
                        'data': json.dumps(
                            {
                                'text': (
                                    'Teamcity build finished.\n\n'
                                    'Name: TestName\n'
                                    'Source: new-project (1.0.22) unstable; '
                                    'urgency=low\n'
                                    'Commit: 78efd47f3d7cf98eccdd45c9'
                                    '1faa771558e0e63a\n'
                                    'Build: 111222\n'
                                    'Status: !!(green)SUCCESS!!\n\n'
                                    '((https://teamcity.taxi.yandex-team.ru/'
                                    'viewLog.html?buildId=111222 '
                                    '[teamcity build]))\n'
                                ),
                                'attachmentIds': [1234, 1235],
                            },
                        ).encode('utf-8'),
                        'json': None,
                        'headers': {
                            'Authorization': 'OAuth stoken',
                            'Content-Type': 'application/json',
                        },
                        'timeout': 5,
                        'verify': False,
                    },
                },
                startrek_attach_requests=[
                    {
                        'method': 'POST',
                        'url': startrek_client.API_URL + 'attachments',
                        'kwargs': {
                            'data': None,
                            'json': None,
                            'headers': {'Authorization': 'OAuth stoken'},
                            'files': {'file': 'some_full_other_file.txt'},
                            'params': {'filename': 'some_full_other_file.txt'},
                            'timeout': 30,
                            'verify': False,
                        },
                    },
                    {
                        'method': 'POST',
                        'url': startrek_client.API_URL + 'attachments',
                        'kwargs': {
                            'data': None,
                            'json': None,
                            'headers': {'Authorization': 'OAuth stoken'},
                            'files': {'file': 'some_full_file.txt'},
                            'params': {'filename': 'some_full_file.txt'},
                            'timeout': 30,
                            'verify': False,
                        },
                    },
                ],
                startrek_attach_responses=[{'id': '1234'}, {'id': '1235'}],
            ),
            id='startrack report with attachments',
        ),
        pytest.param(
            Params(
                user_id='test-user',
                password='test-password',
                attachment_file_pool=['bad_full_file.txt'],
                argv=[
                    '--name',
                    'TestName',
                    '--build',
                    '111222',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                    '--attachments_wildcard',
                    '*_file.txt',
                    'debian/changelog',
                ],
                teamcity_status_response=b'SUCCESS',
                teamcity_request=[
                    {
                        'method': 'GET',
                        'url': f'{TEAMCITY_URL}app/rest/builds/111222/status',
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': None,
                        },
                    },
                ],
                startrek_attach_requests=[
                    {
                        'method': 'POST',
                        'url': startrek_client.API_URL + 'attachments',
                        'kwargs': {
                            'data': None,
                            'json': None,
                            'headers': {'Authorization': 'OAuth stoken'},
                            'files': {'file': 'bad_full_file.txt'},
                            'params': {'filename': 'bad_full_file.txt'},
                            'timeout': 30,
                            'verify': False,
                        },
                    },
                ],
                startrek_attach_responses=[{}],
            ),
            id='startrack report with attachments fails to upload attachment',
        ),
        pytest.param(
            Params(
                user_id='test-user',
                password='test-password',
                attachment_file_pool=['some_full_file.txt'],
                argv=[
                    '--name',
                    'TestName',
                    '--build',
                    '111222',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                    '--attachments_wildcard',
                    '*_file.txt',
                    '--attach_tests_info',
                    'debian/changelog',
                ],
                teamcity_status_response=b'SUCCESS',
                teamcity_request=[
                    {
                        'method': 'GET',
                        'url': f'{TEAMCITY_URL}app/rest/builds/111222/status',
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': None,
                        },
                    },
                    {
                        'method': 'GET',
                        'url': f'{TEAMCITY_URL}app/rest/builds/111222',
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': {
                                'Accept': 'application/json',
                                'Origin': (
                                    'https://teamcity.taxi.' 'yandex-team.ru/'
                                ),
                            },
                        },
                    },
                ],
                teamcity_tests_csv_requests=[
                    {
                        'method': 'GET',
                        'url': (
                            f'{TEAMCITY_URL}get/tests/'
                            'buildId/111222/tests.csv'
                        ),
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': None,
                        },
                    },
                ],
                teamcity_tests_csv_response=b'header1,header2\n1,2',
                startrek_issue_request={
                    'method': 'POST',
                    'url': (
                        startrek_client.get_issues_url()
                        + '/SUPERTAXIREL-123/comments'
                    ),
                    'kwargs': {
                        'data': json.dumps(
                            {
                                'text': (
                                    'Teamcity build finished.\n\n'
                                    'Name: TestName\n'
                                    'Source: new-project (1.0.22) unstable; '
                                    'urgency=low\n'
                                    'Commit: 78efd47f3d7cf98eccdd45c91'
                                    'faa771558e0e63a\n'
                                    'Build: 111222\n'
                                    'Status: !!(green)SUCCESS!!\n\n'
                                    '((https://teamcity.taxi.yandex-team.ru/'
                                    'viewLog.html?buildId=111222 '
                                    '[teamcity build]))\n'
                                ),
                                'attachmentIds': [1234, 1235],
                            },
                        ).encode('utf-8'),
                        'json': None,
                        'headers': {
                            'Authorization': 'OAuth stoken',
                            'Content-Type': 'application/json',
                        },
                        'timeout': 5,
                        'verify': False,
                    },
                },
                startrek_attach_requests=[
                    {
                        'method': 'POST',
                        'url': startrek_client.API_URL + 'attachments',
                        'kwargs': {
                            'data': None,
                            'json': None,
                            'headers': {'Authorization': 'OAuth stoken'},
                            'files': {'file': 'some_full_file.txt'},
                            'params': {'filename': 'some_full_file.txt'},
                            'timeout': 30,
                            'verify': False,
                        },
                    },
                    {
                        'method': 'POST',
                        'url': startrek_client.API_URL + 'attachments',
                        'kwargs': {
                            'data': None,
                            'json': None,
                            'headers': {'Authorization': 'OAuth stoken'},
                            'files': {'file': 'test_info.csv'},
                            'params': {'filename': 'test_info.csv'},
                            'timeout': 30,
                            'verify': False,
                        },
                    },
                ],
                # 1 from disk + 1 from teamcity tests
                startrek_attach_responses=[{'id': '1234'}, {'id': '1235'}],
            ),
            id='startrack report with attachments and test report',
        ),
        pytest.param(
            Params(
                user_id='test-user',
                password='test-password',
                argv=[
                    '--name',
                    'TestName',
                    '--build',
                    '111222',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                    '--source',
                    'new-project (1.1.1) unstable; urgency=low',
                    '--release_ticket_url',
                    'https://st.yandex-team.ru/SUPERTAXIREL-321',
                ],
                teamcity_status_response=b'SUCCESS',
                teamcity_request=[
                    {
                        'method': 'GET',
                        'url': f'{TEAMCITY_URL}app/rest/builds/111222/status',
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': None,
                        },
                    },
                ],
                startrek_issue_request={
                    'method': 'POST',
                    'url': (
                        startrek_client.get_issues_url()
                        + '/SUPERTAXIREL-321/comments'
                    ),
                    'kwargs': {
                        'data': (
                            b'{'
                            b'"text": '
                            b'"Teamcity build finished.\\n\\n'
                            b'Name: TestName\\n'
                            b'Source: new-project (1.1.1) unstable; '
                            b'urgency=low\\n'
                            b'Commit: 78efd47f3d7cf98eccdd45c'
                            b'91faa771558e0e63a\\n'
                            b'Build: 111222\\n'
                            b'Status: !!(green)SUCCESS!!\\n\\n'
                            b'((https://teamcity.taxi.yandex-team.ru/'
                            b'viewLog.html?buildId=111222 '
                            b'[teamcity build]))\\n"'
                            b'}'
                        ),
                        'json': None,
                        'headers': {
                            'Authorization': 'OAuth stoken',
                            'Content-Type': 'application/json',
                        },
                        'timeout': 5,
                        'verify': False,
                    },
                },
            ),
            id='run without changelog, with args',
        ),
        pytest.param(
            Params(
                argv=[
                    '--name',
                    'TestName',
                    '--build',
                    '111222',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                    '--source',
                    'new-project (1.1.1) unstable; urgency=low',
                    '--release_ticket_url',
                    startrek_client.USER_URL + 'SUPERTAXIREL-321',
                    'debian/changelog',
                ],
                err_message=(
                    'Pass `--release_ticket_url` AND `--source` args XOR pass '
                    'path to changelog\n'
                ),
            ),
            id='run with changelog and args',
        ),
        pytest.param(
            Params(
                argv=[
                    '--name',
                    'TestName',
                    '--build',
                    '111222',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                    '--source',
                    'new-project (1.1.1) unstable; urgency=low',
                ],
                err_message=(
                    'Pass `--release_ticket_url` AND `--source` args XOR pass '
                    'path to changelog\n'
                ),
            ),
            id='run without changelog and source args',
        ),
        pytest.param(
            Params(
                argv=[
                    '--name',
                    'TestName',
                    '--build',
                    '111222',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                    '--source',
                    'new-project (1.1.1) unstable; urgency=low',
                    '--release_ticket_url',
                    'https://wrong-url.com',
                ],
                err_message=(
                    '`--release_ticket_url` is not valid: '
                    'https://wrong-url.com\n'
                ),
            ),
            id='wrong release_ticket_url',
        ),
        pytest.param(
            Params(
                user_id='test-user',
                password='test-password',
                attachment_file_pool=['some_full_file.txt'],
                env_status='SUCCESS',
                argv=[
                    '--name',
                    'TestName',
                    '--build',
                    '111222',
                    '--commit',
                    '78efd47f3d7cf98eccdd45c91faa771558e0e63a',
                    '--attach_tests_info',
                    '--status-variable',
                    'BUILD_STATUS',
                    'debian/changelog',
                ],
                teamcity_tests_csv_requests=[
                    {
                        'method': 'GET',
                        'url': (
                            f'{TEAMCITY_URL}get/tests/'
                            'buildId/111222/tests.csv'
                        ),
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': None,
                        },
                    },
                    {
                        'method': 'GET',
                        'url': (
                            f'{TEAMCITY_URL}get/tests/buildId/789/tests.csv'
                        ),
                        'kwargs': {
                            'auth': TEAMCITY_AUTH,
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                            'allow_redirects': True,
                            'headers': None,
                        },
                    },
                ],
                teamcity_tests_csv_response=b'header1,header2\n1,2',
                teamcity_build_response={
                    'snapshot-dependencies': {'build': [{'id': 789}]},
                    'buildType': {'name': 'some (py3)'},
                },
                teamcity_request=[
                    {
                        'kwargs': {
                            'allow_redirects': True,
                            'auth': TEAMCITY_AUTH,
                            'headers': {
                                'Accept': 'application/json',
                                'Origin': (
                                    'https://teamcity.taxi.yandex-team.ru/'
                                ),
                            },
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                        },
                        'method': 'GET',
                        'url': f'{TEAMCITY_URL}app/rest/builds/111222',
                    },
                    {
                        'kwargs': {
                            'allow_redirects': True,
                            'auth': TEAMCITY_AUTH,
                            'headers': {
                                'Accept': 'application/json',
                                'Origin': (
                                    'https://teamcity.taxi.yandex-team.ru/'
                                ),
                            },
                            'timeout': teamcity_client.TIMEOUT,
                            'verify': False,
                        },
                        'method': 'GET',
                        'url': f'{TEAMCITY_URL}app/rest/builds/789',
                    },
                ],
                startrek_issue_request={
                    'method': 'POST',
                    'url': (
                        startrek_client.get_issues_url()
                        + '/SUPERTAXIREL-123/comments'
                    ),
                    'kwargs': {
                        'data': json.dumps(
                            {
                                'text': (
                                    'Teamcity build finished.\n\n'
                                    'Name: TestName\n'
                                    'Source: new-project (1.0.22) unstable; '
                                    'urgency=low\n'
                                    'Commit: 78efd47f3d7cf98eccdd45c91'
                                    'faa771558e0e63a\n'
                                    'Build: 111222\n'
                                    'Status: !!(green)SUCCESS!!\n\n'
                                    '((https://teamcity.taxi.yandex-team.ru/'
                                    'viewLog.html?buildId=111222 '
                                    '[teamcity build]))\n'
                                ),
                                'attachmentIds': [1234, 1235],
                            },
                        ).encode('utf-8'),
                        'json': None,
                        'headers': {
                            'Authorization': 'OAuth stoken',
                            'Content-Type': 'application/json',
                        },
                        'timeout': 5,
                        'verify': False,
                    },
                },
                startrek_attach_requests=[
                    {
                        'method': 'POST',
                        'url': startrek_client.API_URL + 'attachments',
                        'kwargs': {
                            'data': None,
                            'json': None,
                            'headers': {'Authorization': 'OAuth stoken'},
                            'files': {'file': 'test_info.csv'},
                            'params': {'filename': 'test_info.csv'},
                            'timeout': 30,
                            'verify': False,
                        },
                    },
                    {
                        'method': 'POST',
                        'url': startrek_client.API_URL + 'attachments',
                        'kwargs': {
                            'data': None,
                            'json': None,
                            'headers': {'Authorization': 'OAuth stoken'},
                            'files': {'file': 'test_info_some__py3_.csv'},
                            'params': {'filename': 'test_info_some__py3_.csv'},
                            'timeout': 30,
                            'verify': False,
                        },
                    },
                ],
                startrek_attach_responses=[{'id': '1234'}, {'id': '1235'}],
            ),
            id='startrack snapshot attachments',
        ),
    ],
)
def test_startrek_report(
        tmpdir, chdir, monkeypatch, patch_requests, capsys, params: Params,
):
    @patch_requests(TEAMCITY_API_PREFIX)
    def teamcity_request(method, url, **kwargs):
        command = url.split(TEAMCITY_API_PREFIX)[-1]
        command = command.split('?')[0]

        if command.endswith('status'):
            return patch_requests.response(
                content=params.teamcity_status_response,
            )
        if command.startswith('builds'):
            build_resp = params.teamcity_build_response
            if build_resp is None:
                build_resp = {}
            return patch_requests.response(json=build_resp)

        assert False, 'Unpatched teamcity request: %s' % url

    @patch_requests(f'{TEAMCITY_URL}get/tests')
    def teamcity_tests(method, url, **kwargs):
        assert method.upper() == 'GET'
        return patch_requests.response(
            content=params.teamcity_tests_csv_response,
        )

    attach_responses = iter(params.startrek_attach_responses)

    @patch_requests(startrek_client.API_URL + 'attachments')
    def _startrek_attachs(method, url, **kwargs):
        assert method.upper() == 'POST'
        # dont want to diff actual file objects
        filename = kwargs['params']['filename']
        kwargs['files']['file'] = filename

        status_code = 204 if filename.startswith('bad') else 201
        return patch_requests.response(
            status_code=status_code, json=next(attach_responses),
        )

    @patch_requests(startrek_client.API_URL + 'issues')
    def _startrek_issues(method, url, **kwargs):
        assert method.upper() == 'POST'
        return patch_requests.response(json=params.startrek_issue_request)

    def _attach_key(attach):
        # key for sorting attach_responses
        return attach['kwargs']['files']['file']

    monkeypatch.setenv('STARTREK_TOKEN', 'stoken')
    monkeypatch.setenv('TEAMCITY_TOKEN', TEAMCITY_TOKEN)

    repo = repository.init_repo(
        str(tmpdir.mkdir('repo')), 'oyaso', 'oyaso@yandex-team.ru',
    )
    repository.commit_debian_dir(
        repo,
        'new-project',
        version='1.0.22',
        release_ticket='SUPERTAXIREL-123',
    )

    chdir(repo.working_tree_dir)

    # make files for attachments
    for filename in params.attachment_file_pool:
        filepath = os.path.join(repo.working_tree_dir, filename)
        with open(filepath, 'w') as file:
            if not filename.startswith('empty'):
                file.write(filename)
    if params.env_status:
        monkeypatch.setenv('BUILD_STATUS', params.env_status)
    if params.err_message:
        with pytest.raises(SystemExit) as excinfo:
            startrek_report.main(params.argv)
        err = capsys.readouterr().err
        assert params.err_message == err
        assert (1,) == excinfo.value.args
        assert [] == teamcity_tests.calls
        assert [] == _startrek_issues.calls
        assert [] == _startrek_attachs.calls
    elif any(file.startswith('bad') for file in params.attachment_file_pool):
        with pytest.raises(SystemExit) as excinfo:
            startrek_report.main(params.argv)
        assert (1,) == excinfo.value.args
        assert list(params.teamcity_tests_csv_requests) == teamcity_tests.calls
        assert sorted(
            params.startrek_attach_requests, key=_attach_key,
        ) == sorted(_startrek_attachs.calls, key=_attach_key)
        assert [] == _startrek_issues.calls
    else:
        startrek_report.main(params.argv)
        err = capsys.readouterr().err
        assert err == ''
        assert list(params.teamcity_tests_csv_requests) == teamcity_tests.calls

        assert sorted(
            params.startrek_attach_requests, key=_attach_key,
        ) == sorted(_startrek_attachs.calls, key=_attach_key)
        assert [params.startrek_issue_request] == _startrek_issues.calls

    assert params.teamcity_request == teamcity_request.calls
