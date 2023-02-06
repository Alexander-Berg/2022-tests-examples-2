import pytest

DEFAULT_HEADERS = {'X-YaTaxi-UserId': '0'}


@pytest.mark.parametrize(
    'position, available', [([40, 40], True), ([40.5, 40], False)],
)
@pytest.mark.config(MASSTRANSIT_AVAILABILITY_SPAN=[0.005, 0.005])
@pytest.mark.stops_file(filename='stops.json')
async def test_availability(
        taxi_masstransit, mockserver, load_binary, position, available,
):
    @mockserver.json_handler('/mtinfo/v2/stop')
    def _mock_mtinfo(request):
        return mockserver.make_response(
            load_binary('mtinfo_response.bin'),
            content_type='application/x-protobuf',
        )

    request = {'position': position}
    response = await taxi_masstransit.post(
        '/masstransit/v1/availability', request, headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['available'] == available
