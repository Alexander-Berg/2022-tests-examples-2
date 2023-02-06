# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from communications_audience_plugins import *  # noqa: F403 F401


@pytest.fixture
def mock_promotions(mockserver):
    def _init(status_code=200):
        @mockserver.json_handler('/promotions/admin/promotions/publish/')
        def publish_handler(request):
            return mockserver.make_response(status=status_code)

        return publish_handler

    return _init


@pytest.fixture
def mock_promotions_unpublish(mockserver):
    def _init(status_code=200):
        @mockserver.json_handler('/promotions/admin/promotions/unpublish/')
        def unpublish_handler(request):
            if status_code == 200:
                return mockserver.make_response(status=status_code)
            # /publish and /unpublish return error reponses
            # with the same schema for all defined error codes
            error_response = {
                'code': str(status_code),
                'message': 'something bad happened',
            }
            return mockserver.make_response(
                status=status_code, json=error_response,
            )

        return unpublish_handler

    return _init


@pytest.fixture
def mock_userapi(mockserver):
    def _init(is_staff=False):
        @mockserver.json_handler('/user-api/v2/user_phones/get')
        def search_handler(request):
            return mockserver.make_response(
                status=200, json={'id': 'not used', 'yandex_staff': is_staff},
            )

        return search_handler

    return _init
