# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from fts_emulator_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
def handlers_service(mockserver):
    @mockserver.json_handler('/yagr/pipeline/test/position/store')
    def _yagr_handler(request):
        print(request)
        return mockserver.make_response('OK', status=200)

    @mockserver.json_handler('/maps-router/v2/route')
    def _router_handler(request):
        return mockserver.make_response(
            response='Ffuuu',
            status=500,
            content_type='application/x-protobuf',
        )
