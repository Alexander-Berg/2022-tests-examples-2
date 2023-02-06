import pytest


@pytest.fixture(name='geotracks')
def geotracks(mockserver):
    class Context:
        def __init__(self):
            self.calls = 0
            self.gps_storage_get_response = {}

        def set_response(self, response):
            self.gps_storage_get_response = response

    context = Context()

    @mockserver.json_handler('/driver-trackstory/legacy/gps-storage/get')
    async def _gps_storage_get(request):
        context.calls += 1
        return context.gps_storage_get_response

    return context
