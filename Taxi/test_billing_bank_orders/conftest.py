# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import billing_bank_orders.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['billing_bank_orders.generated.service.pytest_plugins']

TVM_TICKET = 'good_ticket'


@pytest.fixture(autouse=True)
def ydb_fixture(patch):
    @patch(
        'billing_bank_orders.generated.service.ydb_client.plugin.BaseYdbDriver._init_driver',  # noqa: E501
    )
    async def init_driver(*args, **kwargs):
        pass

    return init_driver


@pytest.fixture
def request_headers():
    return {'X-Ya-Service-Ticket': TVM_TICKET}


@pytest.fixture
def patched_tvm_ticket_check(patch):
    return _patch_tvm_ticket_check(patch, 'billing-bank-orders')


def _patch_tvm_ticket_check(patch, src_service_name):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        if ticket_body == b'good_ticket':
            return src_service_name
        return None

    return get_service_name
