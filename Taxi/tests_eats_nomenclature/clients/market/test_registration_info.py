import pytest


@pytest.mark.pgsql('eats_nomenclature', files=['fill_market_places.sql'])
async def test_no_info(taxi_eats_nomenclature):
    request = {'place_ids': [4, 5, 6, 7]}
    response = await taxi_eats_nomenclature.post(
        f'/v1/market/registration_info', json=request,
    )
    assert response.status == 200
    assert not response.json()['registration_info']


@pytest.mark.pgsql('eats_nomenclature', files=['fill_market_places.sql'])
async def test_normal(taxi_eats_nomenclature):
    request = {'place_ids': [1, 2, 4, 3]}
    response = await taxi_eats_nomenclature.post(
        f'/v1/market/registration_info', json=request,
    )
    assert response.status == 200
    assert set(
        (
            i['brand_id'],
            i['place_id'],
            i['business_id'],
            i['partner_id'],
            i['feed_id'],
        )
        for i in response.json()['registration_info']
    ) == {(777, 1, 10, 20, 30), (777, 2, 40, 50, 60), (778, 3, 70, 80, 90)}
