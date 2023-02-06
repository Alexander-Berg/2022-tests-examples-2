# pylint: disable=unused-variable
# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import os

import pytest

from taxi import discovery
from taxi.clients import audit
from taxi.clients import experiments3
from taxi.clients import idm

import taxi_api_admin.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from taxi_api_admin import cron_run  # noqa: I100
from taxi_api_admin.generated.web import run_web
import test_taxi_api_admin

pytest_plugins = [
    'taxi_api_admin.generated.service.pytest_plugins',
    'taxi.pytest_plugins.experiments3',
]

ACTION_IDS = [
    {'action_id': 'send_sms', 'title': 'title'},
    {'action_id': 'test_action_id', 'title': 'title'},
]
PERMISSIONS_TREE = {
    'categories': [
        {
            'id': 'send_sms_category_id',
            'name': 'СМС',
            'permissions': [
                {
                    'action': 'просмотр',
                    'comment': None,
                    'sections': ['Информация отсутствует'],
                    'id': 'send_sms',
                },
            ],
        },
        {
            'id': 'test_category_id',
            'name': 'Тест',
            'permissions': [
                {
                    'action': 'просмотр',
                    'comment': None,
                    'sections': ['Информация отсутствует'],
                    'id': 'test_perm',
                },
            ],
        },
    ],
}


class FakeTVMClient:
    _calls_count = 0

    async def get_auth_headers(self, dst_service_name, log_extra=None):
        self._calls_count += 1
        return {'X-Ya-Service-Ticket': '123'}

    def calls(self):
        count = self._calls_count
        self._calls_count = 0
        return count


class FakeStartrackAPIClient:
    async def get_ticket(self, ticket, log_extra=None):
        return None

    async def create_ticket(
            self, summary, queue, description, *args, **kwargs,
    ):
        return {'key': f'{queue}-100'}

    async def create_comment(self, ticket, **kwargs):
        return {'id': 'comment_id'}

    async def execute_transition(self, *args, **kwargs):
        return {}


@pytest.fixture(name='services_schemes_path')
def _services_schemes_path():
    return os.path.join(
        os.path.dirname(test_taxi_api_admin.__file__),
        'static',
        'services_schemes',
    )


@pytest.fixture(name='actions_path')
def _actions_path():
    return None


@pytest.fixture(name='sections_path')
def _sections_path():
    return None


@pytest.fixture(name='categories_path')
def _categories_path():
    return None


@pytest.fixture(name='patch_ymsh_admin')
def _patch_ymsh_admin(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(
        'https://ymsh-admin-unstable.tst.mobile.yandex-team.ru',
    )
    def _patch_admin(method, url, **kwargs):
        if 'audit/actions/list/' in url:
            return response_mock(text=str(ACTION_IDS), json=ACTION_IDS)
        return response_mock(text=str(PERMISSIONS_TREE), json=PERMISSIONS_TREE)

    return _patch_admin


@pytest.fixture(name='disable_schemes_checker')
def _disable_schemes_checker(monkeypatch):
    async def _mock_func(*args):
        return None

    monkeypatch.setattr(
        'taxi_api_admin.components.services_schemes.'
        'scheme_checker.check_all_schemes',
        _mock_func,
    )


@pytest.fixture
def taxi_api_admin_app(
        monkeypatch,
        simple_secdist,
        services_schemes_path,
        actions_path,
        sections_path,
        categories_path,
        patch_ymsh_admin,
):
    simple_secdist['settings_override']['STARTRACK_API_TOKEN'] = 'TOKEN'
    test_app = run_web.create_app()
    test_app.secdist['settings_override']['API_ADMIN_SERVICES_TOKENS'] = {
        'error_service': '123',
        'sms': '123',
        'service_with_object_id': '123',
        'service_with_ticket': '123',
        'service_with_dynamic_permission': '456',
        'service_with_exclude_audit': '123',
        'service_with_experiments_filters': '123',
        'service_without_unstable': '123',
        'service_with_unstable': '123',
    }
    test_app.settings.BLACKBOX_AUTH = False

    monkeypatch.setattr(
        test_app.ctx.services_schemes,
        '_services_schemes_path',
        services_schemes_path,
    )
    if actions_path:
        monkeypatch.setattr(
            test_app.ctx.services_schemes, '_actions_path', actions_path,
        )
    if sections_path:
        monkeypatch.setattr(
            test_app.ctx.services_schemes, '_sections_path', sections_path,
        )
    if categories_path:
        monkeypatch.setattr(
            test_app.ctx.services_schemes, '_categories_path', categories_path,
        )

    test_app.tvm = FakeTVMClient()
    test_app.startrack_client = FakeStartrackAPIClient()
    test_app.experiments_client = experiments3.Experiments3Client(
        secdist=test_app.secdist,
        config=test_app.config,
        session=test_app.session,
        tvm_client=None,
    )
    test_app.audit_client = audit.AuditClient(
        session=test_app.session,
        service=discovery.find_service('audit'),
        use_service=True,
        db=test_app.db,
    )
    test_app.idm_client = idm.IdmApiClient(
        session=test_app.session, tvm=test_app.tvm, config=test_app.config,
    )
    return test_app


@pytest.fixture
def taxi_api_admin_client(loop, aiohttp_client, taxi_api_admin_app):
    return loop.run_until_complete(aiohttp_client(taxi_api_admin_app))


@pytest.fixture
async def api_admin_cron_app(loop, patch, simple_secdist, monkeypatch):
    simple_secdist['settings_override']['STARTRACK_API_TOKEN'] = 'TOKEN'
    test_app = cron_run.TaxiApiAdminCronApplication()

    for method in test_app.on_startup:
        await method(test_app)
    yield test_app
    for method in test_app.on_shutdown:
        await method(test_app)


@pytest.fixture(name='patch_audit_log', autouse=True)
def _patch_audit_log(patch_aiohttp_session, response_mock):
    class MockRequest:
        @staticmethod
        @patch_aiohttp_session(discovery.find_service('audit').url, 'POST')
        def _mock_audit_log(*args, **kwargs):
            return response_mock(json={'id': 'new_id'})

        def only_one_request(self):
            calls = self._mock_audit_log.calls
            assert len(calls) <= 1
            return calls[0]['kwargs']['json'] if calls else None

    return MockRequest()
