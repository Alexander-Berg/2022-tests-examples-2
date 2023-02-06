import copy
import datetime as dt

import pytest
import pytz

from ... import utils

BRAND_ID = 777
PLACE_ID = 1
TRAIT_ID = 1
NON_DEFAULT_ASSORTMENT_DESTRUCTIVE_ERROR_TYPE = (
    'New non-default assortment is potentially destructive'
)
DEFAULT_ASSORTMENT_DESTRUCTIVE_ERROR_TYPE = (
    'New default assortment is potentially destructive'
)
PARTNER_ASSORTMENT_DESTRUCTIVE_ERROR_TYPE = (
    'New partner assortment is potentially destructive'
)
ASSORTMENT_DESTRUCTIVE_ERROR_DETAILS = (
    'New assortment is potentially destructive: '
    '33% of category_products were removed '
    '(prev_assortment_id=1, prev_count=3, new_count=2)'
)
ASSORTMENT_DESTRUCTIVE_ERROR_DETAILS_2 = (
    'New assortment is potentially destructive: '
    '50% of category_products were removed '
    '(prev_assortment_id=2, prev_count=2, new_count=1)'
)
MOCK_NOW = dt.datetime(2021, 8, 13, 12, tzinfo=pytz.UTC)


def settings(limit):
    return {f'{BRAND_ID}': {'assortment_remove_limit_in_percent': limit}}


def set_enrichment_timeout(taxi_config, assortment_enrichment_timeout):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_PROCESSOR_TIMEOUTS': {
                'assortment_enrichment_timeout': assortment_enrichment_timeout,
                'max_task_lifetime_in_min': 50,
            },
        },
    )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.config(EATS_NOMENCLATURE_VERIFICATION=settings(1))
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_items_remove_too_much_1(
        pgsql,
        activate_assortment,
        brand_task_enqueue,
        sql_get_place_assortment_proc_last_status,
        sql_get_place_assortment_last_status_history,
        testpoint,
):
    @testpoint('assortment-is-potentially-destructive')
    def task_testpoint(param):
        pass

    data_to_upload = get_upload_data()
    assert not get_sql_item_origin_ids(pgsql)

    await brand_task_enqueue('1', brand_nomenclature=data_to_upload)
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
        new_availabilities, new_stocks, new_prices, PLACE_ID, '1',
    )
    last_status = {
        'status': 'processed',
        'assortment_id': 1,
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    expected_last_statuses = [last_status]
    assert sql_get_place_assortment_proc_last_status(PLACE_ID) == last_status
    assert (
        sql_get_place_assortment_last_status_history(PLACE_ID)
        == expected_last_statuses
    )

    assert get_sql_item_origin_ids(pgsql) == get_item_origin_ids(
        data_to_upload,
    )

    prev_data = copy.deepcopy(data_to_upload)
    data_to_upload['items'] = data_to_upload['items'][:-1]

    await brand_task_enqueue(
        '2', brand_nomenclature=data_to_upload, expect_fail=True,
    )

    assert task_testpoint.times_called == 1
    assert get_sql_item_origin_ids(pgsql) == get_item_origin_ids(prev_data)

    last_status = {
        'assortment_id': None,
        'status': 'failed',
        'task_error': PARTNER_ASSORTMENT_DESTRUCTIVE_ERROR_TYPE,
        'task_error_details': ASSORTMENT_DESTRUCTIVE_ERROR_DETAILS,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    expected_last_statuses.append(last_status)
    assert sql_get_place_assortment_proc_last_status(PLACE_ID) == last_status
    assert (
        sql_get_place_assortment_last_status_history(PLACE_ID)
        == expected_last_statuses
    )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.config(EATS_NOMENCLATURE_VERIFICATION=settings(50))
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_items_remove_too_much_50(
        pgsql,
        taxi_config,
        mocked_time,
        activate_assortment,
        brand_task_enqueue,
        sql_get_place_assortment_proc_last_status,
        sql_get_place_assortment_last_status_history,
        testpoint,
):
    @testpoint('assortment-is-potentially-destructive')
    def task_testpoint(param):
        pass

    assortment_enrichment_timeout = 40
    set_enrichment_timeout(taxi_config, assortment_enrichment_timeout)
    now = mocked_time.now()

    data_to_upload = get_upload_data()
    assert not get_sql_item_origin_ids(pgsql)

    await brand_task_enqueue('1', brand_nomenclature=data_to_upload)
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
        new_availabilities, new_stocks, new_prices, PLACE_ID, '1',
    )
    assert get_sql_item_origin_ids(pgsql) == get_item_origin_ids(
        data_to_upload,
    )
    last_status = {
        'status': 'processed',
        'assortment_id': 1,
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': MOCK_NOW,
    }
    expected_last_statuses = [last_status]

    data_to_upload['items'] = data_to_upload['items'][:-1]

    now += dt.timedelta(minutes=assortment_enrichment_timeout + 1)
    mocked_time.set(now)

    await brand_task_enqueue('2', brand_nomenclature=data_to_upload)

    await activate_assortment(
        new_availabilities, new_stocks, new_prices, PLACE_ID, '1',
    )

    last_status = {
        'status': 'processed',
        'assortment_id': 2,
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': now.replace(tzinfo=pytz.UTC),
    }
    expected_last_statuses.append(last_status)
    assert sql_get_place_assortment_proc_last_status(PLACE_ID) == last_status
    assert (
        sql_get_place_assortment_last_status_history(PLACE_ID)
        == expected_last_statuses
    )

    assert get_sql_item_origin_ids(pgsql) == get_item_origin_ids(
        data_to_upload,
    )

    prev_data = copy.deepcopy(data_to_upload)
    data_to_upload['items'] = data_to_upload['items'][:-1]

    now += dt.timedelta(minutes=assortment_enrichment_timeout + 1)
    mocked_time.set(now)

    await brand_task_enqueue(
        '3', brand_nomenclature=data_to_upload, expect_fail=True,
    )

    assert task_testpoint.times_called == 1
    assert get_sql_item_origin_ids(pgsql) == get_item_origin_ids(prev_data)

    last_status = {
        'assortment_id': None,
        'status': 'failed',
        'task_error': PARTNER_ASSORTMENT_DESTRUCTIVE_ERROR_TYPE,
        'task_error_details': ASSORTMENT_DESTRUCTIVE_ERROR_DETAILS_2,
        'task_warnings': None,
        'status_or_text_changed_at': now.replace(tzinfo=pytz.UTC),
    }
    expected_last_statuses.append(last_status)
    assert sql_get_place_assortment_proc_last_status(PLACE_ID) == last_status
    assert (
        sql_get_place_assortment_last_status_history(PLACE_ID)
        == expected_last_statuses
    )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.config(EATS_NOMENCLATURE_VERIFICATION=settings(1))
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
@pytest.mark.parametrize(**utils.gen_bool_params('set_default_assortment'))
async def test_remove_too_much_in_non_partner_assortment(
        pgsql,
        taxi_config,
        mocked_time,
        activate_assortment,
        brand_task_enqueue,
        sql_get_place_assortment_proc_last_status,
        testpoint,
        # parametrize,
        set_default_assortment,
):
    @testpoint('assortment-is-potentially-destructive')
    def task_testpoint(param):
        pass

    setup_default_custom_assortment(pgsql, set_default_assortment)

    assortment_enrichment_timeout = 40
    set_enrichment_timeout(taxi_config, assortment_enrichment_timeout)
    now = mocked_time.now()

    data_to_upload = get_upload_data()

    await brand_task_enqueue('1', brand_nomenclature=data_to_upload)
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
        new_availabilities, new_stocks, new_prices, PLACE_ID, '1', TRAIT_ID,
    )

    # make custom assortment full custom so that it will be empty
    # to emulate custom assortment reduction
    make_trait_full_custom(TRAIT_ID, pgsql)

    now += dt.timedelta(minutes=assortment_enrichment_timeout + 1)
    mocked_time.set(now)

    await brand_task_enqueue(
        '2', brand_nomenclature=data_to_upload, expect_fail=False,
    )
    await activate_assortment(
        new_availabilities,
        new_stocks,
        new_prices,
        PLACE_ID,
        '1',
        TRAIT_ID,
        expect_partner_fail=False,
        expect_custom_fail=True,
    )

    assert task_testpoint.times_called == 1
    assert (
        sql_get_place_assortment_proc_last_status(PLACE_ID, TRAIT_ID)[
            'task_error'
        ]
        == DEFAULT_ASSORTMENT_DESTRUCTIVE_ERROR_TYPE
        if set_default_assortment
        else NON_DEFAULT_ASSORTMENT_DESTRUCTIVE_ERROR_TYPE
    )


def setup_default_custom_assortment(pgsql, set_default):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        INSERT INTO eats_nomenclature.assortment_traits
        (brand_id, assortment_name)
        VALUES ({BRAND_ID}, 'assortment_name_1');
        """,
    )
    if set_default:
        cursor.execute(
            f"""
            INSERT INTO eats_nomenclature.place_default_assortments
            (place_id, trait_id)
            VALUES ({PLACE_ID}, 1);
            """,
        )


def make_trait_full_custom(trait_id, pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        UPDATE eats_nomenclature.assortment_traits
        SET is_full_custom = true
        where id = {trait_id};
        """,
    )


def get_sql_item_origin_ids(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        SELECT p.origin_id
        FROM eats_nomenclature.place_assortments pa
          JOIN eats_nomenclature.categories_products cp
            on cp.assortment_id = pa.assortment_id
          JOIN eats_nomenclature.products p
            on p.id = cp.product_id
          JOIN eats_nomenclature.places_products pp
            on pp.product_id = p.id
        """,
    )
    return {i[0] for i in cursor}


def get_item_origin_ids(upload_data):
    return {c['origin_id'] for c in upload_data['items']}


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
