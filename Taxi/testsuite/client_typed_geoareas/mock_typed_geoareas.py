import pytest


@pytest.fixture
def mock_typed_geoareas(mockserver, geoareas, load_json):
    @mockserver.json_handler('/geoareas/typed-geoareas/v1/fetch_geoareas')
    def mock_typed_geoareas_list(request):
        params = request.args
        if 'updated_after' in params:
            return {'geoareas': [], 'removed': []}
        return {
            'geoareas': geoareas.get_list(collection_name='typed_geoareas'),
            'removed': [],
        }

    return mock_typed_geoareas_list
