import json as json_module
import os

from aiohttp import web
import pytest

from taxi import discovery
from taxi.util import dates
from yandex.arc.api.public import repo_pb2

from taxi_teamcity_monitoring.generated.cron import run_cron

BACKEND_PY3_REPO = 'backend-py3'
USERVICES_REPO = 'uservices'
ARC_USERVICES_REPO = 'taxi/uservices'
BACKEND_PY3_BUILDTYPE = 'YandexTaxiProjects_TaxiBackendPy3_PullRequests'
USERVICES_BUILDTYPE = 'YandexTaxiProjects_Uservices_PullRequests'
ARC_USERVICES_BUILDTYPE = (
    'YandexTaxiProjects_UservicesArcadia_PullRequests_PullRequests'
)
EXAMPLE_YAML_CONTENT = 'maintainers:\n  - %s <%s@yandex-team.ru>\n'


@pytest.fixture
def arcanum_file_services(mock, patch_file_service, arc_mockserver):
    @mock
    def _read_file(request, context):
        data = EXAMPLE_YAML_CONTENT % ('aserebriyskiy', 'aserebriyskiy')
        yield repo_pb2.ReadFileResponse(
            Header=repo_pb2.ReadFileResponse.ReadFileHeader(
                Oid='853cb0f6a5888d6ecfe2c7acc6a90d42af85b89c',
                FileSize=len(data),
            ),
        )
        yield repo_pb2.ReadFileResponse(Data=bytes(data, 'utf-8'))

    file_service_mock = patch_file_service(read_file=_read_file)
    arc_mockserver(file_service_mock)


def message_to_dict(message):
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
    TEAMCITY_MONITORING_FLAP_EMAIL_BODY_TEMPLATE='{tests}',
    TEAMCITY_MONITORING_FLAP_EMAIL_ENABLED=True,
    TEAMCITY_MONITORING_FLAP_CREATE_TICKETS_ENABLED=True,
    TEAMCITY_MONITORING_FLAP_ENABLED=True,
    TEAMCITY_MONITORING_FLAP_REPO_TO_BUILD_ID={
        BACKEND_PY3_REPO: BACKEND_PY3_BUILDTYPE,
        USERVICES_REPO: USERVICES_BUILDTYPE,
        ARC_USERVICES_REPO: ARC_USERVICES_BUILDTYPE,
    },
    TEAMCITY_MONITORING_FLAP_TICKET_TITLE_TPL=(
        '{repo_name} Починить {test_name}'
    ),
)
@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.usefixtures('arcanum_file_services')
async def test_flaps_monitoring(
        load_json,
        patch_aiohttp_session,
        response_mock,
        patch,
        monkeypatch,
        tmpdir,
        mock,
        async_commands_mock,
        db,
        mock_teamcity,
):
    @mock_teamcity('/app/rest/testOccurrences', prefix=True)
    def teamcity_request(request):
        locator = request.args['locator']
        loaded_json = None
        if BACKEND_PY3_BUILDTYPE in locator:
            loaded_json = load_json(
                'teamcity_backend_py3_failed_tests_response.json',
            )
        elif USERVICES_BUILDTYPE in locator:
            loaded_json = load_json(
                'teamcity_uservices_failed_tests_response.json',
            )
        elif ARC_USERVICES_BUILDTYPE in locator:
            loaded_json = load_json(
                'teamcity_arc_uservices_failed_tests_response.json',
            )

        if loaded_json is None:
            assert False, 'Incorrect locator for teamcity request!!!'
        return web.json_response(loaded_json)

    @patch_aiohttp_session(discovery.find_service('wiki').url)
    def wiki_request(method, url, json, **kwargs):
        return response_mock()

    @patch_aiohttp_session('http://s3.mds.yandex.net/common')
    def s3_request(method, url, **kwargs):
        response = response_mock(headers={'ETag': ''})
        response.status_code = response.status
        response.raw_headers = [
            (k.encode(), v.encode()) for k, v in response.headers.items()
        ]
        return response

    @patch_aiohttp_session('https://test-startrack-url/')
    def st_request(method, url, json, **kwargs):
        if method == 'post':
            return response_mock(json={'key': 'TAXIFLAPTEST-777'})
        ticket_id = url.split('/')[4]
        responses = {
            'TAXIFLAPTEST-123': {
                'key': 'TAXIFLAPTEST-123',
                'status': {'key': 'closed'},
                'resolution': {'key': 'fixed'},
                'assignee': {'id': 'example1'},
                'resolvedAt': '2010-01-01T00:00:00.0+0000',
            },
            'TAXIFLAPTEST-3546': {
                'key': 'TAXIFLAPTEST-3546',
                'status': {'key': 'open'},
                'assignee': {'id': 'example3'},
            },
            'TAXIFLAPTEST-9999': {
                'key': 'TAXIFLAPTEST-9999',
                'status': {'key': 'closed'},
                'resolution': {'key': 'fixed'},
                'assignee': {'id': 'example4'},
                'resolvedAt': '2019-03-03T00:00:00.0+0000',
            },
        }
        return response_mock(json=responses[ticket_id])

    @async_commands_mock('/usr/bin/git')
    async def git(args, **kwargs):
        cwd = kwargs['cwd']
        repo_url = args[-1]
        if BACKEND_PY3_REPO in repo_url:
            repo = BACKEND_PY3_REPO
        elif USERVICES_REPO in repo_url:
            repo = USERVICES_REPO
        else:
            assert False, 'Try to clone incorrect repository!!!'

        root = os.path.join(cwd, repo)

        def mkfile(filename):
            full_path = os.path.join(root, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            open(full_path, 'w').close()

        def mk_service_yaml(filename, author):
            entity_yaml = 'service.yaml'
            if filename.startswith('libraries'):
                entity_yaml = 'library.yaml'
            full_path = os.path.join(root, filename, entity_yaml)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as fin:
                fin.write(
                    'maintainers:\n'
                    '  - %s <%s@yandex-team.ru>\n' % (author, author),
                )

        if not os.path.exists(root):
            os.mkdir(root)
        if repo == BACKEND_PY3_REPO:
            mkfile(
                'example-service/test_example_service/cron/'
                'test_blacksuite.py',
            )
            mkfile('clownductor/test_clownductor/web/test_tasks.py')
            mkfile('feeds-admin/test_feeds_admin/web/test_all.py')

            mk_service_yaml('example-service/', 'seanchaidh')
            mk_service_yaml('clownductor/', 'vitja')
            mk_service_yaml('feeds-admin', 'mister_x')
        elif repo == USERVICES_REPO:
            mkfile('services/driver_authorizer/testsuite/test_chat_add.py')
            mkfile(
                'services/driver_authorizer/testsuite/' 'test_driver_check.py',
            )
            mkfile(
                'services/driver_authorizer/testsuite/'
                'test_driver_client_token.py',
            )
            mkfile(
                'services/driver_authorizer/testsuite/'
                'test_driver_client_token.py',
            )
            mkfile('services/hejmdal/testsuite/tests_hejmdal.py')
            mk_service_yaml('services/driver_authorizer/', 'mister_x')
            mk_service_yaml('services/hejmdal', 'seanchaidh')
        return ''

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

    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.settings.S3_SEND_TO_BUCKET', True,
    )

    @patch('tempfile.mkdtemp')
    def mkdtemp(*args, **kwargs):
        return str(tmpdir.mkdir('repo'))

    await run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'flaps_monitoring.run_flaps_monitoring',
            '-t',
            '0',
        ],
    )

    teamcity_request_times_called = 3
    expected_query_url_pattern = (
        '/app/rest/testOccurrences?'
        'locator=status:FAILURE,build:(project:(id:{buildtype_id}),'
        'branch:default:any,lookupLimit:1000,count:-1),'
        'count:-1&fields=testOccurrence(name,'
        'build(id,branchName,startDate,problemOccurrences(problemOccurrence('
        'details))),test(id))'
    )
    expected_query_url_parts = [
        expected_query_url_pattern.format(buildtype_id=BACKEND_PY3_BUILDTYPE),
        expected_query_url_pattern.format(buildtype_id=USERVICES_BUILDTYPE),
        expected_query_url_pattern.format(
            buildtype_id=ARC_USERVICES_BUILDTYPE,
        ),
    ]

    assert teamcity_request.times_called == teamcity_request_times_called
    for i in range(teamcity_request_times_called):
        tc_request_args = (await teamcity_request.wait_call())['request']
        assert tc_request_args.url.endswith(expected_query_url_parts[i])

    calls = mkdtemp.calls
    assert len(calls) == 2

    calls = git.calls
    assert len(calls) == 2
    for call in calls:
        call.pop('kwargs')
        call['args'] = call['args']
    assert calls == [
        {
            'args': (
                '/usr/bin/git',
                'clone',
                'https://github.yandex-team.ru/taxi/backend-py3.git',
            ),
        },
        {
            'args': (
                '/usr/bin/git',
                'clone',
                'https://github.yandex-team.ru/taxi/uservices.git',
            ),
        },
    ]

    calls = st_request.calls
    assert len(calls) == 17
    for call in calls:
        call.pop('kwargs')
        if call['json'] is not None:
            call['json'].pop('unique')

    assert calls == [
        {
            'json': None,
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXIFLAPTEST-3546',
        },
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXIFLAPTEST-9999',
            'json': None,
        },
        {
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
            'json': {
                'summary': 'backend-py3 Починить test_example_task',
                'queue': {'key': 'TAXIFLAPTEST'},
                'description': (
                    ' Название: example-service.test_example_service.cron.'
                    'test_blacksuite.test_example_task\n'
                    'Проект: backend-py3\n'
                    '((https://teamcity.taxi.yandex-team.ru/project.html'
                    '?projectId=YandexTaxiProjects_TaxiBackendPy3_PullRequests'
                    '&testNameId=-8445431642882081800&'
                    'tab=testDetails&order=TEST_STATUS_DESC История флапов)) '
                ),
                'type': {'key': 'task'},
                'assignee': 'seanchaidh',
                'tags': ['backend-py3', 'test_example_service'],
            },
        },
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXIFLAPTEST-123',
            'json': None,
        },
        {
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
            'json': {
                'summary': 'backend-py3 Починить test_feature',
                'queue': {'key': 'TAXIFLAPTEST'},
                'description': (
                    ' Название: feeds-admin.test_feeds_admin.web.test_all.'
                    'test_feature\n'
                    'Проект: backend-py3\n'
                    '((https://teamcity.taxi.yandex-team.ru/'
                    'project.html?projectId='
                    'YandexTaxiProjects_TaxiBackendPy3_PullRequests&'
                    'testNameId=7167503634659557009&'
                    'tab=testDetails&order=TEST_STATUS_DESC История флапов)) '
                ),
                'type': {'key': 'task'},
                'assignee': 'mister_x',
                'links': [
                    {'relationship': 'relates', 'issue': 'TAXIFLAPTEST-123'},
                ],
                'tags': ['backend-py3', 'test_feeds_admin'],
            },
        },
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXIFLAPTEST-3546',
            'json': None,
        },
        {
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
            'json': {
                'summary': 'backend-py3 Починить test_something',
                'queue': {'key': 'TAXIFLAPTEST'},
                'description': (
                    ' Название: feeds-admin.test_feeds_admin.web.'
                    'test_all.test_something'
                    '\nПроект: backend-py3'
                    '\n((https://teamcity.taxi.yandex-team.ru/'
                    'project.html?projectId='
                    'YandexTaxiProjects_TaxiBackendPy3_PullRequests&'
                    'testNameId=1735672660920589010&'
                    'tab=testDetails&order=TEST_STATUS_DESC История флапов)) '
                ),
                'type': {'key': 'task'},
                'assignee': 'mister_x',
                'tags': ['backend-py3', 'test_feeds_admin'],
            },
        },
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXIFLAPTEST-123',
            'json': None,
        },
        {
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
            'json': {
                'summary': 'uservices Починить test_feature',
                'queue': {'key': 'TAXIFLAPTEST'},
                'description': (
                    ' Название: services.driver_authorizer.testsuite.'
                    'test_all.test_feature\n'
                    'Проект: uservices\n'
                    '((https://teamcity.taxi.yandex-team.ru/project.html?'
                    'projectId=YandexTaxiProjects_Uservices_PullRequests&'
                    'testNameId=7158394725659589009&'
                    'tab=testDetails&order=TEST_STATUS_DESC История флапов)) '
                ),
                'type': {'key': 'task'},
                'assignee': 'mister_x',
                'links': [
                    {'relationship': 'relates', 'issue': 'TAXIFLAPTEST-123'},
                ],
                'tags': ['uservices', 'driver_authorizer'],
            },
        },
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXIFLAPTEST-3546',
            'json': None,
        },
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXIFLAPTEST-9999',
            'json': None,
        },
        {
            'method': 'get',
            'url': 'https://test-startrack-url/issues/TAXIFLAPTEST-9999',
            'json': None,
        },
        {
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
            'json': {
                'summary': 'uservices Починить test_no_message',
                'queue': {'key': 'TAXIFLAPTEST'},
                'description': (
                    ' Название: services.driver_authorizer.'
                    'testsuite.test_chat_add.test_no_message\n'
                    'Проект: uservices\n'
                    '((https://teamcity.taxi.yandex-team.ru/'
                    'project.html?projectId='
                    'YandexTaxiProjects_Uservices_PullRequests'
                    '&testNameId='
                    '-7867456256208523264&tab=testDetails&'
                    'order=TEST_STATUS_DESC История флапов)) '
                ),
                'type': {'key': 'task'},
                'assignee': 'mister_x',
                'links': [
                    {'relationship': 'relates', 'issue': 'TAXIFLAPTEST-9999'},
                ],
                'tags': ['uservices', 'driver_authorizer'],
            },
        },
        {
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
            'json': {
                'summary': 'uservices Починить test_driver_cost',
                'queue': {'key': 'TAXIFLAPTEST'},
                'description': (
                    ' Название: services.driver_authorizer.testsuite.'
                    'test_driver_cost.test_driver_cost\n'
                    'Проект: uservices\n'
                    '((https://teamcity.taxi.yandex-team.ru/project.html?'
                    'projectId=YandexTaxiProjects_Uservices_PullRequests&'
                    'testNameId=-1514671559710586989&tab=testDetails&'
                    'order=TEST_STATUS_DESC История флапов)) '
                ),
                'type': {'key': 'task'},
                'assignee': 'mister_x',
                'tags': ['uservices', 'driver_authorizer'],
            },
        },
        {
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
            'json': {
                'summary': 'uservices Починить tests_hejmdal',
                'queue': {'key': 'TAXIFLAPTEST'},
                'description': (
                    ' Название: services.hejmdal.testsuite.tests_hejmdal\n'
                    'Проект: uservices\n'
                    '((https://teamcity.taxi.yandex-team.ru/project.html?'
                    'projectId=YandexTaxiProjects_Uservices_PullRequests&'
                    'testNameId=9875465135798745654&tab=testDetails&'
                    'order=TEST_STATUS_DESC История флапов)) '
                ),
                'type': {'key': 'task'},
                'assignee': 'seanchaidh',
                'tags': ['uservices', 'hejmdal'],
            },
        },
        {
            'json': {
                'assignee': 'aserebriyskiy',
                'description': (
                    ' Название: services.yagr.testsuite.tests_yagr.test_driver'
                    '_v1_position_store.test_driver_position_store_'
                    'basic_check\n'
                    'Проект: taxi/uservices\n'
                    '((https://teamcity.taxi.yandex-team.ru/project.html?'
                    'projectId=YandexTaxiProjects_UservicesArcadia_'
                    'PullRequests_PullRequests&testNameId=965994995585541085&'
                    'tab=testDetails&order=TEST_STATUS_DESC '
                    'История флапов)) '
                ),
                'queue': {'key': 'TAXIFLAPTEST'},
                'summary': (
                    'taxi/uservices Починить '
                    'test_driver_position_store_basic_check'
                ),
                'tags': ['taxi/uservices', 'yagr'],
                'type': {'key': 'task'},
            },
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
        },
        {
            'json': {
                'assignee': 'aserebriyskiy',
                'description': (
                    ' Название: services.yagr.testsuite.tests_yagr.'
                    'test_service_v2_position_store.test_service_v2_position_'
                    'store_basic_check\n'
                    'Проект: taxi/uservices\n'
                    '((https://teamcity.taxi.yandex-team.ru/project.html?'
                    'projectId=YandexTaxiProjects_UservicesArcadia_'
                    'PullRequests_PullRequests&testNameId=-2424806541626831688'
                    '&tab=testDetails&order=TEST_STATUS_DESC '
                    'История флапов)) '
                ),
                'queue': {'key': 'TAXIFLAPTEST'},
                'summary': (
                    'taxi/uservices Починить '
                    'test_service_v2_position_store_basic_check'
                ),
                'tags': ['taxi/uservices', 'yagr'],
                'type': {'key': 'task'},
            },
            'method': 'post',
            'url': 'https://test-startrack-url/issues',
        },
    ]

    calls = MySMTP.send_message.calls  # pylint: disable=no-member
    assert len(calls) == 3
    messages_expected = load_json('email_messages.json')
    messages = [message_to_dict(call['message']) for call in calls]
    assert messages == messages_expected

    calls = s3_request.calls
    assert len(calls) == 1
    call = calls[0]
    flaps = json_module.loads(call['kwargs']['data'].read().decode('utf-8'))
    assert flaps == [
        'clownductor.test_clownductor.web.test_tasks.test_pull_flap',
        'clownductor.test_clownductor.web.test_tasks.'
        'test_task_change_statuses',
        'example-service.test_example_service.cron.'
        'test_blacksuite.test_example_task',
        'feeds-admin.test_feeds_admin.web.test_all.test_feature',
        'feeds-admin.test_feeds_admin.web.test_all.test_fff',
        'feeds-admin.test_feeds_admin.web.test_all.test_something',
        'services.driver_authorizer.testsuite.test_all.test_feature',
        'services.driver_authorizer.testsuite.test_all.test_fff',
        'services.driver_authorizer.testsuite.test_all.test_something',
        'services.driver_authorizer.testsuite.test_chat_add.test_no_message',
        'services.driver_authorizer.testsuite.'
        'test_driver_cost.test_driver_cost',
        'services.hejmdal.testsuite.tests_hejmdal',
        'services.some_service.testsuite.test_some.test_some_success',
        (
            'services.yagr.testsuite.tests_yagr.test_driver_v1_position_store.'
            'test_driver_position_store_basic_check'
        ),
        (
            'services.yagr.testsuite.tests_yagr.test_service_v2_position_store'
            '.test_service_v2_position_store_basic_check'
        ),
        'testsuite.tests.protocol.test_ololo.test_ping',
    ]
    call.pop('kwargs')
    assert call == {
        'method': 'put',
        'url': 'http://s3.mds.yandex.net/common/flap_tests',
    }

    json_expected = load_json('wiki_page_content.json')
    calls = wiki_request.calls
    assert len(calls) == 1
    call = calls[0]
    assert call['url'] == (
        'https://wiki-api.test.yandex-team.ru/_api/frontend/users/'
        'robot-taxi-test/flappingtests/'
    )
    assert call['json'] == json_expected

    flap_tests = [
        doc
        async for doc in db.flap_tests.find({'status': 'open'}).sort('_id', 1)
    ]
    assert flap_tests == [
        {
            '_id': (
                'clownductor.test_clownductor.web.test_tasks.test_pull_flap'
            ),
            'repository': 'backend-py3',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-3546',
        },
        {
            '_id': (
                'example-service.test_example_service.cron.'
                'test_blacksuite.test_example_task'
            ),
            'repository': 'backend-py3',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-777',
        },
        {
            '_id': 'feeds-admin.test_feeds_admin.web.test_all.test_feature',
            'repository': 'backend-py3',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-777',
        },
        {
            '_id': 'feeds-admin.test_feeds_admin.web.test_all.test_fff',
            'repository': 'backend-py3',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-3546',
        },
        {
            '_id': 'feeds-admin.test_feeds_admin.web.test_all.test_something',
            'repository': 'backend-py3',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-777',
        },
        {
            '_id': (
                'services.driver_authorizer.testsuite.test_all.test_feature'
            ),
            'repository': 'uservices',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-777',
        },
        {
            '_id': 'services.driver_authorizer.testsuite.test_all.test_fff',
            'repository': 'uservices',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-3546',
        },
        {
            '_id': (
                'services.driver_authorizer.testsuite.'
                'test_chat_add.test_no_message'
            ),
            'repository': 'uservices',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-777',
        },
        {
            '_id': (
                'services.driver_authorizer.testsuite.'
                'test_driver_cost.test_driver_cost'
            ),
            'repository': 'uservices',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-777',
        },
        {
            '_id': 'services.hejmdal.testsuite.tests_hejmdal',
            'repository': 'uservices',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-777',
        },
        {
            '_id': (
                'services.some_service.testsuite.test_some.test_some_success'
            ),
            'repository': 'backend-py3',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-666',
        },
        {
            '_id': (
                'services.yagr.testsuite.tests_yagr.test_driver_v1_position_'
                'store.test_driver_position_store_basic_check'
            ),
            'repository': 'taxi/uservices',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-777',
        },
        {
            '_id': (
                'services.yagr.testsuite.tests_yagr.test_service_v2_position_'
                'store.test_service_v2_position_store_basic_check'
            ),
            'repository': 'taxi/uservices',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-777',
        },
        {
            '_id': 'testsuite.tests.protocol.test_ololo.test_ping',
            'repository': 'backend-py3',
            'status': 'open',
            'ticket_id': 'TAXIFLAPTEST-9191',
        },
    ]

    flap_authors = [doc async for doc in db.flap_authors.find().sort('_id', 1)]
    assert flap_authors == [
        {
            '_id': 'aserebriyskiy',
            'last_send': dates.parse_timestring('2019-03-03T03:00:00+0000'),
        },
        {
            '_id': 'example1',
            'last_send': dates.parse_timestring('2016-05-02T00:00:00+0000'),
        },
        {
            '_id': 'mister_x',
            'last_send': dates.parse_timestring('2019-03-03T03:00:00+0000'),
        },
        {
            '_id': 'seanchaidh',
            'last_send': dates.parse_timestring('2019-03-03T01:00:00+0000'),
        },
        {
            '_id': 'vitja',
            'last_send': dates.parse_timestring('2019-03-03T03:00:00+0000'),
        },
    ]
