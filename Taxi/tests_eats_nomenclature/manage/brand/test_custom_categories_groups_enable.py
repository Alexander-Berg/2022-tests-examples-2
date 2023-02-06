import pytest

BRAND_CUSTOM_GROUP_HANDLER = '/v1/manage/brand/custom_categories_groups'
ENABLE_CUSTOM_GROUP_HANDLER = (
    '/v1/manage/brand/custom_categories_groups/enable'
)
BRAND_ID = 1
ASSORTMENT_NAME = 'test_1'


async def test_404_unknown_brand(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        ENABLE_CUSTOM_GROUP_HANDLER + '?brand_id=123',
        json={
            'custom_categories_group_id': (
                '11111111-1111-1111-1111-111111111111'
            ),
            'enabled': True,
        },
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_groups.sql'])
async def test_404_unknown_custom_group(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        ENABLE_CUSTOM_GROUP_HANDLER + f'?brand_id={BRAND_ID}',
        json={
            'custom_categories_group_id': (
                '77777777-7777-7777-7777-777777777777'
            ),
            'enabled': True,
        },
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_groups.sql'])
async def test_404_unknown_assortment_name(taxi_eats_nomenclature):
    unknown_assortment_name = 'UNKNOWN_ASSORTMENT_NAME'
    public_id = '11111111-1111-1111-1111-111111111111'

    response = await taxi_eats_nomenclature.post(
        ENABLE_CUSTOM_GROUP_HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&assortment_name={unknown_assortment_name}',
        json={'custom_categories_group_id': public_id, 'enabled': False},
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_groups.sql'])
async def test_404_no_default_assortment(
        taxi_eats_nomenclature, sql_remove_default_assortment_trait,
):

    sql_remove_default_assortment_trait(BRAND_ID)

    public_id = '11111111-1111-1111-1111-111111111111'

    response = await taxi_eats_nomenclature.post(
        ENABLE_CUSTOM_GROUP_HANDLER + f'?brand_id={BRAND_ID}',
        json={'custom_categories_group_id': public_id, 'enabled': False},
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_custom_groups.sql'])
async def test_enable(
        taxi_eats_nomenclature,
        use_assortment_name,
        sql_get_assortment_trait_id,
):

    public_id = '11111111-1111-1111-1111-111111111111'
    assortment_query = (
        f'&assortment_name={ASSORTMENT_NAME}' if use_assortment_name else ''
    )
    sql_get_assortment_trait_id(
        BRAND_ID,
        ASSORTMENT_NAME if use_assortment_name else None,
        insert_if_missing=True,
    )

    request = {'categories_groups': [{'id': public_id}]}
    response = await taxi_eats_nomenclature.post(
        BRAND_CUSTOM_GROUP_HANDLER
        + f'?brand_id={BRAND_ID}'
        + assortment_query,
        json=request,
    )
    assert response.status_code == 200

    response = await taxi_eats_nomenclature.get(
        BRAND_CUSTOM_GROUP_HANDLER
        + f'?brand_id={BRAND_ID}'
        + assortment_query,
    )
    assert response.status_code == 200
    assert response.json()['custom_categories_groups'][0]['is_enabled'] is True

    # Disable custom group.
    response = await taxi_eats_nomenclature.post(
        ENABLE_CUSTOM_GROUP_HANDLER
        + f'?brand_id={BRAND_ID}'
        + assortment_query,
        json={'custom_categories_group_id': public_id, 'enabled': False},
    )
    assert response.status_code == 204

    response = await taxi_eats_nomenclature.get(
        BRAND_CUSTOM_GROUP_HANDLER
        + f'?brand_id={BRAND_ID}'
        + assortment_query,
    )
    assert response.status_code == 200
    assert (
        response.json()['custom_categories_groups'][0]['is_enabled'] is False
    )

    # Enable custom group.
    response = await taxi_eats_nomenclature.post(
        ENABLE_CUSTOM_GROUP_HANDLER
        + f'?brand_id={BRAND_ID}'
        + assortment_query,
        json={'custom_categories_group_id': public_id, 'enabled': True},
    )
    assert response.status_code == 204

    response = await taxi_eats_nomenclature.get(
        BRAND_CUSTOM_GROUP_HANDLER
        + f'?brand_id={BRAND_ID}'
        + assortment_query,
    )
    assert response.status_code == 200
    assert response.json()['custom_categories_groups'][0]['is_enabled'] is True
