import json

import pytest


@pytest.fixture(name='lavka_stocks', autouse=True)
def _lavka_stocks(mockserver, load_json):
    @mockserver.handler('/lavka-wms/4/availableforsale/', prefix=True)
    def _mock_all(request):
        return mockserver.make_response(
            json.dumps(load_json('stocks_response.json')), 200,
        )
