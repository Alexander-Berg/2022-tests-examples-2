# pylint: disable=redefined-outer-name,invalid-name
import pytest

from taxi import secdist
from taxi.billing.clients import billing_buffer_proxy
from taxi.pytest_plugins import service

from taxi_billing_buffer_proxy import app
from taxi_billing_buffer_proxy import stq_setup

pytest_plugins = ['taxi.pytest_plugins.stq_agent']

service.install_service_local_fixtures(__name__)

TVM_TICKET = 'good_ticket'


@pytest.fixture
def request_headers():
    return {'X-Ya-Service-Ticket': TVM_TICKET}


@pytest.fixture
def taxi_billing_buffer_proxy_secdist(monkeypatch, mongo_settings):
    def load_secdist():
        return {'billing_buffer_proxy': {}, 'mongo_settings': mongo_settings}

    def load_secdist_ro():
        return {'billing_buffer_proxy': {}, 'mongo_settings': mongo_settings}

    monkeypatch.setattr(secdist, 'load_secdist', load_secdist)
    monkeypatch.setattr(secdist, 'load_secdist_ro', load_secdist_ro)


@pytest.fixture
def taxi_billing_buffer_proxy_app(taxi_billing_buffer_proxy_secdist):
    return app.create_app()


@pytest.fixture
def taxi_billing_buffer_proxy_client(
        aiohttp_client, taxi_billing_buffer_proxy_app, loop,
):
    return loop.run_until_complete(
        aiohttp_client(taxi_billing_buffer_proxy_app),
    )


@pytest.fixture
async def taxi_billing_buffer_proxy_stq_context(loop, simple_secdist):
    context = stq_setup.setup(loop=loop)
    async for c in context:
        yield c


@pytest.fixture
async def api_client(taxi_billing_buffer_proxy_stq_context):
    return billing_buffer_proxy.BillingBufferProxyApiClient(
        session=taxi_billing_buffer_proxy_stq_context.session,
        config=taxi_billing_buffer_proxy_stq_context.config,
        tvm_client=taxi_billing_buffer_proxy_stq_context.tvm_client,
    )
