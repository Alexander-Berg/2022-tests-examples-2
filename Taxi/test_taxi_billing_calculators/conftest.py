# pylint: disable=redefined-outer-name
import pytest

from taxi.pytest_plugins import service

from taxi_billing_calculators import app
from taxi_billing_calculators import config
from taxi_billing_calculators.stq.driver_mode_subscription import (
    context as stq_driver_mode_subscription_context,
)
from taxi_billing_calculators.stq.main import context as stq_main_context
from taxi_billing_calculators.stq.manual_transactions import (
    context as stq_manual_transactions_context,
)
from taxi_billing_calculators.stq.taximeter import (
    context as stq_taximeter_context,
)
from taxi_billing_calculators.stq.tlog import context as stq_tlog_context


pytest_plugins = ['taxi.pytest_plugins.stq_agent']

TVM_TICKET = 'good_ticket'


@pytest.fixture
def simple_secdist(simple_secdist):
    config = {
        'token': 'some_yt_token',
        'prefix': '//testsuite/',
        'proxy': {
            'url': 'hahn',
            'content_encoding': 'identity',
            'retries': {'enable': False},
        },
        'api_version': 'v3',
    }
    simple_secdist['settings_override'].update(
        {
            'BILLING_MANUAL_TRANSACTIONS_MDS_S3': {
                'url': 'test_url',
                'bucket': 'attachments',
                'access_key_id': 'test_key_id',
                'secret_key': 'test_key',
            },
            'YT_CONFIG': {'hahn': config},
        },
    )
    return simple_secdist


@pytest.fixture
def request_headers():
    return {'X-Ya-Service-Ticket': TVM_TICKET}


@pytest.fixture
def patched_tvm_ticket_check(patch):
    return _patch_tvm_ticket_check(patch, 'billing_calculators')


def _patch_tvm_ticket_check(patch, src_service_name):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        if ticket_body == b'good_ticket':
            return src_service_name
        return None

    return get_service_name


@pytest.fixture
def patched_tvm_get_headers(patch):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {'X-Ya-Service-Ticket': TVM_TICKET}


@pytest.fixture
# pylint: disable=invalid-name
def taxi_billing_calculators_app(simple_secdist):
    simple_secdist['billing_calculators'] = {}
    return app.create_app()


@pytest.fixture
def taxi_billing_calculators_client(
        aiohttp_client, taxi_billing_calculators_app, loop,
):
    return loop.run_until_complete(
        aiohttp_client(taxi_billing_calculators_app),
    )


@pytest.fixture
# pylint: disable=invalid-name
async def taxi_billing_calculators_stq_main_ctx(
        test_taxi_app, loop, simple_secdist,
):
    ctx = stq_main_context.Context()
    await ctx.startup()
    yield ctx
    await ctx.cleanup()


@pytest.fixture
# pylint: disable=invalid-name
async def taxi_billing_calculators_stq_manual_transactions_ctx(
        test_taxi_app, loop, simple_secdist,
):
    ctx = stq_manual_transactions_context.Context()
    await ctx.startup()
    yield ctx
    await ctx.cleanup()


@pytest.fixture
# pylint: disable=invalid-name
async def taxi_billing_calculators_stq_payment_requests_ctx(
        test_taxi_app, loop, simple_secdist,
):
    ctx = stq_main_context.Context()
    await ctx.startup()
    yield ctx
    await ctx.cleanup()


@pytest.fixture
# pylint: disable=invalid-name
async def taxi_billing_calculators_stq_taximeter_ctx(
        test_taxi_app, loop, simple_secdist,
):
    ctx = stq_taximeter_context.Context()
    await ctx.startup()
    yield ctx
    await ctx.cleanup()


@pytest.fixture
# pylint: disable=invalid-name
async def taxi_billing_calculators_stq_driver_mode_subscription_ctx(
        test_taxi_app, loop, simple_secdist,
):
    ctx = stq_driver_mode_subscription_context.Context()
    await ctx.startup()
    yield ctx
    await ctx.cleanup()


@pytest.fixture
# pylint: disable=invalid-name
async def taxi_billing_calculators_stq_tlog_ctx(
        test_taxi_app, loop, simple_secdist,
):
    ctx = stq_tlog_context.Context()
    await ctx.startup()
    yield ctx
    await ctx.cleanup()


@pytest.fixture
def stq_client_patched(patch):
    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def stq_client_put(
            queue, eta=None, task_id=None, args=None, kwargs=None,
    ):
        return

    return stq_client_put


service.install_service_local_fixtures(__name__)


@pytest.fixture(autouse=True)
def _patch_billing_old_journal_limit_days(monkeypatch):
    monkeypatch.setattr(config.Config, 'BILLING_OLD_JOURNAL_LIMIT_DAYS', 3650)
