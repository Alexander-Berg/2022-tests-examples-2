import dataclasses

import pytest

import testsuite._internal.fixture_types as fixture_types

import tests_invoices_archive.mocks.common as common

SERVICE_NAME = 'order-archive'


@pytest.fixture(name='mock_find_order_ids_by_uid')
def _mock_find_order_ids_by_uid(mockserver: fixture_types.MockserverFixture):
    def mock(response: common.MockedHandlerContext.TResponse = None):
        @mockserver.json_handler(
            SERVICE_NAME + '/v1/order_proc/takeout/find_order_ids_by_uid',
        )
        async def handler(request):
            response_func = context.response_func
            response_json = (
                response_func(request)
                if callable(response_func)
                else {'order_infos': []}
            )
            return mockserver.make_response(json=response_json)

        context = common.MockedHandlerContext(handler, response)
        return context

    return mock


@dataclasses.dataclass
class MockedServiceContext:
    find_order_ids_by_uid: common.MockedHandlerContext


@pytest.fixture(name='mock_order_archive_service')
def _mock_order_archive_service(mock_find_order_ids_by_uid):
    return MockedServiceContext(
        find_order_ids_by_uid=mock_find_order_ids_by_uid(),
    )
