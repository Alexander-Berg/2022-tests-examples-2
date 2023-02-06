# -*- coding: utf-8 -*-
import pytest


@pytest.mark.servicetest
async def test_ping(taxi_supply_diagnostics, mockserver):
    @mockserver.json_handler('/candidates/v1/list-profiles')
    def _mock_candidates(request):
        return {'drivers': []}

    response = await taxi_supply_diagnostics.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''
