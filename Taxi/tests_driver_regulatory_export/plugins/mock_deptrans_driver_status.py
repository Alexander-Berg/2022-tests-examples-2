import pytest


@pytest.fixture(autouse=True)
def deptrans_driver_status(mockserver):
    @mockserver.json_handler(
        '/deptrans-driver-status/internal/v3/profiles/updates',
    )
    def _mock_profiles_updates(request):
        return {'cursor': 'something', 'data': []}
