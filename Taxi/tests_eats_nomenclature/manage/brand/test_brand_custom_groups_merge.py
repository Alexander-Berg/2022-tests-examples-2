import datetime as dt

import pytest


HANDLER = '/v1/manage/brand/custom_categories_groups'
BRAND_ID = 1
ASSORTMENT_NAME = 'test_1'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_404_no_default_assortment(
        taxi_eats_nomenclature, load_json, sql_remove_default_assortment_trait,
):
    sql_remove_default_assortment_trait(BRAND_ID)

    response = await taxi_eats_nomenclature.get(
        HANDLER + f'?brand_id={BRAND_ID}', json=load_json('request.json'),
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_merge(
        taxi_eats_nomenclature, load_json, pgsql, use_assortment_name,
):
    assortment_name = ASSORTMENT_NAME if use_assortment_name else None

    old_data_expected = {3: 200, 4: 300, 5: 100, 6: 100}
    assert (
        sql_get_brand_custom_groups(pgsql, BRAND_ID, assortment_name)
        == old_data_expected
    )

    assortment_query = (
        f'&assortment_name={ASSORTMENT_NAME}' if use_assortment_name else ''
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}' + assortment_query,
        json=load_json('request.json'),
    )

    assert response.status_code == 200
    new_data_expected = {1: 200, 2: 10, 3: 100, 4: 50}
    assert (
        sql_get_brand_custom_groups(pgsql, BRAND_ID, assortment_name)
        == new_data_expected
    )


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
        load_json,
        pgsql,
        renew_in_progress_assortment,
        insert_enrichment_status,
        sql_get_assortment_trait_id,
        use_assortment_name,
):
    place_id = 1
    assortment_name = ASSORTMENT_NAME if use_assortment_name else None
    sql_get_assortment_trait_id(
        BRAND_ID, assortment_name, insert_if_missing=True,
    )

    assortment_id = renew_in_progress_assortment(place_id)
    insert_enrichment_status(assortment_id, dt.datetime.now())
    old_data_expected = {3: 200, 4: 300, 5: 100, 6: 100}
    assert (
        sql_get_brand_custom_groups(pgsql, BRAND_ID, assortment_name)
        == old_data_expected
    )

    # Request brand with in_progress_assortment.
    assortment_query = (
        f'&assortment_name={ASSORTMENT_NAME}' if use_assortment_name else ''
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}' + assortment_query,
        json=load_json('request.json'),
    )

    assert response.status_code == 200
    new_data_expected = {1: 200, 2: 10, 3: 100, 4: 50}
    assert (
        sql_get_brand_custom_groups(pgsql, BRAND_ID, assortment_name)
        == new_data_expected
    )


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.parametrize(
    'use_only_custom_categories, status_code,', [(True, 400), (False, 200)],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_clean_brand_groups(
        taxi_eats_nomenclature,
        pgsql,
        use_only_custom_categories,
        status_code,
        use_assortment_name,
):

    assortment_name = ASSORTMENT_NAME if use_assortment_name else None

    old_data_expected = {3: 200, 4: 300, 5: 100, 6: 100}
    assert (
        sql_get_brand_custom_groups(pgsql, BRAND_ID, assortment_name)
        == old_data_expected
    )

    empty_request = {
        'categories_groups': [],
        'use_only_custom_categories': use_only_custom_categories,
    }
    assortment_query = (
        f'&assortment_name={ASSORTMENT_NAME}' if use_assortment_name else ''
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}' + assortment_query,
        json=empty_request,
    )

    assert response.status_code == status_code
    brand_groups_were_cleaned = (
        sql_get_brand_custom_groups(pgsql, BRAND_ID, assortment_name) == {}
    )
    assert use_only_custom_categories != brand_groups_were_cleaned


def sql_get_brand_custom_groups(pgsql, brand_id, assortment_name):
    if not assortment_name:
        assortment_name = 'default_assortment'

    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select custom_categories_group_id, sort_order
        from eats_nomenclature.brands_custom_categories_groups ccgi
        join eats_nomenclature.assortment_traits at
            on at.id = trait_id
        where
            ccgi.brand_id = %s
            and at.assortment_name = %s
        """,
        (brand_id, assortment_name),
    )
    return {row[0]: row[1] for row in cursor}
