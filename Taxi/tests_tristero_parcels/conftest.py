# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from tristero_parcels_plugins import *  # noqa: F403 F401

from tests_tristero_parcels import tristero_parcels_db


@pytest.fixture(name='tristero_parcels_db')
def mock_tristero_parcels_db(pgsql):
    return tristero_parcels_db.TristeroParcelsDbAgent(pgsql=pgsql)


@pytest.fixture(name='grocery_wms', autouse=True)
def mock_grocery_wms(mockserver):
    @mockserver.json_handler('/grocery-wms/api/external/products/v1/stocks')
    def _mock_wms(request):
        return {'code': 'OK', 'cursor': 'end', 'stocks': []}
