import pytest


HANDLER = '/v1/manage/brand/assortment/add'
BRAND_ID = 1


async def test_partner_assortment_name(taxi_eats_nomenclature, pgsql):
    assortment_name = 'partner'
    sql_insert_assortment_trait(pgsql, assortment_name=assortment_name)
    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&assortment_name={assortment_name}',
    )
    assert response.status_code == 409


@pytest.mark.parametrize('is_full_custom', [True, False])
async def test_409(taxi_eats_nomenclature, pgsql, is_full_custom):
    assortment_name = 'assortment_name'
    sql_insert_assortment_trait(pgsql, assortment_name=assortment_name)
    old_data = sql_select_assortment_trait(pgsql)

    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&assortment_name={assortment_name}'
        + f'&is_full_custom={is_full_custom}',
    )
    assert response.status_code == 409
    assert old_data == sql_select_assortment_trait(pgsql)


@pytest.mark.parametrize('is_full_custom', [True, False])
async def test_204(taxi_eats_nomenclature, pgsql, is_full_custom):
    assortment_name = 'assortment_name'
    sql_insert_assortment_trait(pgsql, assortment_name=assortment_name)
    old_data = sql_select_assortment_trait(pgsql)

    new_assortment_name = 'new_assortment_name'

    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&assortment_name={new_assortment_name}'
        + f'&is_full_custom={is_full_custom}',
    )
    assert response.status_code == 204
    expected_data = old_data | {(new_assortment_name, is_full_custom)}
    assert expected_data == sql_select_assortment_trait(pgsql)


def sql_select_assortment_trait(pgsql, brand_id=BRAND_ID):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select assortment_name, is_full_custom
        from eats_nomenclature.assortment_traits
        where brand_id = {brand_id}
        """,
    )
    return {(row[0], row[1]) for row in cursor}


def sql_insert_assortment_trait(
        pgsql, assortment_name, brand_id=BRAND_ID, is_full_custom=False,
):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.brands (id)
        values ({brand_id})
        """,
    )
    cursor.execute(
        f"""
        insert into eats_nomenclature.assortment_traits (
            brand_id, assortment_name, is_full_custom
        ) values ({brand_id}, '{assortment_name}', {is_full_custom})
        """,
    )
