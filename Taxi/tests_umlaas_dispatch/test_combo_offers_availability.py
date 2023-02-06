# pylint: disable=import-error

import pytest

URL = '/umlaas-dispatch/v1/combo-offers-availability'


async def test_ml_combo_offers_availability(taxi_umlaas_dispatch, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_dispatch.post(URL, request)
    assert response.status_code == 200
