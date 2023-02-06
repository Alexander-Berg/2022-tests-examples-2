import urllib

import pytest


@pytest.fixture
def mock_geoareas(mockserver, geoareas, load_json):
    @mockserver.json_handler('/geoareas/geoareas/v1/tariff-areas')
    def mock_geoareas_list(request):
        params = urllib.parse.parse_qs(request.query_string.decode())
        if 'updated_after' in params:
            return {'geoareas': [], 'removed_names': []}
        return {'geoareas': geoareas.get_list(), 'removed_names': []}

    return mock_geoareas_list
