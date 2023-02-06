"""
Mock for territories.
"""

import pytest


@pytest.fixture
def mock_territories(mockserver, load_json):
    @mockserver.json_handler('/territories/v1/countries/list')
    def mock_countries_list(request):
        request.get_data()
        # todo - uncomment when tvm2_client mock is OK
        # assert request.headers.get('X-Ya-Service-Ticket') is not None
        return load_json('countries.json')

    return mock_countries_list
