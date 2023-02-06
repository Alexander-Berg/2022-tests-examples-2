# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest


@pytest.fixture
def mocker_order_complete(mockserver):
    def wrapper(json: dict, status: int = 200):
        @mockserver.json_handler(
            '/cargo-claims/v1/claims/mark/taxi-order-complete',
        )
        def mark_order_complete(request):
            result = {} if json is None else json
            return mockserver.make_response(json=result, status=status)

        return mark_order_complete

    return wrapper
