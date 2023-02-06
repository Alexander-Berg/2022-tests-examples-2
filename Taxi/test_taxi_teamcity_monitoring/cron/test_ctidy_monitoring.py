# pylint: disable=too-many-lines
import pathlib
import typing

from aiohttp import web
import pytest

import arc_api.components as arc_api
from taxi.clients import startrack as clients_startrek
from taxi.util import dates
from yandex.arc.api.public import repo_pb2

from taxi_teamcity_monitoring.crontasks import utils
from taxi_teamcity_monitoring.crontasks.ctidy_monitoring import (
    run_ctidy_monitoring,
)
from taxi_teamcity_monitoring.generated.cron import run_cron


class ExtractPathTestParams(typing.NamedTuple):
    filename: str
    expected_yaml: typing.Optional[dict]


class StartrekLinkParams(typing.NamedTuple):
    filename: str
    expected_startrek_link: str


DEFAULT_CTIDY_NAMES_ENTRIES = [
    {
        '_id': (
            'libraries/experiments3/src/experiments3/'
            'utils/experiments3/files.cpp'
        ),
        'ticket_id': 'TAXICTIDY-7493',
    },
    {
        '_id': 'services/api-proxy/src/components/configuration.cpp',
        'ticket_id': 'TAXICTIDY-8591',
    },
    {
        '_id': 'services/umlaas/src/custom/dependencies.cpp',
        'ticket_id': 'TAXICTIDY-9813',
    },
]
EXAMPLE_YAML_CONTENT = 'maintainers:\n  - %s <%s@yandex-team.ru>\n'


@pytest.fixture
def arcanum_file_services(mock, patch_file_service, arc_mockserver):
    @mock
    def _read_file(request, context):
        path = request.Path
        data = ''
        if path.startswith('taxi/uservices/services/api-proxy'):
            data = EXAMPLE_YAML_CONTENT % ('vasya', 'vasya')
        if path.startswith('taxi/uservices/services/cardstorage'):
            data = EXAMPLE_YAML_CONTENT % ('vasya', 'vasya')
        if path.startswith('taxi/uservices/libraries/experiments3'):
            data = EXAMPLE_YAML_CONTENT % ('pupkin', 'pupkin')
        if data == '':
            raise arc_api.ArcClientBaseError()

        yield repo_pb2.ReadFileResponse(
            Header=repo_pb2.ReadFileResponse.ReadFileHeader(
                Oid='853cb0f6a5888d6ecfe2c7acc6a90d42af85b89c',
                FileSize=len(data),
            ),
        )
        yield repo_pb2.ReadFileResponse(Data=bytes(data, 'utf-8'))

    file_service_mock = patch_file_service(read_file=_read_file)
    arc_mockserver(file_service_mock)


def _message_to_dict(message):
    return {
        'From': message['From'],
        'To': message['To'],
        'Subject': message['Subject'],
        'Content-Type': message['Content-Type'],
        'Body': message.get_payload(decode=True).decode('utf-8'),
    }


# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
@pytest.mark.now('2019-03-03T03:00:00+0000')
@pytest.mark.config(
    TEAMCITY_MONITORING_CTIDY_CREATE_TICKETS_ENABLED=True,
    TEAMCITY_MONITORING_CTIDY_EMAIL_ENABLED=True,
    TEAMCITY_MONITORING_CTIDY_EMAIL_BODY_TPL='{repository}\n{stacktraces}',
    TEAMCITY_MONITORING_CTIDY_DEFAULT_RECIPIENT='mister_x',
    TEAMCITY_MONITORING_CTIDY_TICKET_TITLE_TPL='{filename}',
    TEAMCITY_MONITORING_CTIDY_TICKET_BODY_TPL='{filename}\n'
    '{repository}\n{stacktrace}',
)
@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.usefixtures('arcanum_file_services')
async def test_ctidy_monitoring(
        load,
        load_json,
        patch_aiohttp_session,
        response_mock,
        patch,
        monkeypatch,
        tmpdir,
        mock,
        commands_mock,
        db,
        mock_teamcity,
        failed=False,
        threshold=False,
):
    @mock_teamcity('/app/rest/builds', prefix=True)
    def teamcity_get_build_request(request):
        return web.json_response(
            load_json('teamcity_test_builds_response.json'),
        )

    @mock_teamcity('/app/rest/testOccurrences', prefix=True)
    def teamcity_get_tests_request(request):
        return web.json_response(
            load_json('teamcity_test_occurrences_response.json'),
        )

    @patch_aiohttp_session('https://test-startrack-url/')
    def st_request(method, url, json, **kwargs):
        responses = {
            'TAXICTIDY-7493': {
                'key': 'TAXICTIDY-7493',
                'status': {'key': 'closed'},
                'resolution': {'key': 'fixed'},
                'assignee': {'id': 'user442'},
                'resolvedAt': '2010-01-01T00:00:00.0+0000',
            },
            'TAXICTIDY-8591': {
                'key': 'TAXICTIDY-8591',
                'status': {'key': 'open'},
                'assignee': {'id': 'user315'},
            },
            'TAXICTIDY-9813': {
                'key': 'TAXICTIDY-9813',
                'status': {'key': 'closed'},
                'resolution': {'key': 'fixed'},
                'assignee': {'id': 'user831'},
                'resolvedAt': '2025-03-03T00:00:00.0+0000',
            },
            'TAXICTIDY-7493-NEW': {
                'key': 'TAXICTIDY-7493-NEW',
                'status': {'key': 'open'},
            },
            'TAXICTIDY-ABS-NEW-7': {
                'key': 'TAXICTIDY-ABS-NEW-7',
                'status': {'key': 'open'},
            },
            'TAXICTIDY-ABS-X': {
                'key': 'TAXICTIDY-ABS-X',
                'status': {'key': 'open'},
            },
        }

        if method == 'post':
            filename = json['summary'].split('/')[-1]
            ticket_id = None
            if filename == 'files.cpp':
                ticket_id = 'TAXICTIDY-7493-NEW'
            elif filename == 'stat_counter.cpp':
                ticket_id = 'TAXICTIDY-ABS-NEW-7'
            elif filename == 'utils.cpp':
                ticket_id = 'TAXICTIDY-ABS-X'
            elif filename == 'configuration.cpp':
                ticket_id = 'SHOULD_NOT_BE'
            return response_mock(json=responses[ticket_id])
        ticket_id = url.split('/')[4]
        if ticket_id == 'FAILED':
            return response_mock(
                json={
                    'errors': {
                        'assignee': 'пользователь oyaso не существует.',
                    },
                    'errorMessages': [],
                    'statusCode': 422,
                },
            )
        return response_mock(json=responses[ticket_id])

    class MySMTP:
        # pylint: disable=no-self-argument

        @mock
        def __init__(host, port):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        @mock
        def send_message(message):
            pass

    monkeypatch.setattr('smtplib.SMTP', MySMTP)
    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.settings.EMAIL_SEND_TO_AUTHOR',
        True,
    )
    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.settings.TICKET_URL_TPL',
        'https://test-startrack-url/{ticket_id}',
    )

    commands = [
        'taxi_teamcity_monitoring.crontasks.'
        'ctidy_monitoring.run_ctidy_monitoring',
        '-t',
        '0',
    ]

    if failed or threshold:
        with pytest.raises(run_ctidy_monitoring.CtidyMonitoringError):
            await run_cron.main(commands)
    else:
        await run_cron.main(commands)

    assert teamcity_get_tests_request.times_called == 1
    tc_get_failed_tests_args = (await teamcity_get_tests_request.wait_call())[
        'request'
    ]
    assert tc_get_failed_tests_args.url.endswith(
        '/app/rest/testOccurrences?locator=status:FAILURE,'
        'build:(id:19970909,branch:(default:true),count:1),count:-1&'
        'fields=testOccurrence(name,details,build(startDate))',
    )

    assert teamcity_get_build_request.times_called == 1
    tc_get_successful_build_args = (
        await teamcity_get_build_request.wait_call()
    )['request']
    assert tc_get_successful_build_args.url.endswith(
        '/app/rest/builds?locator=status:SUCCESS,buildType:YandexTaxiProjects_'
        'UservicesArcadia_Internal_ClangTidyCheck,count:1,'
        'branch:(default:true)&fields=build(id)',
    )

    if threshold:
        return

    calls = st_request.calls
    assert len(calls) == 6 + int(failed)
    for call in calls:
        call.pop('kwargs')
        if call['json'] is not None:
            if 'unique' in call['json']:
                call['json'].pop('unique')

    expected_calls = [
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXICTIDY-8591',
            'json': None,
        },
        {
            'method': 'patch',
            'url': 'https://test-startrack-url/issues/TAXICTIDY-8591',
            'json': {
                'description': (
                    '((https://a.yandex-team.ru/arc_vcs/'
                    'taxi/uservices/services/api-proxy/src/'
                    'components/configuration.cpp services/'
                    'api-proxy/src/components/'
                    'configuration.cpp))\ntaxi/'
                    'uservices\nerror'
                ),
            },
        },
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXICTIDY-7493',
            'json': None,
        },
        {
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
            'json': {
                'summary': (
                    'libraries/experiments3/src/experiments3/'
                    'utils/experiments3/files.cpp'
                ),
                'queue': {'key': 'TAXICTIDY'},
                'description': (
                    '((https://a.yandex-team.ru/arc_vcs/'
                    'taxi/uservices/libraries/experiments3/'
                    'src/experiments3/utils/experiments3/files.cpp'
                    ' libraries/experiments3/src/experiments3/utils/'
                    'experiments3/files.cpp))\ntaxi/'
                    'uservices\nerror'
                ),
                'type': {'key': 'task'},
                'assignee': 'pupkin',
                'links': [
                    {'relationship': 'relates', 'issue': 'TAXICTIDY-7493'},
                ],
            },
        },
        {
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
            'json': {
                'summary': (
                    'services/cardstorage/src/statistics/stat_counter.cpp'
                ),
                'queue': {'key': 'TAXICTIDY'},
                'description': (
                    '((https://a.yandex-team.ru/arc_vcs/taxi/'
                    'uservices/services/cardstorage/src/statistics/'
                    'stat_counter.cpp services/cardstorage/src/'
                    'statistics/stat_counter.cpp))\ntaxi/uservices\nerror'
                ),
                'type': {'key': 'task'},
                'assignee': 'vasya',
            },
        },
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXICTIDY-9813',
            'json': None,
        },
    ]

    if failed:
        expected_calls.extend(
            [
                {
                    'method': 'get',
                    'url': 'https://test-startrack-url/issues/FAILED',
                    'json': None,
                },
            ],
        )

    assert calls == expected_calls

    calls = MySMTP.send_message.calls  # pylint: disable=no-member
    smtp_len_calls = 2
    assert len(calls) == smtp_len_calls
    if failed:
        messages_expected = load_json('email_messages_failed.json')
    else:
        messages_expected = load_json('email_messages.json')
    for i in range(smtp_len_calls):
        message = _message_to_dict(calls[i]['message'])
        assert message == messages_expected[i]

    ctidy_filenames = [
        doc async for doc in db.ctidy_filenames.find().sort('_id', 1)
    ]
    expected_ctidy_filenames = [
        {
            '_id': (
                'libraries/experiments3/src/experiments3/utils/'
                'experiments3/files.cpp'
            ),
            'ticket_id': 'TAXICTIDY-7493-NEW',
        },
        {
            '_id': 'services/api-proxy/src/components/configuration.cpp',
            'ticket_id': 'TAXICTIDY-8591',
        },
        {
            '_id': 'services/cardstorage/src/statistics/stat_counter.cpp',
            'ticket_id': 'TAXICTIDY-ABS-NEW-7',
        },
        {
            '_id': 'services/umlaas/src/custom/dependencies.cpp',
            'ticket_id': 'TAXICTIDY-9813',
        },
    ]

    if failed:
        expected_ctidy_filenames.append(
            {
                '_id': 'strange-path/reposition/src/custom/failed.cpp',
                'ticket_id': 'FAILED',
            },
        )
        expected_ctidy_filenames = sorted(
            expected_ctidy_filenames, key=lambda file: file['_id'],
        )

    assert ctidy_filenames == expected_ctidy_filenames

    ctidy_authors = [
        doc async for doc in db.ctidy_authors.find().sort('_id', 1)
    ]
    assert ctidy_authors == [
        {
            '_id': 'mister_x',
            'last_send': dates.parse_timestring('2019-03-03T03:00:00+0000'),
        },
        {
            '_id': 'pupkin',
            'last_send': dates.parse_timestring('2019-03-03T03:00:00+0000'),
        },
        {
            '_id': 'vasya',
            'last_send': dates.parse_timestring('2019-03-02T12:00:00+0000'),
        },
    ]


@pytest.mark.now('2019-03-03T03:00:00+0000')
@pytest.mark.config(
    TEAMCITY_MONITORING_CTIDY_CREATE_TICKETS_ENABLED=False,
    TEAMCITY_MONITORING_CTIDY_EMAIL_ENABLED=True,
    TEAMCITY_MONITORING_CTIDY_EMAIL_BODY_TPL='{repository}\n{stacktraces}',
    TEAMCITY_MONITORING_CTIDY_DEFAULT_RECIPIENT='mister_x',
    TEAMCITY_MONITORING_CTIDY_TICKET_TITLE_TPL='{filename}',
    TEAMCITY_MONITORING_CTIDY_TICKET_BODY_TPL='{repository}\n{stacktrace}',
)
@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.usefixtures('arcanum_file_services')
async def test_ctidy_monitoring_without_ticket_creation(
        load,
        load_json,
        patch_aiohttp_session,
        response_mock,
        patch,
        monkeypatch,
        tmpdir,
        mock,
        commands_mock,
        db,
        mock_teamcity,
):
    @mock_teamcity('/app/rest/builds', prefix=True)
    def teamcity_get_build_request(request):
        return web.json_response(
            load_json('teamcity_test_builds_response.json'),
        )

    @mock_teamcity('/app/rest/testOccurrences', prefix=True)
    def teamcity_get_tests_request(request):
        return web.json_response(
            load_json('teamcity_test_occurrences_response.json'),
        )

    @patch_aiohttp_session('https://test-startrack-url/')
    def st_request(method, url, json, **kwargs):
        assert False, 'This should not run'

    class MySMTP:
        # pylint: disable=no-self-argument

        @mock
        def __init__(host, port):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        @mock
        def send_message(message):
            pass

    monkeypatch.setattr('smtplib.SMTP', MySMTP)
    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.settings.EMAIL_SEND_TO_AUTHOR',
        True,
    )
    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.settings.TICKET_URL_TPL',
        'https://test-startrack-url/{ticket_id}',
    )

    await run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'ctidy_monitoring.run_ctidy_monitoring',
            '-t',
            '0',
        ],
    )

    assert teamcity_get_tests_request.times_called == 1
    tc_get_failed_tests_args = (await teamcity_get_tests_request.wait_call())[
        'request'
    ]
    assert tc_get_failed_tests_args.url.endswith(
        '/app/rest/testOccurrences?locator=status:FAILURE,'
        'build:(id:19970909,branch:(default:true),count:1),count:-1&'
        'fields=testOccurrence(name,details,build(startDate))',
    )

    assert teamcity_get_build_request.times_called == 1
    tc_get_successful_build_args = (
        await teamcity_get_build_request.wait_call()
    )['request']
    assert tc_get_successful_build_args.url.endswith(
        '/app/rest/builds?locator=status:SUCCESS,buildType:YandexTaxiProjects_'
        'UservicesArcadia_Internal_ClangTidyCheck,count:1,'
        'branch:(default:true)&fields=build(id)',
    )

    assert not st_request.calls

    calls = MySMTP.send_message.calls  # pylint: disable=no-member
    smtp_len_calls = 2
    assert len(calls) == smtp_len_calls
    messages_expected = load_json('email_messages_without_tickets.json')
    for i in range(smtp_len_calls):
        message = _message_to_dict(calls[i]['message'])
        assert message == messages_expected[i]

    ctidy_filenames = [
        doc async for doc in db.ctidy_filenames.find().sort('_id', 1)
    ]
    assert ctidy_filenames == DEFAULT_CTIDY_NAMES_ENTRIES

    ctidy_authors = [
        doc async for doc in db.ctidy_authors.find().sort('_id', 1)
    ]
    assert ctidy_authors == [
        {
            '_id': 'mister_x',
            'last_send': dates.parse_timestring('2019-03-03T03:00:00+0000'),
        },
        {
            '_id': 'pupkin',
            'last_send': dates.parse_timestring('2019-03-03T03:00:00+0000'),
        },
        {
            '_id': 'vasya',
            'last_send': dates.parse_timestring('2019-03-02T12:00:00+0000'),
        },
    ]


@pytest.mark.config(
    TEAMCITY_MONITORING_CTIDY_CREATE_TICKETS_ENABLED=False,
    TEAMCITY_MONITORING_CTIDY_EMAIL_ENABLED=False,
    TEAMCITY_MONITORING_CTIDY_DEFAULT_RECIPIENT='mister_x',
)
@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.usefixtures('arcanum_file_services')
async def test_ctidy_monitoring_disabled_configs(
        load,
        load_json,
        patch_aiohttp_session,
        response_mock,
        patch,
        monkeypatch,
        tmpdir,
        mock,
        commands_mock,
        db,
        mock_teamcity,
):
    @mock_teamcity('/app/rest/builds', prefix=True)
    def teamcity_get_build_request(request):
        return web.json_response(
            load_json('teamcity_test_builds_response.json'),
        )

    @mock_teamcity('/app/rest/testOccurrences', prefix=True)
    def teamcity_get_tests_request(request):
        return web.json_response(
            load_json('teamcity_test_occurrences_response.json'),
        )

    @patch_aiohttp_session('https://test-startrack-url/')
    def st_request(method, url, json, **kwargs):
        assert False, 'This should not be run'

    class MySMTP:
        # pylint: disable=no-self-argument

        @mock
        def __init__(host, port):
            assert False, 'This should not be run'

        @mock
        def send_message(message):
            assert False, 'This should not be run'

    monkeypatch.setattr('smtplib.SMTP', MySMTP)
    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.settings.EMAIL_SEND_TO_AUTHOR',
        True,
    )

    await run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'ctidy_monitoring.run_ctidy_monitoring',
            '-t',
            '0',
        ],
    )

    assert teamcity_get_tests_request.times_called == 1
    tc_get_failed_tests_args = (await teamcity_get_tests_request.wait_call())[
        'request'
    ]
    assert tc_get_failed_tests_args.url.endswith(
        '/app/rest/testOccurrences?locator=status:FAILURE,'
        'build:(id:19970909,branch:(default:true),count:1),count:-1&'
        'fields=testOccurrence(name,details,build(startDate))',
    )

    assert teamcity_get_build_request.times_called == 1
    tc_get_successful_build_args = (
        await teamcity_get_build_request.wait_call()
    )['request']
    assert tc_get_successful_build_args.url.endswith(
        '/app/rest/builds?locator=status:SUCCESS,buildType:YandexTaxiProjects_'
        'UservicesArcadia_Internal_ClangTidyCheck,count:1,'
        'branch:(default:true)&fields=build(id)',
    )

    calls = st_request.calls
    assert not calls

    calls = MySMTP.send_message.calls  # pylint: disable=no-member
    assert not calls

    ctidy_filenames = [
        doc async for doc in db.ctidy_filenames.find().sort('_id', 1)
    ]
    assert ctidy_filenames == DEFAULT_CTIDY_NAMES_ENTRIES

    ctidy_authors = [
        doc async for doc in db.ctidy_authors.find().sort('_id', 1)
    ]
    assert ctidy_authors == [
        {
            '_id': 'mister_x',
            'last_send': dates.parse_timestring('2019-03-02T01:00:00.0+0000'),
        },
        {
            '_id': 'vasya',
            'last_send': dates.parse_timestring('2019-03-02T12:00:00.0+0000'),
        },
    ]


@pytest.mark.now('2019-03-03T03:00:00+0000')
@pytest.mark.config(
    TEAMCITY_MONITORING_CTIDY_CREATE_TICKETS_ENABLED=True,
    TEAMCITY_MONITORING_CTIDY_EMAIL_ENABLED=True,
    TEAMCITY_MONITORING_CTIDY_DEFAULT_RECIPIENT='mister_x',
    TEAMCITY_MONITORING_CTIDY_TICKET_TITLE_TPL='{filename}',
)
@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.usefixtures('arcanum_file_services')
async def test_ctidy_monitoring_without_any_notifying(
        load,
        load_json,
        patch_aiohttp_session,
        response_mock,
        patch,
        monkeypatch,
        tmpdir,
        mock,
        commands_mock,
        db,
        mock_teamcity,
):
    @mock_teamcity('/app/rest/builds', prefix=True)
    def teamcity_get_build_request(request):
        return web.json_response(
            load_json('teamcity_test_builds_response.json'),
        )

    @mock_teamcity('/app/rest/testOccurrences', prefix=True)
    def teamcity_get_tests_request(request):
        return web.json_response(
            load_json(
                'teamcity_test_without_notifying_occurrences_response.json',
            ),
        )

    @patch_aiohttp_session('https://test-startrack-url/')
    def st_request(method, url, json, **kwargs):
        responses = {
            'TAXICTIDY-7493': {
                'key': 'TAXICTIDY-7493',
                'status': {'key': 'closed'},
                'resolution': {'key': 'fixed'},
                'assignee': {'id': 'user442'},
                'resolvedAt': '2076-01-01T00:00:00.0+0000',
            },
            'TAXICTIDY-8591': {
                'key': 'TAXICTIDY-8591',
                'status': {'key': 'closed'},
                'resolution': {'key': 'fixed'},
                'assignee': {'id': 'user442'},
                'resolvedAt': '2074-01-01T00:00:00.0+0000',
            },
            'TAXICTIDY-9813': {
                'key': 'TAXICTIDY-9813',
                'status': {'key': 'closed'},
                'resolution': {'key': 'fixed'},
                'assignee': {'id': 'user831'},
                'resolvedAt': '2025-03-03T00:00:00.0+0000',
            },
        }
        if method == 'post':
            assert False, 'This should not run'
        ticket_id = url.split('/')[4]
        return response_mock(json=responses[ticket_id])

    class MySMTP:
        # pylint: disable=no-self-argument

        @mock
        def __init__(host, port):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        @mock
        def send_message(message):
            assert False, 'This should not run'

    monkeypatch.setattr('smtplib.SMTP', MySMTP)
    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.settings.EMAIL_SEND_TO_AUTHOR',
        True,
    )
    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.settings.TICKET_URL_TPL',
        'https://test-startrack-url/{ticket_id}',
    )

    await run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'ctidy_monitoring.run_ctidy_monitoring',
            '-t',
            '0',
        ],
    )

    assert teamcity_get_tests_request.times_called == 1
    tc_get_failed_tests_args = (await teamcity_get_tests_request.wait_call())[
        'request'
    ]
    assert tc_get_failed_tests_args.url.endswith(
        '/app/rest/testOccurrences?locator=status:FAILURE,'
        'build:(id:19970909,branch:(default:true),count:1),count:-1&'
        'fields=testOccurrence(name,details,build(startDate))',
    )

    assert teamcity_get_build_request.times_called == 1
    tc_get_successful_build_args = (
        await teamcity_get_build_request.wait_call()
    )['request']
    assert tc_get_successful_build_args.url.endswith(
        '/app/rest/builds?locator=status:SUCCESS,buildType:YandexTaxiProjects_'
        'UservicesArcadia_Internal_ClangTidyCheck,count:1,'
        'branch:(default:true)&fields=build(id)',
    )

    calls = st_request.calls
    assert len(calls) == 3
    for call in calls:
        call.pop('kwargs')
        if call['json'] is not None:
            if 'unique' in call['json']:
                call['json'].pop('unique')

    assert calls == [
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXICTIDY-8591',
            'json': None,
        },
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXICTIDY-7493',
            'json': None,
        },
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXICTIDY-9813',
            'json': None,
        },
    ]

    calls = MySMTP.send_message.calls  # pylint: disable=no-member
    assert not calls

    ctidy_filenames = [
        doc async for doc in db.ctidy_filenames.find().sort('_id', 1)
    ]
    assert ctidy_filenames == [
        {
            '_id': (
                'libraries/experiments3/src/experiments3/utils/'
                'experiments3/files.cpp'
            ),
            'ticket_id': 'TAXICTIDY-7493',
        },
        {
            '_id': 'services/api-proxy/src/components/configuration.cpp',
            'ticket_id': 'TAXICTIDY-8591',
        },
        {
            '_id': 'services/umlaas/src/custom/dependencies.cpp',
            'ticket_id': 'TAXICTIDY-9813',
        },
    ]

    ctidy_authors = [
        doc async for doc in db.ctidy_authors.find().sort('_id', 1)
    ]
    assert ctidy_authors == [
        {
            '_id': 'mister_x',
            'last_send': dates.parse_timestring('2019-03-02T01:00:00+0000'),
        },
        {
            '_id': 'vasya',
            'last_send': dates.parse_timestring('2019-03-02T12:00:00+0000'),
        },
    ]


@pytest.mark.config(
    TEAMCITY_MONITORING_CTIDY_CREATE_TICKETS_ENABLED=True,
    TEAMCITY_MONITORING_CTIDY_EMAIL_ENABLED=True,
)
@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.usefixtures('arcanum_file_services')
async def test_empty_crontask(
        load_json,
        mock_teamcity,
        commands_mock,
        patch_aiohttp_session,
        patch,
        mock,
        monkeypatch,
):
    @mock_teamcity('/app/rest/builds', prefix=True)
    def teamcity_get_build_request(request):
        return web.json_response(
            load_json('teamcity_test_builds_response.json'),
        )

    @mock_teamcity('/app/rest/testOccurrences', prefix=True)
    def teamcity_get_tests_request(request):
        return web.json_response(
            load_json('teamcity_test_empty_occurrences_response.json'),
        )

    @patch_aiohttp_session('https://test-startrack-url/')
    def st_request(method, url, json, **kwargs):
        assert False, 'This should not run'

    class MySMTP:
        # pylint: disable=no-self-argument

        @mock
        def __init__(host, port):
            assert False, 'This should not run'

    monkeypatch.setattr('smtplib.SMTP', MySMTP)

    await run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'ctidy_monitoring.run_ctidy_monitoring',
            '-t',
            '0',
        ],
    )

    assert teamcity_get_tests_request.times_called == 1
    tc_get_failed_tests_args = (await teamcity_get_tests_request.wait_call())[
        'request'
    ]
    assert tc_get_failed_tests_args.url.endswith(
        '/app/rest/testOccurrences?locator=status:FAILURE,'
        'build:(id:19970909,branch:(default:true),count:1),count:-1&'
        'fields=testOccurrence(name,details,build(startDate))',
    )

    assert teamcity_get_build_request.times_called == 1
    tc_get_successful_build_args = (
        await teamcity_get_build_request.wait_call()
    )['request']
    assert tc_get_successful_build_args.url.endswith(
        '/app/rest/builds?locator=status:SUCCESS,buildType:YandexTaxiProjects_'
        'UservicesArcadia_Internal_ClangTidyCheck,count:1,'
        'branch:(default:true)&fields=build(id)',
    )

    assert not st_request.calls


# pylint: disable=protected-access
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            ExtractPathTestParams(
                filename='services/service_name/some/service_file.cpp',
                expected_yaml={'some_service': 'info'},
            ),
            id='service_yaml',
        ),
        pytest.param(
            ExtractPathTestParams(
                filename='libraries/lib/name/more/deep/path/',
                expected_yaml={'some_lib': 'info'},
            ),
            id='library_yaml',
        ),
        pytest.param(
            ExtractPathTestParams(
                filename='some/wrong/path/name', expected_yaml=None,
            ),
            id='absent_yaml',
        ),
        pytest.param(
            ExtractPathTestParams(
                filename='/absolute/path/for/some/name.py', expected_yaml=None,
            ),
            id='absolute_path',
        ),
    ],
)
def test_extract_entity_yaml_path(params, tmpdir):
    root = pathlib.Path(tmpdir.mkdir('repo'))

    service_yaml_path = root / 'services' / 'service_name' / 'service.yaml'
    service_yaml_path.parent.mkdir(parents=True, exist_ok=True)
    service_yaml_path.write_text('some_service: info')
    library_yaml_path = root / 'libraries' / 'lib' / 'name' / 'library.yaml'
    library_yaml_path.parent.mkdir(parents=True, exist_ok=True)
    library_yaml_path.write_text('some_lib: info')

    output_yaml = utils._extract_entity_yaml_path(
        pathlib.Path(params.filename), root,
    )
    assert output_yaml == params.expected_yaml


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            StartrekLinkParams(
                filename='services/service_name/some/file.cpp',
                expected_startrek_link='((https://a.yandex-team.ru/arc_vcs/'
                'taxi/uservices/services/service_name/some/'
                'file.cpp services/service_name/some/file.cpp))',
            ),
            id='File from services',
        ),
        pytest.param(
            StartrekLinkParams(
                filename='libraries/lib-sample/src/lib-sample.cpp',
                expected_startrek_link='((https://a.yandex-team.ru/arc_vcs/'
                'taxi/uservices/libraries/lib-sample/'
                'src/lib-sample.cpp libraries/lib-sample/src/lib-sample.cpp))',
            ),
            id='File from libraries',
        ),
        pytest.param(
            StartrekLinkParams(
                filename='build/lib-sample/src/some_file.cpp',
                expected_startrek_link='build/lib-sample/src/some_file.cpp',
            ),
            id='File from build',
        ),
        pytest.param(
            StartrekLinkParams(
                filename='../some/path/outside/taxi/uservices/file.cpp',
                expected_startrek_link='../some/path/outside/taxi/'
                'uservices/file.cpp',
            ),
            id='File outside taxi/uservices',
        ),
    ],
)
def test_startrek_link_to_arcadia(params):
    startrek_link = run_ctidy_monitoring._startrek_link_to_arcadia(
        params.filename,
    )
    assert startrek_link == params.expected_startrek_link


# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
@pytest.mark.now('2019-03-03T03:00:00+0000')
@pytest.mark.config(
    TEAMCITY_MONITORING_CTIDY_CREATE_TICKETS_ENABLED=True,
    TEAMCITY_MONITORING_CTIDY_EMAIL_ENABLED=True,
    TEAMCITY_MONITORING_CTIDY_CLOSE_RESOLVED_TICKETS=True,
    TEAMCITY_MONITORING_CTIDY_EMAIL_BODY_TPL='{repository}\n{stacktraces}',
    TEAMCITY_MONITORING_CTIDY_DEFAULT_RECIPIENT='mister_x',
    TEAMCITY_MONITORING_CTIDY_TICKET_TITLE_TPL='{filename}',
    TEAMCITY_MONITORING_CTIDY_TICKET_BODY_TPL='{filename}\n'
    '{repository}\n{stacktrace}',
)
@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.usefixtures('arcanum_file_services')
async def test_startrek_failed(
        load,
        load_json,
        patch_aiohttp_session,
        response_mock,
        patch,
        monkeypatch,
        tmpdir,
        mock,
        commands_mock,
        db,
        mock_teamcity,
):
    await db.ctidy_filenames.insert_one(
        {
            '_id': 'strange-path/reposition/src/custom/failed.cpp',
            'ticket_id': 'FAILED',
        },
    )
    await test_ctidy_monitoring(
        load,
        load_json,
        patch_aiohttp_session,
        response_mock,
        patch,
        monkeypatch,
        tmpdir,
        mock,
        commands_mock,
        db,
        mock_teamcity,
        failed=True,
    )


# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
@pytest.mark.now('2019-03-03T03:00:00+0000')
@pytest.mark.config(TEAMCITY_MONITORING_CTIDY_DIFF_THRESHOLD=2)
@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.usefixtures('arcanum_file_services')
async def test_ctidy_diff_threshold(
        load,
        load_json,
        patch_aiohttp_session,
        response_mock,
        patch,
        monkeypatch,
        tmpdir,
        mock,
        commands_mock,
        db,
        mock_teamcity,
):
    await test_ctidy_monitoring(
        load,
        load_json,
        patch_aiohttp_session,
        response_mock,
        patch,
        monkeypatch,
        tmpdir,
        mock,
        commands_mock,
        db,
        mock_teamcity,
        arcanum_file_services,
        threshold=True,
    )


# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
@pytest.mark.now('2019-03-03T03:00:00+0000')
@pytest.mark.config(
    TEAMCITY_MONITORING_CTIDY_CLOSE_RESOLVED_TICKETS=True,
    TEAMCITY_MONITORING_CTIDY_EMAIL_BODY_TPL='{repository}\n{stacktraces}',
    TEAMCITY_MONITORING_CTIDY_DEFAULT_RECIPIENT='mister_x',
    TEAMCITY_MONITORING_CTIDY_TICKET_TITLE_TPL='{filename}',
    TEAMCITY_MONITORING_CTIDY_TICKET_BODY_TPL='{repository}\n{stacktrace}',
)
@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.usefixtures('arcanum_file_services')
@pytest.mark.filldb(ctidy_filenames='queue_extra')
async def test_fail_db_remove(
        load,
        load_json,
        patch_aiohttp_session,
        response_mock,
        patch,
        monkeypatch,
        tmpdir,
        mock,
        commands_mock,
        db,
        mock_teamcity,
):
    @mock_teamcity('/app/rest/builds', prefix=True)
    def teamcity_get_build_request(request):
        return web.json_response(
            load_json('teamcity_test_builds_response.json'),
        )

    @mock_teamcity('/app/rest/testOccurrences', prefix=True)
    def teamcity_get_tests_request(request):
        return web.json_response(
            load_json('teamcity_test_occurrences_response.json'),
        )

    @patch_aiohttp_session('https://test-startrack-url/')
    def st_request(method, url, json, **kwargs):
        ticket_id = url.split('/')[4]
        if ticket_id == 'TAXICTIDY-1111':
            return response_mock(
                json={
                    'key': 'TAXICTIDY-1111',
                    'status': {'key': 'closed'},
                    'resolution': {'key': 'fixed'},
                    'assignee': {'id': 'user831'},
                    'resolvedAt': '2025-03-03T00:00:00.0+0000',
                },
            )
        if ticket_id == 'TAXICTIDY-7894':
            return response_mock(
                json={'key': 'TAXICTIDY-7894', 'status': {'key': 'open'}},
            )

        if ticket_id == 'FAILED':
            raise clients_startrek.NotFoundError('Ticket not found.')
        if ticket_id == 'BREAKER':
            raise clients_startrek.BaseError('something goes wrong')
        return response_mock(json={})

    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.settings.TICKET_URL_TPL',
        'https://test-startrack-url/{ticket_id}',
    )

    commands = [
        'taxi_teamcity_monitoring.crontasks.'
        'ctidy_monitoring.run_ctidy_monitoring',
        '-t',
        '0',
    ]

    with pytest.raises(run_ctidy_monitoring.CtidyMonitoringError):
        await run_cron.main(commands)

    assert teamcity_get_tests_request.times_called == 1
    tc_get_failed_tests_args = (await teamcity_get_tests_request.wait_call())[
        'request'
    ]
    assert tc_get_failed_tests_args.url.endswith(
        '/app/rest/testOccurrences?locator=status:FAILURE,'
        'build:(id:19970909,branch:(default:true),count:1),count:-1&'
        'fields=testOccurrence(name,details,build(startDate))',
    )

    assert teamcity_get_build_request.times_called == 1
    tc_get_build_args = (await teamcity_get_build_request.wait_call())[
        'request'
    ]
    assert tc_get_build_args.url.endswith(
        '/app/rest/builds?locator=status:SUCCESS,buildType:YandexTaxiProjects_'
        'UservicesArcadia_Internal_ClangTidyCheck,count:1,'
        'branch:(default:true)&fields=build(id)',
    )

    calls = st_request.calls
    assert len(calls) == 4
    for call in calls:
        call.pop('kwargs')
        if call['json'] is not None:
            if 'unique' in call['json']:
                call['json'].pop('unique')

    expected_calls = [
        {
            'json': {'resolution': 'fixed'},
            'method': 'post',
            'url': (
                'https://test-startrack-url/issues/TAXICTIDY-7894/'
                'transitions/close/_execute'
            ),
        },
        {
            'json': {'resolution': 'fixed'},
            'method': 'post',
            'url': (
                'https://test-startrack-url/issues/TAXICTIDY-1111/'
                'transitions/close/_execute'
            ),
        },
        {
            'json': {'resolution': 'fixed'},
            'method': 'post',
            'url': (
                'https://test-startrack-url/issues/FAILED/'
                'transitions/close/_execute'
            ),
        },
        {
            'json': {'resolution': 'fixed'},
            'method': 'post',
            'url': (
                'https://test-startrack-url/issues/BREAKER/'
                'transitions/close/_execute'
            ),
        },
    ]

    assert calls == expected_calls

    ctidy_filenames = [
        doc async for doc in db.ctidy_filenames.find().sort('_id', 1)
    ]
    expected_ctidy_filenames = [
        {
            '_id': 'services/cerebellum/src/web/test_service.py',
            'ticket_id': 'BREAKER',
        },
    ]
    assert ctidy_filenames == expected_ctidy_filenames

    ctidy_authors = [
        doc async for doc in db.ctidy_authors.find().sort('_id', 1)
    ]
    assert ctidy_authors == [
        {
            '_id': 'mister_x',
            'last_send': dates.parse_timestring('2019-03-02T01:00:00+0000'),
        },
        {
            '_id': 'vasya',
            'last_send': dates.parse_timestring('2019-03-02T12:00:00+0000'),
        },
    ]


async def test_no_successful_builds(load_json, mock_teamcity):
    @mock_teamcity('/app/rest/builds', prefix=True)
    def teamcity_get_build_request(request):
        return web.json_response(
            load_json('teamcity_test_builds_empty_response.json'),
        )

    commands = [
        'taxi_teamcity_monitoring.crontasks.'
        'ctidy_monitoring.run_ctidy_monitoring',
        '-t',
        '0',
    ]

    with pytest.raises(run_ctidy_monitoring.CtidyMonitoringError):
        await run_cron.main(commands)

    assert teamcity_get_build_request.times_called == 1
    tc_get_successful_build_args = (
        await teamcity_get_build_request.wait_call()
    )['request']
    assert tc_get_successful_build_args.url.endswith(
        '/app/rest/builds?locator=status:SUCCESS,buildType:YandexTaxiProjects_'
        'UservicesArcadia_Internal_ClangTidyCheck,count:1,'
        'branch:(default:true)&fields=build(id)',
    )
