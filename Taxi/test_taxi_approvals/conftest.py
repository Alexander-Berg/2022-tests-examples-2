# pylint: disable=redefined-outer-name, unused-variable
import datetime
import os
import pathlib

import pytest

from taxi.clients import approvals
from taxi.clients import startrack
from taxi.pytest_plugins import service

import taxi_approvals.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from taxi_approvals import app_stq  # noqa: I100
from taxi_approvals import cron_run
from taxi_approvals.generated.web import run_web
import test_taxi_approvals


CHECK_DATA_RESPONSE = {'change_doc_id': 'test_doc_id'}

pytest_plugins = [
    'taxi_approvals.generated.service.pytest_plugins',
    'taxi_testsuite.plugins.mocks.localizations_replica',
]


@pytest.fixture(name='pgsql_local', scope='session')
def _pgsql_local(pgsql_local_create):
    service_name = 'taxi-approvals'
    pgsql_db_names = ['approvals']
    tests_dir = pathlib.Path(__file__).parent
    databases = service.pgsql_discover(tests_dir, service_name, pgsql_db_names)
    return pgsql_local_create(databases)


@pytest.fixture
async def taxi_approvals_app_stq(loop, db, pgsql, pgsql_local, simple_secdist):
    approvals_app = app_stq.TaxiApprovalsStqApplication()

    await approvals_app.startup()
    yield approvals_app
    await approvals_app.shutdown()


@pytest.fixture(name='stq_put_mock')
def _stq_put_mock(patch):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        put_kwargs = kwargs['kwargs']
        assert put_kwargs.pop('log_extra')
        assert put_kwargs == {
            'login': 'test_login',
            'time': datetime.datetime(2017, 10, 31, 22, 10, 0),
            'ticket': 'TAXIRATE-35',
            'draft_id': 1,
            'api_path': 'test_api',
            'action': 'approval',
        }

    return _put


@pytest.fixture
async def _taxi_approvals_app(
        loop,
        db,
        pgsql,
        pgsql_local,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        patch,
        monkeypatch,
):
    class DummyStartrackClient:
        async def get_ticket(self, ticket, log_extra=None):
            forbidden = ['TAXIREL-1']
            if ticket in forbidden:
                raise startrack.PermissionsError(
                    f'Access to issues/{ticket} is forbidden',
                )
            existed = ['TAXIRATE-35', 'TAXIRATE-36', 'TAXIRATE-38']
            if ticket not in existed:
                raise startrack.NotFoundError
            return {
                'key': ticket,
                'createdBy': {'id': 'test_login'},
                'manager': {'id': 'test_manager'},
                'queue': {'key': 'TAXIRATE'},
                'status': {'key': 'open'},
            }

        async def create_ticket(
                self, summary, queue, description, *args, **kwargs,
        ):
            assert summary == 'test_summary'
            assert description == 'test_description'
            return {
                'key': f'{queue}-100',
                'createdBy': {'id': 'test_login'},
                'manager': {'id': 'test_manager'},
                'queue': {'key': 'TAXIRATE'},
                'status': {'key': 'open'},
            }

    approvals_db_dsn = pgsql_local['approvals'].get_dsn()
    simple_secdist['postgresql_settings'] = {
        'databases': {'approvals': [{'hosts': [approvals_db_dsn]}]},
    }
    simple_secdist['settings_override']['STARTRACK_API_TOKEN'] = 'TOKEN'

    @patch_aiohttp_session('http://unstable-host/check/route', 'post')
    def patch_admin(method, url, **kwargs):
        assert method == 'post'
        CHECK_DATA_RESPONSE['data'] = kwargs['json']
        return response_mock(json=CHECK_DATA_RESPONSE)

    test_app = run_web.create_app()
    test_services_schemes_path = os.path.join(
        os.path.dirname(test_taxi_approvals.__file__), 'services_schemes',
    )
    test_app.approvals_client = approvals.ApprovalsApiClient(
        test_app.session, test_app.tvm,
    )
    test_app.startrack_client = DummyStartrackClient()
    monkeypatch.setattr(
        test_app.ctx.services_schemes,
        '_services_schemes_path',
        test_services_schemes_path,
    )
    monkeypatch.setattr(
        test_app.ctx.services_schemes,
        '_platform_schemes_path',
        os.path.join(test_services_schemes_path, 'platform'),
    )
    monkeypatch.setattr(
        test_app.ctx.services_schemes,
        '_bank_schemes_path',
        os.path.join(test_services_schemes_path, 'bank'),
    )
    monkeypatch.setattr(
        test_app.ctx.services_schemes,
        '_wfm_effrat_schemes_path',
        os.path.join(test_services_schemes_path, 'wfm_effrat'),
    )
    return test_app


@pytest.fixture
async def approvals_cron_app(
        patch,
        patch_aiohttp_session,
        pgsql,
        pgsql_local,
        simple_secdist,
        response_mock,
        loop,
        monkeypatch,
):
    @patch_aiohttp_session('http://unstable-host')
    def patch_admin(method, url, **kwargs):
        return response_mock(json={'status': 'succeeded'})

    approvals_db_dsn = pgsql_local['approvals'].get_dsn()
    simple_secdist['postgresql_settings'] = {
        'databases': {'approvals': [{'hosts': [approvals_db_dsn]}]},
    }
    simple_secdist['settings_override']['STARTRACK_API_TOKEN'] = 'TOKEN'

    test_app = cron_run.TaxiApprovalsCronApplication()
    test_services_schemes_path = os.path.join(
        os.path.dirname(test_taxi_approvals.__file__), 'services_schemes',
    )
    monkeypatch.setattr(
        test_app.ctx.services_schemes,
        '_services_schemes_path',
        test_services_schemes_path,
    )
    monkeypatch.setattr(
        test_app.ctx.services_schemes,
        '_platform_schemes_path',
        os.path.join(test_services_schemes_path, 'platform'),
    )

    @patch('taxi_approvals.cron_run.create_app')
    async def create_app():
        yield test_app
        return

    for method in test_app.on_startup:
        await method(test_app)
    yield test_app
    for method in test_app.on_shutdown:
        await method(test_app)


@pytest.fixture
def taxi_approvals_client(aiohttp_client, _taxi_approvals_app, loop):
    return loop.run_until_complete(aiohttp_client(_taxi_approvals_app))


@pytest.fixture
def stq_put_mock(patch):
    def wrapper(
            *,
            draft_id,
            expected_found_logins,
            expected_tickets,
            api_path='test_api',
            service_name='test_service',
            tplatform_namespace=None,
    ):
        @patch('taxi.stq.client.put')
        async def _put(*args, **kwargs):
            put_kwargs = kwargs['kwargs']
            found_logins = list(sorted(put_kwargs.pop('found_logins')))
            assert put_kwargs.pop('log_extra')
            assert found_logins == expected_found_logins
            assert put_kwargs == {
                'draft_id': draft_id,
                'draft_tickets': expected_tickets,
                'api_path': api_path,
                'service_name': service_name,
                'tplatform_namespace': tplatform_namespace,
            }

        return _put

    return wrapper


@pytest.fixture
def check_route_mock(patch_aiohttp_session, response_mock):
    def wrapper(
            *,
            change_doc_id,
            lock_ids,
            route_method,
            route_headers,
            route_params,
            tickets=None,
            summon_users=None,
            mode=None,
            data=None,
            description=None,
            tplatform_namespace=None,
    ):
        @patch_aiohttp_session(
            'http://unstable-host/check/route', route_method,
        )
        def patch_admin(method, url, **kwargs):
            if route_headers:
                headers = kwargs.get('headers')
                for key in route_headers.keys():
                    assert headers[key] == route_headers[key]
            if route_params:
                params = kwargs.get('params')
                for key in route_params.keys():
                    assert params[key] == route_params[key]
            assert method.lower() == route_method.lower()
            response_json = {
                'data': kwargs['json'] if data is None else data,
                'change_doc_id': change_doc_id,
                'diff': {'new': {}, 'current': {}},
            }
            if lock_ids is not None:
                response_json['lock_ids'] = lock_ids
            if tickets is not None:
                response_json['tickets'] = tickets
            if summon_users is not None:
                response_json['summon_users'] = summon_users
            if mode is not None:
                response_json['mode'] = mode
            if description is not None:
                response_json['description'] = description
            if tplatform_namespace is not None:
                response_json['tplatform_namespace'] = tplatform_namespace
            return response_mock(json=response_json)

        return patch_admin

    return wrapper


@pytest.fixture
def check_route_err_mock(patch_aiohttp_session, response_mock):
    def wrapper(*, err_status, err_msg, err_json):
        @patch_aiohttp_session('http://unstable-host/check/route', 'post')
        def patch_admin(method, url, **kwargs):
            return response_mock(
                text=err_msg, status=err_status, json=err_json,
            )

        return patch_admin

    return wrapper


@pytest.fixture
def create_reports_mock(mockserver):
    def wrapper(
            draft_id,
            summary,
            test_service,
            test_api,
            tickets,
            login='test_login',
            tplatform_namespace=None,
    ):
        tickets_set = set(tickets or [])

        @mockserver.json_handler('/startrack_reports/v2/create_comments/')
        async def patch_reports_comments(request):
            data = request.json
            assert request.headers.get('Accept-Language') == 'ru'
            data_tickets = data.pop('tickets')
            keys, summonees = [], []
            for ticket in data_tickets:
                keys.append(ticket['key'])
                summonees.extend(ticket['summonees'])
            assert all(key in tickets_set for key in keys)
            assert all(
                summonee in ['test_login', 'test_manager']
                for summonee in summonees
            )
            host = 'https://tariff-editor.taxi.yandex-team.ru'
            if tplatform_namespace == 'market':
                host = 'https://market.tplatform.yandex-team.ru'
            url = f'/test_service/test_api/{draft_id}'
            if test_api != 'test_api':
                url = f'/test_service/draft/{draft_id}'
            assert data == {
                'action': f'{test_service}:{test_api}',
                'data': summary,
                'audit_action_id': '',
                'template_kwargs': {
                    'draft_id': draft_id,
                    'url': f'{host}{url}',
                    'login': login,
                    'time': '2017-11-01T01:10:00Z',
                },
            }

    return wrapper


@pytest.fixture(name='config_service_overrides', scope='session')
def _config_service_overrides():
    return {
        'APPROVALS_FEATURES': {'__default__': {'use_entity_urls': True}},
        'APPROVALS_FREEZE_SETTINGS': {
            'enabled': False,
            'allowed_draft_ids': [],
        },
        'APPROVALS_ENTITY_URLS': {
            'namespaces_hosts': {
                '__default__': 'https://tariff-editor.taxi.yandex-team.ru/',
                'market': 'https://market.tplatform.yandex-team.ru/',
            },
            'urls': {
                '__default__': 'drafts/draft/{draft_id}',
                'test_service': {
                    '__default__': 'test_service/draft/{draft_id}',
                    'test_api': 'test_service/test_api/{draft_id}',
                },
            },
        },
    }


@pytest.fixture(name='config_service_defaults', scope='session')
def _config_service_defaults(
        config_service_defaults, config_service_overrides,
):
    defaults = {**config_service_defaults}
    defaults.update(config_service_overrides)
    return defaults
