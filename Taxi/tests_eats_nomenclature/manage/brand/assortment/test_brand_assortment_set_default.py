import pytest

from .... import utils


HANDLER = '/v1/manage/brand/assortment/set_default'
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


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_404_inactive_assortment(taxi_eats_nomenclature, pgsql):
    # Add assortment only for place 1, while place 2 won't have one
    # Place 3 is enabled so it is ignored anyway
    sql_insert_place_assortment(pgsql, 2, 1)

    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&assortment_name={ASSORTMENT_NAME}',
    )
    assert response.status_code == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_204_null_assortment_name(taxi_eats_nomenclature, pgsql):
    sql_insert_place_assortment(pgsql, None, 1)
    sql_insert_place_assortment(pgsql, None, 2)

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?brand_id={BRAND_ID}',
    )
    assert response.status_code == 204
    assert sql_get_brand_default_trait(pgsql, BRAND_ID) is None


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_204_not_null_assortment_name(taxi_eats_nomenclature, pgsql):
    sql_insert_place_assortment(pgsql, 2, 1)
    sql_insert_place_assortment(pgsql, 2, 2)

    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&assortment_name={ASSORTMENT_NAME}',
    )
    assert response.status_code == 204
    assert sql_get_brand_default_trait(pgsql, BRAND_ID) == 2


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_204_null_brand_default_assortment(
        taxi_eats_nomenclature, pgsql,
):
    sql_del_brand_default_trait(pgsql, BRAND_ID)
    sql_insert_place_assortment(pgsql, 2, 1)
    sql_insert_place_assortment(pgsql, 2, 2)

    response = await taxi_eats_nomenclature.post(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&assortment_name={ASSORTMENT_NAME}',
    )
    assert response.status_code == 204
    assert sql_get_brand_default_trait(pgsql, BRAND_ID) == 2


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
@pytest.mark.parametrize(
    **utils.gen_bool_params('enqueue_fts_if_new_default_assortment'),
)
@pytest.mark.parametrize(**utils.gen_bool_params('enable_fts_enqueue'))
async def test_enqueue_fts(
        taxi_eats_nomenclature,
        pgsql,
        stq,
        update_taxi_config,
        # parametrize
        enqueue_fts_if_new_default_assortment,
        enable_fts_enqueue,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_TEMPORARY_CONFIGS',
        {
            'enqueue_fts_if_new_default_assortment': (
                enqueue_fts_if_new_default_assortment
            ),
        },
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_ASSORTMENT_ACTIVATION_NOTIFICATION_SETTINGS',
        {
            'common_delay_in_seconds': 0,
            'is_enabled': True,
            'per_component_additional_settings': {
                '__default__': {
                    'is_enabled': True,
                    'additional_delay_in_seconds': 0,
                },
                'stq_eats_full_text_search_indexer_update_retail_place': {
                    'is_enabled': enable_fts_enqueue,
                    'additional_delay_in_seconds': 0,
                },
            },
        },
    )

    sql_insert_place_assortment(pgsql, 2, 1)
    sql_insert_place_assortment(pgsql, 2, 2)

    await taxi_eats_nomenclature.post(
        HANDLER
        + f'?brand_id={BRAND_ID}'
        + f'&assortment_name={ASSORTMENT_NAME}',
    )

    fts_queue = stq.eats_full_text_search_indexer_update_retail_place
    if enqueue_fts_if_new_default_assortment and enable_fts_enqueue:
        assert fts_queue.times_called == 2
        enqueued_places = set()
        while fts_queue.has_calls:
            task_info = fts_queue.next_call()
            enqueued_places.add(task_info['kwargs']['place_slug'])
        assert enqueued_places == {'slug1', 'slug2'}
    else:
        assert not fts_queue.has_calls


def sql_get_brand_default_trait(pgsql, brand_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select trait_id
        from eats_nomenclature.brand_default_assortments
        where brand_id={brand_id}
        """,
    )
    return cursor.fetchone()[0]


def sql_del_brand_default_trait(pgsql, brand_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        delete from eats_nomenclature.brand_default_assortments
        where brand_id={brand_id}
        """,
    )


def sql_insert_place_assortment(pgsql, trait_id, place_id, assortment_id=1):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        insert into eats_nomenclature.place_assortments (
            place_id, trait_id, assortment_id
        ) values (%s, %s, %s)
        """,
        (place_id, trait_id, assortment_id),
    )
