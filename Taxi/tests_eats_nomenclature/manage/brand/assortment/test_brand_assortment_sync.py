import pytest


HANDLER = '/v1/manage/brand/assortment/sync'
BRAND_ID = 1
ASSORTMENT_NAME = 'new_assortment_name'


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_404_unknown_assortment_name(taxi_eats_nomenclature):
    unknown_assortment_name = 'unknown_assortment_name'
    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&assortment_name={unknown_assortment_name}',
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_404_unknown_brand_id(taxi_eats_nomenclature):
    unknown_brand_id = 2
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={unknown_brand_id}',
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'use_assortment_name',
    [
        pytest.param(True, id='has_assortment_name'),
        pytest.param(False, id='empty_assortment_name'),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_204(
        taxi_eats_nomenclature,
        sql_get_assortment_trait_id,
        stq,
        # parametrize params
        use_assortment_name,
):
    trait_id = sql_get_assortment_trait_id(
        BRAND_ID,
        ASSORTMENT_NAME if use_assortment_name else None,
        insert_if_missing=True,
    )

    assortment_query = (
        f'&assortment_name={ASSORTMENT_NAME}' if use_assortment_name else ''
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}' + assortment_query,
    )
    assert response.status_code == 204

    assert stq.eats_nomenclature_update_brand_assortments.times_called == 1
    task_info = stq.eats_nomenclature_update_brand_assortments.next_call()
    assert task_info['kwargs']['brand_id'] == BRAND_ID
    assert task_info['kwargs']['trait_id'] == trait_id
    assert task_info['id'] == f'{BRAND_ID}_{trait_id}'
