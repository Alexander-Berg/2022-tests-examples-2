import datetime as dt

import pytest
import pytz

BRAND_ID = 777
NON_DEFAULT_ASSORTMENT_DESTRUCTIVE_ERROR_TYPE = (
    'New non-default assortment is potentially destructive'
)
MOCK_NOW = dt.datetime(2021, 8, 13, 12, tzinfo=pytz.UTC)


async def properly_activate_assortment(place_id, activate_assortment):
    new_availabilities = [
        {'origin_id': 'item_origin_1', 'available': True},
        {'origin_id': 'item_origin_2', 'available': True},
        {'origin_id': 'item_origin_3', 'available': True},
    ]
    new_stocks = [
        {'origin_id': 'item_origin_1', 'stocks': None},
        {'origin_id': 'item_origin_2', 'stocks': None},
        {'origin_id': 'item_origin_3', 'stocks': None},
    ]
    new_prices = [
        {'origin_id': 'item_origin_1', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_2', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_3', 'price': '1000', 'currency': 'RUB'},
    ]
    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, task_id='1',
    )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize('verify_assortment_with_same_trait', [False, True])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_partner_and_custom_assortments_comparing(
        pgsql,
        activate_assortment,
        brand_task_enqueue,
        sql_get_place_assortment_proc_last_status,
        sql_get_place_assortment_last_status_history,
        testpoint,
        update_taxi_config,
        stq_runner,
        verify_assortment_with_same_trait,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_VERIFICATION',
        {
            f'{BRAND_ID}': {
                'assortment_remove_limit_in_percent': 1,
                'verify_assortment_with_same_trait': (
                    verify_assortment_with_same_trait
                ),
            },
        },
    )

    @testpoint('assortment-is-potentially-destructive')
    def task_testpoint(param):
        pass

    place_id = 1
    trait_id = 1

    data_to_upload = get_upload_data()
    await brand_task_enqueue(
        task_id='1', brand_id=str(BRAND_ID), brand_nomenclature=data_to_upload,
    )
    await properly_activate_assortment(place_id, activate_assortment)

    sql_fill_custom_assortment_data(pgsql)

    await brand_task_enqueue(
        task_id='2', brand_id=str(BRAND_ID), brand_nomenclature=data_to_upload,
    )
    assortment_id = 2
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
        expect_fail=not verify_assortment_with_same_trait,
    )
    await properly_activate_assortment(place_id, activate_assortment)

    if verify_assortment_with_same_trait:
        assert task_testpoint.times_called == 0
        last_status = {
            'status': 'processed',
            'assortment_id': assortment_id,
            'task_error': None,
            'task_error_details': None,
            'task_warnings': None,
            'status_or_text_changed_at': MOCK_NOW,
        }
    else:
        assert task_testpoint.times_called == 1
        last_status = {
            'status': 'failed',
            'assortment_id': assortment_id,
            'task_error': NON_DEFAULT_ASSORTMENT_DESTRUCTIVE_ERROR_TYPE,
            'task_error_details': (
                'New assortment is potentially destructive:'
                ' 33% of category_products were removed '
                '(prev_assortment_id=1, prev_count=3, new_count=2)'
            ),
            'task_warnings': None,
            'status_or_text_changed_at': MOCK_NOW,
        }
    excepted_last_statuses = [last_status]
    assert (
        sql_get_place_assortment_proc_last_status(place_id, trait_id)
        == last_status
    )
    assert (
        sql_get_place_assortment_last_status_history(place_id, trait_id)
        == excepted_last_statuses
    )

    sql_shrink_custom_assortment(pgsql)

    await brand_task_enqueue(
        task_id='3', brand_id=str(BRAND_ID), brand_nomenclature=data_to_upload,
    )
    assortment_id = 4
    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='2',
        kwargs={'assortment_id': assortment_id, 'trait_id': trait_id},
        expect_fail=True,
    )

    if verify_assortment_with_same_trait:
        assert task_testpoint.times_called == 1
        removed_percent = 50
        prev_assortment_id = 2
        prev_count = 2
    else:
        assert task_testpoint.times_called == 2
        removed_percent = 66
        prev_assortment_id = 3
        prev_count = 3

    new_count = 1
    last_status = {
        'assortment_id': assortment_id,
        'status': 'failed',
        'task_error': NON_DEFAULT_ASSORTMENT_DESTRUCTIVE_ERROR_TYPE,
        'task_error_details': (
            f'New assortment is potentially destructive:'
            f' {removed_percent}% of category_products were removed'
            f' (prev_assortment_id={prev_assortment_id},'
            f' prev_count={prev_count},'
            f' new_count={new_count})'
        ),
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    excepted_last_statuses.append(last_status)
    assert (
        sql_get_place_assortment_proc_last_status(place_id, trait_id)
        == last_status
    )
    assert (
        sql_get_place_assortment_last_status_history(place_id, trait_id)
        == excepted_last_statuses
    )


def sql_fill_custom_assortment_data(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            insert into eats_nomenclature.assortment_traits
            (brand_id, assortment_name, is_full_custom)
            values (777, 'test_assortment', true);

            insert into eats_nomenclature.custom_categories_groups
            (id, public_id, name)
            values (1, '11111111111111111111111111111111', 'custom_group_1');

            insert into eats_nomenclature.brands_custom_categories_groups
            (brand_id, custom_categories_group_id, trait_id)
            values (777, 1, 1);

            insert into eats_nomenclature.product_pictures (
                product_id,
                picture_id
            )
            values (1, 1);

            insert into eats_nomenclature.custom_categories
            (name, picture_id, external_id) values
            ('custom_category_1', 1, 1),
            ('custom_category_2', 1, 2);

            insert into eats_nomenclature.custom_categories_products
            (custom_category_id, product_id) values
            (1, 1),
            (2, 2);

            insert into eats_nomenclature.custom_categories_relations(
                custom_category_group_id,
                custom_category_id,
                parent_custom_category_id
            )
            values
            (1, 1, null),
            (1, 2, null);
        """,
    )


def sql_shrink_custom_assortment(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
            delete from eats_nomenclature.custom_categories_products
            where custom_category_id = 2;
        """,
    )


def get_upload_data():
    return {
        'categories': [
            {
                'images': [],
                'name': 'category_1',
                'origin_id': 'category_1_origin',
                'sort_order': 100,
            },
            {
                'images': [],
                'name': 'category_2',
                'origin_id': 'category_2_origin',
                'sort_order': 100,
            },
            {
                'images': [],
                'name': 'category_3',
                'origin_id': 'category_3_origin',
                'sort_order': 100,
            },
        ],
        'items': [
            {
                'adult': True,
                'barcodes': [
                    {
                        'type': 'ausreply',
                        'value': '123ETR123',
                        'weight_encoding': 'none',
                    },
                ],
                'category_origin_ids': ['category_1_origin'],
                'description': {
                    'composition': 'item 1 composition',
                    'expires_in': 'item 1 expires in',
                    'general': 'item 1 description',
                    'nutritional_value': 'item 1 nutritional vale',
                    'package_info': 'item 1 package info',
                    'purpose': 'item 1 purpose',
                    'storage_requirements': 'item 1 storage requirements',
                    'vendor_country': 'country_2',
                    'vendor_name': 'vendor_2',
                },
                'images': [{'hash': '', 'url': 'url_1'}],
                'is_catch_weight': True,
                'is_choosable': False,
                'location': 'item 1 location',
                'measure': {'quantum': 1, 'unit': 'GRM', 'value': 20},
                'name': 'item_1',
                'origin_id': 'item_origin_1',
                'price': 300,
                'shipping_type': 'delivery',
                'sort_order': 100,
                'vat': 20,
                'vendor_code': 'item 1 vendor code',
                'volume': {'unit': 'DMQ', 'value': 100},
            },
            {
                'adult': True,
                'barcodes': [],
                'category_origin_ids': ['category_1_origin'],
                'description': {
                    'composition': 'item 2 composition',
                    'expires_in': 'item 2 expires in',
                    'general': 'item 2 description',
                    'nutritional_value': 'item 2 nutritional vale',
                    'package_info': 'item 2 package info',
                    'purpose': 'item 2 purpose',
                    'storage_requirements': 'item 2 storage requirements',
                    'vendor_country': 'country_3',
                    'vendor_name': 'vendor_3',
                },
                'images': [],
                'is_catch_weight': True,
                'is_choosable': True,
                'location': 'item 2 location',
                'measure': {'quantum': 0.2, 'unit': 'GRM', 'value': 300},
                'name': 'item_2',
                'origin_id': 'item_origin_2',
                'price': 100,
                'shipping_type': 'delivery',
                'sort_order': 30,
                'vat': 20,
                'vendor_code': 'vendor_code',
                'volume': {'unit': 'DMQ', 'value': 100},
            },
            {
                'adult': True,
                'barcodes': [],
                'category_origin_ids': ['category_2_origin'],
                'description': {
                    'composition': 'item 3 composition',
                    'expires_in': 'item 3 expires in',
                    'general': 'item 3 description',
                    'nutritional_value': 'item 3 nutritional vale',
                    'package_info': 'Тетрапак',
                    'purpose': 'item 3 purpose',
                    'storage_requirements': 'item 3 storage requirements',
                    'vendor_country': 'country_1',
                    'vendor_name': 'vendor_1',
                },
                'images': [],
                'is_catch_weight': True,
                'is_choosable': True,
                'location': 'item 3 location',
                'measure': {'quantum': 1, 'unit': 'GRM', 'value': 1000},
                'name': 'item_3',
                'origin_id': 'item_origin_3',
                'price': 300,
                'shipping_type': 'all',
                'sort_order': 0,
                'vat': 20,
                'vendor_code': 'vendor_code',
                'volume': {'unit': 'DMQ', 'value': 100},
            },
        ],
    }
