# root conftest for service scooters-surge
import pytest


pytest_plugins = ['scooters_surge_plugins.pytest_plugins']


@pytest.fixture(autouse=True)
def mock_heatmap_storage(mockserver, load_json):
    @mockserver.json_handler('/heatmap-storage/v1/get_actual_map_metadata')
    def _mock_actual_map(request):
        return mockserver.make_response(
            json={
                'id': 1,
                'created': '2019-01-01T00:00:00Z',
                'expires': '2019-01-02T00:00:00Z',
                'heatmap_type': 'mapped_features',
            },
        )

    @mockserver.handler('/heatmap-storage/v1/get_map')
    def _mock_get_map(request):
        return mockserver.make_response(
            response=str(load_json('surge_map_zoned.json')).replace('\'', '"'),
            headers={
                'Created': '2019-01-01T00:00:00Z',
                'Expires': '2019-01-02T00:00:00Z',
                'X-YaTaxi-Heatmap-Type': 'mapped_features',
                'X-YaTaxi-Heatmap-Content-Key': 'scooters_surge_zoned/default',
                'Content-Type': 'application/x-flatbuffers',
            },
        )
