import datetime as dt

import pytest


HANDLER = '/v1/manage/brand/custom_categories_groups/delete'
BRAND_ID = 1
ASSORTMENT_NAME = 'test_1'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_404_unknown_brand(taxi_eats_nomenclature):
    unknown_brand_id = 123
    custom_group_id = '11111111-1111-1111-1111-111111111111'
    response = await taxi_eats_nomenclature.get(
        HANDLER
        + f'?brand_id={unknown_brand_id}'
        + f'&categories_group_id={custom_group_id}',
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_404_unknown_custom_group(taxi_eats_nomenclature):
    unknown_custom_group_id = '12345678-7777-7777-7777-777777777777'
    response = await taxi_eats_nomenclature.get(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&categories_group_id={unknown_custom_group_id}',
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_404_unknown_assortment_name(taxi_eats_nomenclature):
    custom_group_id = '12345678-7777-7777-7777-777777777777'
    unknown_assortment_name = 'UNKNOWN_ASSORTMENT_NAME'
    response = await taxi_eats_nomenclature.get(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&categories_group_id={custom_group_id}'
        + f'&assortment_name={unknown_assortment_name}',
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_404_no_default_assortment(
        taxi_eats_nomenclature, sql_remove_default_assortment_trait,
):
    sql_remove_default_assortment_trait(BRAND_ID)

    custom_group_id = '12345678-7777-7777-7777-777777777777'
    response = await taxi_eats_nomenclature.get(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&categories_group_id={custom_group_id}',
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_400_invalid_custom_group_id(
        taxi_eats_nomenclature, sql_get_assortment_trait_id,
):
    sql_get_assortment_trait_id(BRAND_ID, None, insert_if_missing=True)

    invalid_custom_group_id = 'invalid_custom_group_id'
    response = await taxi_eats_nomenclature.get(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&categories_group_id={invalid_custom_group_id}',
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_in_progress_assortment(
        taxi_eats_nomenclature,
        renew_in_progress_assortment,
        insert_enrichment_status,
        pgsql,
        sql_get_assortment_trait_id,
        use_assortment_name,
):
    place_id = 1
    custom_group_id = '33333333-3333-3333-3333-333333333333'
    assortment_name = ASSORTMENT_NAME if use_assortment_name else None
    sql_get_assortment_trait_id(
        BRAND_ID, assortment_name, insert_if_missing=True,
    )
    assortment_id = renew_in_progress_assortment(place_id)
    insert_enrichment_status(assortment_id, dt.datetime.now())
    assert sql_get_brand_custom_groups(pgsql, BRAND_ID, assortment_name) == {
        3,
        4,
        5,
        6,
    }

    assortment_query = (
        f'&assortment_name={ASSORTMENT_NAME}' if use_assortment_name else ''
    )
    response = await taxi_eats_nomenclature.get(
        HANDLER
        + f'?brand_id={BRAND_ID}&categories_group_id={custom_group_id}'
        + assortment_query,
    )
    assert response.status_code == 200
    assert sql_get_brand_custom_groups(pgsql, BRAND_ID, assortment_name) == {
        4,
        5,
        6,
    }


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_delete_custom_group(
        taxi_eats_nomenclature,
        pgsql,
        sql_get_assortment_trait_id,
        use_assortment_name,
):
    custom_group_id = '33333333-3333-3333-3333-333333333333'
    assortment_name = ASSORTMENT_NAME if use_assortment_name else None
    sql_get_assortment_trait_id(
        BRAND_ID, assortment_name, insert_if_missing=True,
    )

    assert sql_get_brand_custom_groups(pgsql, BRAND_ID, assortment_name) == {
        3,
        4,
        5,
        6,
    }

    assortment_query = (
        f'&assortment_name={ASSORTMENT_NAME}' if use_assortment_name else ''
    )
    response = await taxi_eats_nomenclature.get(
        HANDLER
        + f'?brand_id={BRAND_ID}&categories_group_id={custom_group_id}'
        + assortment_query,
    )
    assert response.status_code == 200
    assert sql_get_brand_custom_groups(pgsql, BRAND_ID, assortment_name) == {
        4,
        5,
        6,
    }


def sql_get_brand_custom_groups(pgsql, brand_id, assortment_name):
    if not assortment_name:
        assortment_name = 'default_assortment'

    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select custom_categories_group_id
        from eats_nomenclature.brands_custom_categories_groups ccgi
        join eats_nomenclature.assortment_traits at
            on at.id = trait_id
        where
            ccgi.brand_id = %s
            and at.assortment_name = %s
        """,
        (brand_id, assortment_name),
    )
    return {row[0] for row in cursor}
