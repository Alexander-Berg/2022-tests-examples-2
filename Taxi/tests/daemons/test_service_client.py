# pylint: disable=protected-access
import pytest

from taxi_tests.daemons import service_client
from taxi_tests.utils import tracing


@pytest.fixture
def client_tests_control(
        mockserver, service_client_options, trace_id, mocked_time,
):
    return service_client.ClientTestsControl(
        mockserver.base_url,
        service_headers={tracing.TRACE_ID_HEADER: trace_id},
        **service_client_options,
        mocked_time=mocked_time,
    )


@pytest.mark.parametrize(
    'url,expected',
    [
        ('http://localhost:9999/', 'http://localhost:9999/'),
        ('http://localhost:9999', 'http://localhost:9999/'),
    ],
)
def test_normalize_base_url(url, expected):
    assert service_client._normalize_base_url(url) == expected


@pytest.mark.parametrize(
    'base,path,expected',
    [
        ('http://localhost:9999/', 'foo', 'http://localhost:9999/foo'),
        ('http://localhost:9999/', '/foo', 'http://localhost:9999/foo'),
        ('http://localhost:9999/', '//foo', 'http://localhost:9999//foo'),
    ],
)
def test_url_join(base, path, expected):
    assert service_client._url_join(base, path) == expected


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
