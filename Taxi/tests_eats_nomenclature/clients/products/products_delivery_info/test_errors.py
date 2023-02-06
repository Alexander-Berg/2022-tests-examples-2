import pytest

HANDLER = '/v1/products/delivery_info'
UNKNOWN_PLACE_ID = 999
PLACE_ID_WITHOUT_BRAND = 1


@pytest.mark.pgsql('eats_nomenclature', files=['fill_dictionaries.sql'])
async def test_unknown_place(taxi_eats_nomenclature):
    body = {'origin_ids': ['item_origin_1']}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={UNKNOWN_PLACE_ID}', json=body,
    )
    assert response.status == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_dictionaries.sql'])
async def test_place_without_brand(pgsql, taxi_eats_nomenclature):
    _sql_add_place_without_brand(pgsql)

    body = {'origin_ids': ['item_origin_1']}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={UNKNOWN_PLACE_ID}', json=body,
    )
    assert response.status == 404


def _sql_add_place_without_brand(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        insert into eats_nomenclature.places (id, slug)
        values(%s, %s)
        """,
        (PLACE_ID_WITHOUT_BRAND, 'slug'),
    )
