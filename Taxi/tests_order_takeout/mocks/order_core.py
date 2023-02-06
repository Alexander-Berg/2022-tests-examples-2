import dataclasses

import bson
import pytest

import testsuite._internal.fixture_types as fixture_types
import testsuite.utils.http as utils_http

import tests_order_takeout.mocks.common as common

SERVICE_NAME = 'order-core'


@pytest.fixture(name='mock_order_proc_set_fields')
def _mock_order_proc_set_fields(mockserver: fixture_types.MockserverFixture):
    def mock():
        @mockserver.handler(
            SERVICE_NAME + '/internal/takeout/v1/order-proc/set-fields',
        )
        async def handler(request: utils_http.Request):
            resp = context.get_response() or {}
            data = bson.BSON.encode(resp)
            status = context.status or 200
            return mockserver.make_response(
                response=data, status=status, content_type='application/bson',
            )

        context = common.MockedHandlerContext(handler)
        return context

    return mock


@pytest.fixture(name='mock_order_proc_get_order')
def _mock_order_proc_get_order(mockserver: fixture_types.MockserverFixture):
    def mock():
        @mockserver.handler(
            SERVICE_NAME + '/internal/processing/v1/order-proc/get-order',
        )
        async def handler():
            resp = context.get_response()
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
    order_proc_set_fields: common.MockedHandlerContext
    order_proc_get_order: common.MockedHandlerContext


@pytest.fixture(name='mock_order_core_service')
def _mock_order_core_service(
        mock_order_proc_set_fields, mock_order_proc_get_order,
):
    return MockedServiceContext(
        order_proc_set_fields=mock_order_proc_set_fields(),
        order_proc_get_order=mock_order_proc_get_order(),
    )
