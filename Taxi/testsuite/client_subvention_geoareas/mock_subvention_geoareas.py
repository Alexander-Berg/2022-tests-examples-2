import pytest


@pytest.fixture
def mock_subvention_geoareas(mockserver, geoareas, load_json):
    @mockserver.json_handler('/geoareas/subvention-geoareas/v1/geoareas')
    def mock_subvention_geoareas_list(request):
        params = request.args
        if 'updated_after' in params:
            return {'geoareas': [], 'removed_names': []}
        return {
            'geoareas': geoareas.get_list(
                collection_name='subvention_geoareas',
            ),
            'removed_names': [],
        }

    return mock_subvention_geoareas_list
