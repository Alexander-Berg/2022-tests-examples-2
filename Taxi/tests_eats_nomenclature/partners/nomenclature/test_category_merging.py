import datetime

import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_another_place_data.sql'],
)
async def test_category_merging(
        load_json,
        pgsql,
        taxi_config,
        mocked_time,
        activate_assortment,
        brand_task_enqueue,
):
    assortment_enrichment_timeout = 40
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS': {
                'assortment_enrichment_timeout': assortment_enrichment_timeout,
                'max_task_lifetime_in_min': 100,
            },
        },
    )
    now = mocked_time.now()

    place_id = '1'

    # check data in the currently inactive assortment

    assortment_id = sql_get_assortment_id(pgsql, place_id, False)
    assert sql_get_categories(pgsql, assortment_id) == {
        ('category_1', True, False),
        ('category_2', True, False),
        ('category_3', True, False),
        ('category_4', True, False),
        ('category_5', True, False),
    }

    # upload new data (which will merge data in
    # inactive assortment and will make it active)

    data_to_upload = load_json('upload_data.json')

    await brand_task_enqueue(task_id='1', brand_nomenclature=data_to_upload)
    new_availabilities = [
        {'origin_id': 'item_origin_4', 'available': True},
        {'origin_id': 'item_origin_5', 'available': True},
        {'origin_id': 'item_origin_6', 'available': True},
    ]
    new_stocks = [
        {'origin_id': 'item_origin_4', 'stocks': None},
        {'origin_id': 'item_origin_5', 'stocks': None},
        {'origin_id': 'item_origin_6', 'stocks': None},
    ]
    new_prices = [
        {'origin_id': 'item_origin_4', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_5', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_6', 'price': '1000', 'currency': 'RUB'},
    ]
    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, '1',
    )

    assortment_id = sql_get_assortment_id(pgsql, place_id)
    assert sql_get_categories(pgsql, assortment_id) == {
        ('category_3', True, False),
        ('category_6', True, False),
    }

    # upload data again (to check that it works
    # with the other assortment as well)

    now += datetime.timedelta(minutes=assortment_enrichment_timeout + 1)
    mocked_time.set(now)
    await brand_task_enqueue(task_id='1', brand_nomenclature=data_to_upload)

    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, '1',
    )

    assortment_id = sql_get_assortment_id(pgsql, place_id)
    assert sql_get_categories(pgsql, assortment_id) == {
        ('category_3', True, False),
        ('category_6', True, False),
    }

    # upload same data but with changed values
    # (to check that merge works)

    for cat in data_to_upload['categories']:
        cat['name'] += '_new'

    now += datetime.timedelta(minutes=assortment_enrichment_timeout + 1)
    mocked_time.set(now)
    await brand_task_enqueue(task_id='1', brand_nomenclature=data_to_upload)

    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, '1',
    )

    assortment_id = sql_get_assortment_id(pgsql, place_id)
    assert sql_get_categories(pgsql, assortment_id) == {
        ('category_3_new', True, False),
        ('category_6_new', True, False),
    }


def sql_get_assortment_id(pgsql, place_id, is_active=True):
    field = 'assortment_id'
    if not is_active:
        field = 'in_progress_assortment_id'

    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select pa.{field}
        from eats_nomenclature.place_assortments pa
        join eats_nomenclature.assortments a
          on pa.{field} = a.id
        where pa.place_id = {place_id}
        """,
    )
    return list(cursor)[0][0]


def sql_get_categories(pgsql, assortment_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        SELECT name, is_base, is_restaurant
        FROM eats_nomenclature.categories
        where assortment_id={assortment_id}
        """,
    )
    return set(cursor)
