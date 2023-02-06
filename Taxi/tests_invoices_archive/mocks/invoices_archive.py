import dataclasses

import bson
import pytest

import testsuite._internal.fixture_types as fixture_types
import testsuite.utils.http as utils_http

import tests_invoices_archive.mocks.common as common

SERVICE_NAME = 'invoices-archive'


@pytest.fixture(name='mock_invoices_archive_get_order')
def _mock_invoices_archive_get_order(
        mockserver: fixture_types.MockserverFixture,
):
    def mock():
        @mockserver.handler(SERVICE_NAME + '/v1/orders/get-order')
        async def handler(request: utils_http.Request):
            resp = context.get_response(request)
            status = context.status or 200
            if status == 200:
                data = bson.BSON.encode({'doc': resp})
                return mockserver.make_response(
                    response=data, content_type='application/bson',
                )
            return mockserver.make_response(
                json=resp, status=status, content_type='application/json',
            )

        context = common.MockedHandlerContext(handler)
        return context

    return mock


@dataclasses.dataclass
class MockedServiceContext:
    invoices_archive_get_order: common.MockedHandlerContext


@pytest.fixture(name='mock_invoices_archive_service')
def _mock_invoices_archive_service(mock_invoices_archive_get_order):
    return MockedServiceContext(
        invoices_archive_get_order=mock_invoices_archive_get_order(),
    )
