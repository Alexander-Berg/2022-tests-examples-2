# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=wrong-import-order

from pricing_data_preparer_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(autouse=True)
def territories_countries_list(mockserver, load_json):
    @mockserver.json_handler('/territories/v1/countries/list')
    def mock_countries_list(request):
        request.get_data()
        return load_json('countries.json')

    return mock_countries_list
