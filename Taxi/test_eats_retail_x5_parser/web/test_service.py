import pytest


@pytest.mark.servicetest
async def test_ping(taxi_eats_retail_x5_parser_web):
    response = await taxi_eats_retail_x5_parser_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
