import json

import pytest


@pytest.fixture(name='lavka_wms', autouse=True)
def _lavka_wms(mockserver, load_json):
    @mockserver.handler('/lavka-wms/5/nomenclature/', prefix=True)
    def _mock_v5(request):
        return mockserver.make_response(
            json.dumps(load_json('lavka_wms_response.json')), 200,
        )

    @mockserver.handler('/lavka-wms/4/nomenclature/', prefix=True)
    def _mock_v4(request):
        return mockserver.make_response(
            json.dumps(load_json('lavka_wms_response.json')), 200,
        )
