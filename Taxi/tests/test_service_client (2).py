# pylint: disable=protected-access,redefined-outer-name
import pytest

from taxi.pytest_plugins.blacksuite import service_client


@pytest.fixture
def client_tests_control(
        mockserver,
        service_client_default_headers,
        service_client_options,
        mocked_time,
):
    return service_client.AiohttpClientTestsControl(
        mockserver.base_url,
        mocked_time=mocked_time,
        headers={
            **service_client_default_headers,
            mockserver.trace_id_header: mockserver.trace_id,
        },
        **service_client_options,
    )


@pytest.mark.now('2017-03-13T11:30:40.123456+0300')
async def test_test_control(client_tests_control, mockserver):
    @mockserver.json_handler('/tests/control')
    def tests_control_handler(request):
        assert request.json == {
            'cache_clean_update': True,
            'invalidate_caches': True,
            'now': '2017-03-13T08:30:40.123456+0000',
        }
        return {}

    await client_tests_control.invalidate_caches()
    assert tests_control_handler.times_called == 1


@pytest.mark.now(enabled=False)
async def test_when_mock_time_is_disabled_now_is_not_sent(
        client_tests_control, mockserver,
):
    @mockserver.json_handler('/tests/control')
    def tests_control_handler(request):
        assert request.json == {
            'cache_clean_update': True,
            'invalidate_caches': True,
        }
        return {}

    await client_tests_control.invalidate_caches()
    assert tests_control_handler.times_called == 1
