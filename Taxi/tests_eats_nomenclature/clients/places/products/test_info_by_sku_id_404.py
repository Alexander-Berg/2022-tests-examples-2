import pytest

from . import constants


SKU_UUID = constants.SKU_UUID
HANDLER = constants.HANDLER


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_unknown_sku(taxi_eats_nomenclature, load_json):
    place_id = 1
    unknown_sku_id = '99999999-1111-1111-1111-111111111111'

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}', json={'place_ids': [place_id], 'sku_id': unknown_sku_id},
    )
    assert response.status_code == 404
    assert response.json() == {
        'status': 404,
        'message': f'Unknown sku_id {unknown_sku_id}',
    }


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_unknown_place(
        taxi_eats_nomenclature, sql_add_product, sql_add_sku,
):
    unknown_place_id = 123

    sku_id = sql_add_sku(SKU_UUID)
    sql_add_product(origin_id='origin_id_1', sku_id=sku_id)

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}',
        json={'place_ids': [unknown_place_id], 'sku_id': SKU_UUID},
    )
    assert response.status_code == 404
    assert response.json() == {'status': 404, 'message': f'Unknown places'}
