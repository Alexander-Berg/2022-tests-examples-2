import pytest

USERVER_LOCATION_FILE = 'userver/core/src/server/http/http_request_parser.cpp'
USERVER_LOGGED_TEXT = 'headers complete'

SERVICE_LOCATION = (
    'services/test-service/src/views/response-with-headers-without-body/'
    'get/view.cpp:12'
)
SERVICE_LOGGED_TEXT = 'Got something for dynamic debug logging'


@pytest.fixture(name='taxi_bodyless_headers_mock')
def _taxi_bodyless_headers_mock(mockserver):
    @mockserver.json_handler(
        '/test-service/response-with-headers-without-body',
    )
    async def _handler(request):
        return mockserver.make_response(headers={'something': 'nothing'})


async def test_service_debug_logs_off(
        taxi_test_service, taxi_bodyless_headers_mock,
):
    async with taxi_test_service.capture_logs() as capture:
        response = await taxi_test_service.get(
            '/response-with-headers-without-body',
        )
        assert response.status_code == 200

    assert not capture.select(text=SERVICE_LOGGED_TEXT)


async def test_service_debug_logs_on(
        taxi_test_service,
        taxi_test_service_monitor,
        taxi_bodyless_headers_mock,
):
    resp = await taxi_test_service_monitor.put(
        '/log/dynamic-debug', params={'location': SERVICE_LOCATION},
    )
    assert resp.status_code == 200

    async with taxi_test_service.capture_logs() as capture:
        response = await taxi_test_service.get(
            '/response-with-headers-without-body',
        )
        assert response.status_code == 200

    assert capture.select(text=SERVICE_LOGGED_TEXT)


async def test_service_debug_logs_on_off(
        taxi_test_service,
        taxi_test_service_monitor,
        taxi_bodyless_headers_mock,
):
    resp = await taxi_test_service_monitor.put(
        '/log/dynamic-debug', params={'location': SERVICE_LOCATION},
    )
    assert resp.status_code == 200
    resp = await taxi_test_service_monitor.delete(
        '/log/dynamic-debug', params={'location': SERVICE_LOCATION},
    )
    assert resp.status_code == 200

    async with taxi_test_service.capture_logs() as capture:
        response = await taxi_test_service.get(
            '/response-with-headers-without-body',
        )
        assert response.status_code == 200

    assert not capture.select(text=SERVICE_LOGGED_TEXT)


async def test_userver_debug_logs_file_off(
        taxi_test_service, taxi_bodyless_headers_mock,
):
    async with taxi_test_service.capture_logs() as capture:
        response = await taxi_test_service.get(
            '/response-with-headers-without-body',
        )
        assert response.status_code == 200

    assert not capture.select(text=USERVER_LOGGED_TEXT)


async def test_userver_debug_logs_file(
        taxi_test_service,
        taxi_test_service_monitor,
        taxi_bodyless_headers_mock,
):
    resp = await taxi_test_service_monitor.put(
        '/log/dynamic-debug', params={'location': USERVER_LOCATION_FILE},
    )
    assert resp.status_code == 200

    async with taxi_test_service.capture_logs() as capture:
        response = await taxi_test_service.get(
            '/response-with-headers-without-body',
        )
        assert response.status_code == 200

    assert capture.select(text=USERVER_LOGGED_TEXT)
