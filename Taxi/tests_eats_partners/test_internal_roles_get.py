import pytest


@pytest.mark.pgsql('eats_partners', files=['insert_roles.sql'])
async def test_internal_partners_info(taxi_eats_partners, load_json):
    response = await taxi_eats_partners.get('/internal/partners/v1/roles')

    assert response.status_code == 200
    assert response.json() == load_json('response.json')
