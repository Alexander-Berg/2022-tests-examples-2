HANDLER = '/v1/manage/brand/assortment/get'
ADD_HANDLER = '/v1/manage/brand/assortment/add'
BRAND_ID = 1


async def test_404_unknown_brand(taxi_eats_nomenclature):
    unknown_brand_id = 100
    response = await taxi_eats_nomenclature.get(
        HANDLER + f'?brand_id={unknown_brand_id}',
    )
    assert response.status_code == 404


async def test_200_empty_response(taxi_eats_nomenclature, pgsql):
    sql_insert_brand(pgsql)

    response = await taxi_eats_nomenclature.get(
        HANDLER + f'?brand_id={BRAND_ID}',
    )
    assert response.status_code == 200
    assert response.json()['assortments'] == []


async def test_200_non_empty_response(taxi_eats_nomenclature, pgsql):
    sql_insert_brand(pgsql)

    # Add assortment traits.
    assortment_traits = [
        {'name': 'name1', 'is_full_custom': True},
        {'name': 'name2', 'is_full_custom': False},
    ]
    for assortment_trait in assortment_traits:
        name = assortment_trait['name']
        is_full_custom = assortment_trait['is_full_custom']
        response = await taxi_eats_nomenclature.post(
            ADD_HANDLER
            + f'?brand_id={BRAND_ID}'
            + f'&assortment_name={name}'
            + f'&is_full_custom={is_full_custom}',
        )

    response = await taxi_eats_nomenclature.get(
        HANDLER + f'?brand_id={BRAND_ID}',
    )
    assert response.status_code == 200
    assert response.json()['assortments'] == assortment_traits


def sql_insert_brand(pgsql, brand_id=BRAND_ID):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.brands (id)
        values ({brand_id})
        """,
    )
