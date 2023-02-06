# pylint: disable=redefined-outer-name
import os.path

import pytest

from taxi.pytest_plugins import service

from taxi_billing_orders import app
from taxi_billing_orders.stq.internal import (
    context_data as stq_internal_context,
)

pytest_plugins = ['taxi.pytest_plugins.stq_agent']

TVM_TICKET = 'good_ticket'


def get_request_headers():
    return {'X-Ya-Service-Ticket': TVM_TICKET}


@pytest.fixture
def request_headers():
    return get_request_headers()


@pytest.fixture
def patched_tvm_ticket_check(patch):
    return _patch_tvm_ticket_check(patch, 'billing_orders')


def _patch_tvm_ticket_check(patch, src_service_name):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        if ticket_body == b'good_ticket':
            return src_service_name
        return None

    return get_service_name


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'BILLING_MANUAL_TRANSACTIONS_MDS_S3': {
                'url': 'test_url',
                'bucket': 'test_bucket',
                'access_key_id': 'test_access_key_id',
                'secret_key': 'test_secret_key',
            },
        },
    )
    return simple_secdist


@pytest.fixture(name='taxi_billing_orders_app')
def taxi_billing_orders_app_fixture(simple_secdist):
    result = app.init_billing_orders_app(app_id=1)
    return result


@pytest.fixture
def taxi_billing_orders_client(aiohttp_client, taxi_billing_orders_app, loop):
    return loop.run_until_complete(aiohttp_client(taxi_billing_orders_app))


@pytest.fixture
def load_json(load_json):
    def _load_py_json(filename, *args, **kwargs):
        static_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'static',
        )
        return load_json(os.path.join(static_dir, filename), *args, **kwargs)

    return _load_py_json


@pytest.fixture
def load_py_json_dir(load_json):
    def _load_py_json_dir(dir_name, *input_data):
        if not input_data:
            raise RuntimeError('pass some fixture')
        elif len(input_data) == 1:
            return load_json(os.path.join(dir_name, input_data[0]))
        else:
            return [
                load_json(os.path.join(dir_name, a_data))
                for a_data in input_data
            ]

    return _load_py_json_dir


@pytest.fixture
# pylint: disable=invalid-name
async def taxi_billing_orders_stq_internal_ctx(
        test_taxi_app, loop, simple_secdist,
):
    ctx = stq_internal_context.ContextData()
    await ctx.startup()
    yield ctx
    await ctx.cleanup()


service.install_service_local_fixtures(__name__)
