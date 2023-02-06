import pytest


@pytest.fixture
def defer_wait_for_async_write(testpoint, request):
    @testpoint('geohistory::user::AsyncWriteToRedisImpl')
    def cache_update(data):
        pass
    request.addfinalizer(cache_update.wait_call)
