import pytest


# in some positions/store routes data stores in cache
# and than after some delay it saves into mongo
# so tests must wait until their data will be stored in db
# cause in another case race conditions can happen and tests will be flaky
@pytest.fixture
def defer_wait_for_cache_update(testpoint, request):
    @testpoint('PositionsCache::UpdateShortTrackPositionsInternal')
    def cache_update(data):
        pass
    request.addfinalizer(cache_update.wait_call)
