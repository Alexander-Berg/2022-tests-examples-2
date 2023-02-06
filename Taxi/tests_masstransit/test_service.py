# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from masstransit_plugins.generated_tests import *  # noqa


async def test_not_found(taxi_masstransit, mockserver, load_binary, load_json):

    # pylint: disable=unused-variable
    @mockserver.json_handler('/mtinfo/v2/stop')
    def mtinfo_v2_stop(request):
        return mockserver.make_response('Not found', status=404)

    # pylint: disable=unused-variable
    @mockserver.json_handler('/mtinfo/v2/line')
    def mtinfo_v2_line(request):
        return mockserver.make_response('Not found', status=404)

    response = await taxi_masstransit.get(
        '/4.0/masstransit/v1/lineinfo?line_id=1',
    )
    assert response.status_code == 404

    response = await taxi_masstransit.get(
        '/4.0/masstransit/v1/stopinfo?stop_id=1',
    )
    assert response.status_code == 404
