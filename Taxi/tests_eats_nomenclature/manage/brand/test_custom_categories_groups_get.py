import pytest


HANDLER = '/v1/manage/brand/custom_categories_groups'
BRAND_ID = 1
ASSORTMENT_NAME = 'test_1'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_404_unknown_assortment_name(taxi_eats_nomenclature):
    unknown_assortment_name = 'UNKNOWN_ASSORTMENT_NAME'
    response = await taxi_eats_nomenclature.get(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&assortment_name={unknown_assortment_name}',
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_no_custom_groups(taxi_eats_nomenclature):
    brand_id = 2
    response = await taxi_eats_nomenclature.get(
        HANDLER + f'?brand_id={brand_id}',
    )
    assert response.status_code == 200
    assert response.json()['custom_categories_groups'] == []


@pytest.mark.pgsql('eats_nomenclature', files=['fill_brand_custom_groups.sql'])
async def test_404_no_default_assortment(
        taxi_eats_nomenclature, sql_remove_default_assortment_trait,
):
    sql_remove_default_assortment_trait(BRAND_ID)

    response = await taxi_eats_nomenclature.get(
        HANDLER + f'?brand_id={BRAND_ID}',
    )
    assert response.status_code == 404


async def test_404_unknown_brand(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.get(HANDLER + '?brand_id=123')
    assert response.status_code == 404


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_groups.sql'])
async def test_merge(
        taxi_eats_nomenclature,
        pgsql,
        use_assortment_name,
        sql_get_assortment_trait_id,
):
    assortment_name = ASSORTMENT_NAME if use_assortment_name else None
    sql_get_assortment_trait_id(
        BRAND_ID, assortment_name, insert_if_missing=True,
    )

    custom_categories_groups = [
        {
            'public_id': '11111111-1111-1111-1111-111111111111',
            'name': 'custom_group_1',
            'description': 'description_1',
            'is_enabled': True,
            'sort_order': 10,
        },
        {
            'public_id': '22222222-2222-2222-2222-222222222222',
            'name': 'custom_group_2',
            'description': 'description_2',
            'is_enabled': True,
            'sort_order': 20,
        },
        {
            'public_id': '33333333-3333-3333-3333-333333333333',
            'name': 'custom_group_3',
            'description': 'description_3',
            'is_enabled': False,
            'sort_order': 30,
        },
    ]

    def sorted_response_by_public_id(data):
        data['custom_categories_groups'] = sorted(
            data['custom_categories_groups'], key=lambda k: k['public_id'],
        )
        return data

    brand_custom_groups = {
        'categories_groups': [
            {'id': i['public_id'], 'sort_order': i['sort_order']}
            for i in custom_categories_groups
        ],
    }
    assortment_query = (
        f'&assortment_name={ASSORTMENT_NAME}' if use_assortment_name else ''
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}' + assortment_query,
        json=brand_custom_groups,
    )
    custom_group_id = 3
    sql_disable_brand_custom_group(
        pgsql, BRAND_ID, custom_group_id, assortment_name,
    )

    response = await taxi_eats_nomenclature.get(
        HANDLER + f'?brand_id={BRAND_ID}' + assortment_query,
    )
    assert response.status_code == 200
    assert (
        sorted_response_by_public_id(response.json())
        == sorted_response_by_public_id(
            {'custom_categories_groups': custom_categories_groups},
        )
    )


def sql_disable_brand_custom_group(
        pgsql, brand_id, custom_group_id, assortment_name,
):
    cursor = pgsql['eats_nomenclature'].cursor()
    if not assortment_name:
        assortment_name = 'default_assortment'

    cursor.execute(
        """
        update eats_nomenclature.brands_custom_categories_groups
        set is_enabled = false
        where brand_id = %s
        and custom_categories_group_id = %s
        and trait_id in (
            select id
            from eats_nomenclature.assortment_traits
            where assortment_name = %s
        )
        """,
        (brand_id, custom_group_id, assortment_name),
    )
