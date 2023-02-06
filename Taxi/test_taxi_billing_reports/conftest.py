# pylint: disable=redefined-outer-name
import os

import pytest

from taxi.pytest_plugins import service

from taxi_billing_reports import app

TVM_TICKET = 'good_ticket'


def get_request_headers():
    return {'X-Ya-Service-Ticket': TVM_TICKET}


@pytest.fixture
def request_headers():
    return get_request_headers()


@pytest.fixture
def patched_tvm_ticket_check(patch):
    return _patch_tvm_ticket_check(patch, 'billing-reports')


def _patch_tvm_ticket_check(patch, src_service_name):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        if ticket_body == b'good_ticket':
            return src_service_name
        return None

    return get_service_name


@pytest.fixture
def taxi_billing_reports_app(loop, db, simple_secdist):
    simple_secdist['billing_reports'] = {}
    return app.create_app(app_instance=1)


@pytest.fixture
async def taxi_billing_reports_context(loop, db, simple_secdist):
    simple_secdist['billing_reports'] = {}
    br_app = app.create_app(app_instance=1)
    init_iter = app.context_init(br_app)
    await init_iter.__anext__()
    yield br_app['context']
    async for _ in init_iter:
        pass


@pytest.fixture
def taxi_billing_reports_client(
        aiohttp_client, taxi_billing_reports_app, loop,
):
    return loop.run_until_complete(aiohttp_client(taxi_billing_reports_app))


@pytest.fixture
def load_py_json_dir(load_json):
    def _load_py_json(filename, *args, **kwargs):
        static_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'static',
        )
        return load_json(os.path.join(static_dir, filename), *args, **kwargs)

    def _load_py_json_dir(dir_name, *input_data):
        if not input_data:
            raise RuntimeError('pass some fixture')
        elif len(input_data) == 1:
            return _load_py_json(os.path.join(dir_name, input_data[0]))
        else:
            return [
                _load_py_json(os.path.join(dir_name, a_data))
                for a_data in input_data
            ]

    return _load_py_json_dir


service.install_service_local_fixtures(__name__)
