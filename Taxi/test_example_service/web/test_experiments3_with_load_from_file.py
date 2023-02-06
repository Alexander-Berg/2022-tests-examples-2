import pytest


@pytest.mark.client_experiments3(experiments_bodies='exp.json')
@pytest.mark.usefixtures('territories_mock')
async def test_who_are_you(web_app_client):
    response = await web_app_client.get(f'/who_are_you?phone=79219201566')
    assert response.status == 200
    assert (await response.text()) == 'taxi'
