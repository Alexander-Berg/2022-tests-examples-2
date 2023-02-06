import datetime as dt

import pytest
import pytz

S3_AVAILABILITY_PATH = 'availability/availability_1.json'
S3_STOCKS_PATH = 'stocks/stocks_1.json'
S3_PRICES_PATH = 'prices/prices_1.json'
TEST_DATETIME = '2021-03-01T10:45:00+03:00'
MOCK_NOW = dt.datetime(2021, 8, 13, 12, tzinfo=pytz.UTC)

BRAND_ID = 777

PRICE_TASK_TYPE = 'price'
STOCK_TASK_TYPE = 'stock'
AVAILABILITY_TASK_TYPE = 'availability'

UNAVAILABLE_PRODUCTS_ERROR_TYPE = (
    'New assortment has too much unavailable products'
)
UNAVAILABLE_PRODUCTS_ERROR_DETAILS = (
    '50% of products in new assortment are unavailable'
)
ZERO_PRICES_ERROR_TYPE = (
    'New assortment has too much products with zero prices'
)
ZERO_PRICES_ERROR_DETAILS = (
    '50% of products in new assortment have zero prices'
)
ZERO_STOCKS_ERROR_TYPE = (
    'New assortment has too much products with zero stocks'
)
ZERO_STOCKS_ERROR_DETAILS = (
    '50% of products in new assortment have zero stocks'
)
NO_IMAGES_ERROR_TYPE = 'New assortment has too much products without images'
NO_IMAGES_ERROR_DETAILS = '50% of products in new assortment have no images'
DB_ERROR_TYPE = 'DB error occurred while processing assortment'
DB_ERROR_DETAILS = (
    'Statement `some query`, network timeout error: injected error'
)


def settings():
    return {
        f'{BRAND_ID}': {
            'assortment_remove_limit_in_percent': 100,
            'unavailable_products_limit_in_percent': 50,
            'zero_stocks_limit_in_percent': 50,
            'zero_prices_limit_in_percent': 50,
            'products_without_images_limit_in_percent': 50,
        },
    }


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.config(EATS_NOMENCLATURE_VERIFICATION=settings())
@pytest.mark.parametrize(
    'should_fail, fail_reason, error_type, error_details',
    [
        pytest.param(
            True,
            'unavailable_products',
            UNAVAILABLE_PRODUCTS_ERROR_TYPE,
            UNAVAILABLE_PRODUCTS_ERROR_DETAILS,
            id='unavailable_products',
        ),
        pytest.param(
            True,
            'unavailable_products_with_stock_reset_limit',
            UNAVAILABLE_PRODUCTS_ERROR_TYPE,
            UNAVAILABLE_PRODUCTS_ERROR_DETAILS,
            id='unavailable_products_with_stock_reset_limit',
        ),
        pytest.param(
            True,
            'zero_prices',
            ZERO_PRICES_ERROR_TYPE,
            ZERO_PRICES_ERROR_DETAILS,
            id='zero_prices',
        ),
        pytest.param(
            True,
            'zero_stocks',
            ZERO_STOCKS_ERROR_TYPE,
            ZERO_STOCKS_ERROR_DETAILS,
            id='zero_stocks',
        ),
        pytest.param(
            True,
            'no_images',
            NO_IMAGES_ERROR_TYPE,
            NO_IMAGES_ERROR_DETAILS,
            id='no_images',
        ),
        pytest.param(
            True, 'db_error', DB_ERROR_TYPE, DB_ERROR_DETAILS, id='db_error',
        ),
        pytest.param(False, 'none', None, None, id='all_ok'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_assortment_verification(
        pgsql,
        pg_cursor,
        to_utc_datetime,
        load_json,
        upload_verified_nomenclature_to_s3,
        get_uploaded_file_path,
        put_availability_data_to_s3,
        availability_enqueue,
        put_stock_data_to_s3,
        stocks_enqueue,
        put_prices_data_to_s3,
        prices_enqueue,
        complete_enrichment_status,
        sql_get_place_processing_last_status,
        sql_get_place_processing_last_status_history,
        sql_get_place_assortment_proc_last_status,
        sql_get_place_assortment_last_status_history,
        sql_set_place_assortment_proc_last_status,
        stq_runner,
        testpoint,
        # parametrize params
        should_fail,
        fail_reason,
        error_type,
        error_details,
):
    place_id = 1
    task_types = [PRICE_TASK_TYPE, STOCK_TASK_TYPE, AVAILABILITY_TASK_TYPE]

    old_status_or_text_changed_at = '2020-01-01T00:45:00+00:00'
    status = 'processed'
    cursor = pgsql['eats_nomenclature'].cursor()
    custom_trait_id = 1
    old_assortment_id = 1
    sql_set_place_assortment_proc_last_status(
        place_id,
        old_assortment_id,
        custom_trait_id,
        status,
        old_status_or_text_changed_at,
    )

    expected_place_proc_statuses = {}
    for task_type in task_types:
        last_status = {
            'status': 'processed',
            'task_error': None,
            'task_error_details': None,
            'task_warnings': None,
            'status_or_text_changed_at': to_utc_datetime(
                old_status_or_text_changed_at,
            ),
        }

        cursor.execute(
            f"""
            insert into eats_nomenclature.places_processing_last_status_v2(
                place_id, task_type, status, status_or_text_changed_at
            ) values
            (
                {place_id},
                '{task_type}',
                'processed',
                '{old_status_or_text_changed_at}'
            )
            """,
        )
        cursor.execute(
            f"""
            insert into
            eats_nomenclature.places_processing_last_status_v2_history(
                place_id, task_type, status, status_or_text_changed_at
            ) values
            (
                {place_id},
                '{task_type}',
                'processed',
                '{old_status_or_text_changed_at}'
            )
            """,
        )

        expected_place_proc_statuses[task_type] = [last_status]

    db_failed = fail_reason == 'db_error'

    @testpoint('eats-nomenclature::simulate-db-timeout')
    def failed_on_db_timeout(param):
        return {'inject_failure': db_failed}

    @testpoint('eats-nomenclature_only-zero-stocks-products')
    def failed_on_zero_stocks(param):
        pass

    @testpoint('eats-nomenclature_no-available-products')
    def failed_on_unavailable_products(param):
        pass

    @testpoint('eats-nomenclature_only-zero-price-products')
    def failed_on_zero_prices(param):
        pass

    @testpoint('eats-nomenclature_only-products-without-images')
    def failed_on_no_images(param):
        pass

    brand_nomenclature = load_json('request.json')
    if fail_reason == 'no_images':
        brand_nomenclature['items'][0]['images'] = []

    new_availabilities = [
        {'origin_id': 'item_id_1', 'available': True},
        {'origin_id': 'item_id_2', 'available': True},
    ]
    if fail_reason == 'unavailable_products':
        new_availabilities[0]['available'] = False

    new_stocks = [
        {'origin_id': 'item_id_1', 'stocks': '10'},
        {'origin_id': 'item_id_2', 'stocks': '20'},
    ]
    if fail_reason == 'zero_stocks':
        new_stocks[0]['stocks'] = '0'
    if fail_reason == 'unavailable_products_with_stock_reset_limit':
        new_stock_value = 5
        new_stocks[0]['stocks'] = str(new_stock_value)
        _sql_set_place_stock_limit(pg_cursor, place_id, new_stock_value * 2)

    new_prices = [
        {'origin_id': 'item_id_1', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_id_2', 'price': '1000', 'currency': 'RUB'},
    ]
    if fail_reason == 'zero_prices':
        new_prices[0]['price'] = '0'

    await upload_verified_nomenclature_to_s3(
        brand_nomenclature=brand_nomenclature,
    )
    s3_file_path = get_uploaded_file_path(place_id)
    # Update only partner assortment (with tarit_id = null)
    await stq_runner.eats_nomenclature_transform_assortment.call(
        task_id='test_task',
        args=[],
        kwargs={'assortment_s3_url': s3_file_path, 'brand_id': BRAND_ID},
        expect_fail=db_failed,
    )
    complete_enrichment_status(
        place_id, {'availabilities': False, 'stocks': False, 'prices': False},
    )
    await put_availability_data_to_s3(
        new_availabilities, S3_AVAILABILITY_PATH, str(place_id),
    )
    await availability_enqueue(
        place_id,
        S3_AVAILABILITY_PATH,
        TEST_DATETIME,
        '1',
        expect_fail=db_failed,
    )
    await put_stock_data_to_s3(new_stocks, S3_STOCKS_PATH, str(place_id))
    await stocks_enqueue(
        place_id, S3_STOCKS_PATH, TEST_DATETIME, '1', expect_fail=db_failed,
    )
    await put_prices_data_to_s3(new_prices, S3_PRICES_PATH, str(place_id))
    await prices_enqueue(
        place_id, S3_PRICES_PATH, TEST_DATETIME, '1', expect_fail=db_failed,
    )

    assert failed_on_unavailable_products.has_calls == (
        fail_reason
        in {
            'unavailable_products',
            'unavailable_products_with_stock_reset_limit',
        }
    )
    assert failed_on_zero_prices.has_calls == (fail_reason == 'zero_prices')
    assert failed_on_zero_stocks.has_calls == (fail_reason == 'zero_stocks')
    assert failed_on_no_images.has_calls == (fail_reason == 'no_images')
    if db_failed:
        assert failed_on_db_timeout.has_calls

    new_assortment_id = 4
    custom_assortment_status_old = {
        'assortment_id': old_assortment_id,
        'status': 'processed',
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': to_utc_datetime(
            old_status_or_text_changed_at,
        ),
    }

    if not should_fail:
        for task_type in task_types:
            assert (
                sql_get_place_processing_last_status(place_id, task_type)
                == {
                    'status': 'processed',
                    'task_error': None,
                    'task_error_details': None,
                    'task_warnings': None,
                    'status_or_text_changed_at': to_utc_datetime(
                        old_status_or_text_changed_at,
                    ),
                }
            )
            assert (
                sql_get_place_processing_last_status_history(
                    place_id, task_type,
                )
                == expected_place_proc_statuses[task_type]
            )
        default_assortment_last_status = {
            'assortment_id': new_assortment_id,
            'status': 'processed',
            'task_error': None,
            'task_error_details': None,
            'task_warnings': None,
            'status_or_text_changed_at': MOCK_NOW,
        }
        assert (
            sql_get_place_assortment_proc_last_status(place_id)
            == default_assortment_last_status
        )
        assert sql_get_place_assortment_last_status_history(place_id) == [
            default_assortment_last_status,
        ]

        assert (
            sql_get_place_assortment_proc_last_status(
                place_id, custom_trait_id,
            )
            == custom_assortment_status_old
        )
        assert sql_get_place_assortment_last_status_history(
            place_id, custom_trait_id,
        ) == [custom_assortment_status_old]

    elif db_failed:
        for task_type in task_types:
            last_status = {
                'status': 'failed',
                'task_error': error_type,
                'task_error_details': error_details,
                'task_warnings': None,
                'status_or_text_changed_at': MOCK_NOW,
            }
            expected_place_proc_statuses[task_type].append(last_status)
            assert (
                sql_get_place_processing_last_status(place_id, task_type)
                == last_status
            )

            assert (
                sql_get_place_processing_last_status_history(
                    place_id, task_type,
                )
                == expected_place_proc_statuses[task_type]
            )
        default_assortment_last_status = {
            'assortment_id': new_assortment_id,
            'status': 'failed',
            'task_error': error_type,
            'task_error_details': error_details,
            'task_warnings': None,
            'status_or_text_changed_at': MOCK_NOW,
        }
        assert (
            sql_get_place_assortment_proc_last_status(place_id)
            == default_assortment_last_status
        )
        assert sql_get_place_assortment_last_status_history(place_id) == [
            default_assortment_last_status,
        ]
    else:
        assert (
            sql_get_place_assortment_proc_last_status(
                place_id, custom_trait_id,
            )
            == custom_assortment_status_old
        )
        assert sql_get_place_assortment_last_status_history(
            place_id, custom_trait_id,
        ) == [custom_assortment_status_old]

        default_assortment_last_status = {
            'status': 'failed',
            'assortment_id': new_assortment_id,
            'task_error': error_type,
            'task_error_details': error_details,
            'task_warnings': None,
            'status_or_text_changed_at': MOCK_NOW,
        }
        assert (
            sql_get_place_assortment_proc_last_status(place_id, None)
            == default_assortment_last_status
        )
        assert sql_get_place_assortment_last_status_history(
            place_id, None,
        ) == [default_assortment_last_status]


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.config(EATS_NOMENCLATURE_VERIFICATION=settings())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_merge_last_status(
        load_json,
        upload_verified_nomenclature_to_s3,
        get_uploaded_file_path,
        put_availability_data_to_s3,
        availability_enqueue,
        put_prices_data_to_s3,
        put_stock_data_to_s3,
        prices_enqueue,
        complete_enrichment_status,
        sql_set_place_assortment_proc_last_status,
        sql_get_place_assortment_proc_last_status,
        sql_get_place_assortment_last_status_history,
        mocked_time,
        to_utc_datetime,
        stocks_enqueue,
        stq_runner,
):
    place_id = 1
    now = mocked_time.now()
    brand_nomenclature = load_json('request.json')

    async def update_brand_nomenclature():
        await upload_verified_nomenclature_to_s3(
            brand_nomenclature=brand_nomenclature,
        )
        s3_file_path = get_uploaded_file_path(place_id)
        await stq_runner.eats_nomenclature_transform_assortment.call(
            task_id='test_task',
            args=[],
            kwargs={'assortment_s3_url': s3_file_path, 'brand_id': BRAND_ID},
        )
        complete_enrichment_status(
            place_id, {'availabilities': False, 'prices': False},
        )

    async def update_prices(should_set_zero_price):
        new_prices = [
            {'origin_id': 'item_id_1', 'price': '1000', 'currency': 'RUB'},
            {'origin_id': 'item_id_2', 'price': '1000', 'currency': 'RUB'},
        ]
        if should_set_zero_price:
            new_prices[0]['price'] = '0'
        await put_prices_data_to_s3(new_prices, S3_PRICES_PATH, str(place_id))
        await prices_enqueue(place_id, S3_PRICES_PATH, TEST_DATETIME, '1')

    async def update_availability_and_stocks(should_reset_availability):
        new_availabilities = [
            {'origin_id': 'item_id_1', 'available': True},
            {'origin_id': 'item_id_2', 'available': True},
        ]
        new_stocks = [
            {'origin_id': 'item_id_1', 'stocks': None},
            {'origin_id': 'item_id_2', 'stocks': None},
        ]
        if should_reset_availability:
            new_availabilities[0]['available'] = False
        await put_availability_data_to_s3(
            new_availabilities, S3_AVAILABILITY_PATH, str(place_id),
        )
        await availability_enqueue(
            place_id, S3_AVAILABILITY_PATH, TEST_DATETIME, '1',
        )
        await put_stock_data_to_s3(new_stocks, S3_STOCKS_PATH, str(place_id))
        await stocks_enqueue(place_id, S3_STOCKS_PATH, TEST_DATETIME, '1')

    old_status_or_text_changed_at = '2020-01-01T00:45:00+00:00'
    custom_trait_id = 1
    status = 'processed'
    old_assortment_id = 1
    sql_set_place_assortment_proc_last_status(
        place_id,
        old_assortment_id,
        custom_trait_id,
        status,
        old_status_or_text_changed_at,
    )
    sql_set_place_assortment_proc_last_status(
        place_id,
        old_assortment_id,
        None,
        status,
        old_status_or_text_changed_at,
    )
    last_status_old = {
        'status': 'processed',
        'assortment_id': old_assortment_id,
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': to_utc_datetime(
            old_status_or_text_changed_at,
        ),
    }

    # leave processed status, but another assortment
    await update_brand_nomenclature()
    await update_availability_and_stocks(should_reset_availability=False)
    await update_prices(should_set_zero_price=False)

    new_assortment_id = 4
    last_status_new = {
        'status': 'processed',
        'assortment_id': new_assortment_id,
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': now.replace(tzinfo=pytz.UTC),
    }
    default_assortment_statuses = [last_status_old, last_status_new]
    assert (
        sql_get_place_assortment_proc_last_status(place_id, None)
        == last_status_new
    )
    assert (
        sql_get_place_assortment_last_status_history(place_id, None)
        == default_assortment_statuses
    )
    assert (
        sql_get_place_assortment_proc_last_status(place_id, custom_trait_id)
        == last_status_old
    )
    assert sql_get_place_assortment_last_status_history(
        place_id, custom_trait_id,
    ) == [last_status_old]

    now += dt.timedelta(minutes=5)
    mocked_time.set(now)

    # change to failed status
    await update_brand_nomenclature()
    await update_prices(should_set_zero_price=True)
    await update_availability_and_stocks(should_reset_availability=False)
    # Only partner assortment (trait_id = null) was updated

    new_assortment_id = 5
    default_assortment_last_status = {
        'assortment_id': new_assortment_id,
        'status': 'failed',
        'task_error': ZERO_PRICES_ERROR_TYPE,
        'task_error_details': ZERO_PRICES_ERROR_DETAILS,
        'task_warnings': None,
        'status_or_text_changed_at': now.replace(tzinfo=pytz.UTC),
    }
    assert (
        sql_get_place_assortment_proc_last_status(place_id)
        == default_assortment_last_status
    )
    default_assortment_statuses.append(default_assortment_last_status)
    assert (
        sql_get_place_assortment_proc_last_status(place_id)
        == default_assortment_last_status
    )
    assert (
        sql_get_place_assortment_last_status_history(place_id)
        == default_assortment_statuses
    )

    assert (
        sql_get_place_assortment_proc_last_status(place_id, custom_trait_id)
        == last_status_old
    )

    assert sql_get_place_assortment_last_status_history(
        place_id, custom_trait_id,
    ) == [last_status_old]

    now += dt.timedelta(minutes=5)
    mocked_time.set(now)

    # change task error
    await update_brand_nomenclature()
    await update_prices(should_set_zero_price=False)
    await update_availability_and_stocks(should_reset_availability=True)
    # Only partner assortment (trait_id = null) was updated
    default_assortment_last_status = {
        'assortment_id': new_assortment_id,
        'status': 'failed',
        'task_error': UNAVAILABLE_PRODUCTS_ERROR_TYPE,
        'task_error_details': UNAVAILABLE_PRODUCTS_ERROR_DETAILS,
        'task_warnings': None,
        'status_or_text_changed_at': now.replace(tzinfo=pytz.UTC),
    }
    default_assortment_statuses.append(default_assortment_last_status)
    assert (
        sql_get_place_assortment_proc_last_status(place_id)
        == default_assortment_last_status
    )
    assert (
        sql_get_place_assortment_last_status_history(place_id)
        == default_assortment_statuses
    )

    assert (
        sql_get_place_assortment_proc_last_status(place_id, custom_trait_id)
        == last_status_old
    )

    assert sql_get_place_assortment_last_status_history(
        place_id, custom_trait_id,
    ) == [last_status_old]

    now += dt.timedelta(minutes=5)
    mocked_time.set(now)

    # leave same error
    await update_brand_nomenclature()
    await update_prices(should_set_zero_price=True)
    await update_availability_and_stocks(should_reset_availability=True)

    assert (
        sql_get_place_assortment_proc_last_status(place_id)
        == default_assortment_last_status
    )
    assert (
        sql_get_place_assortment_last_status_history(place_id)
        == default_assortment_statuses
    )

    assert (
        sql_get_place_assortment_proc_last_status(place_id, custom_trait_id)
        == last_status_old
    )

    assert sql_get_place_assortment_last_status_history(
        place_id, custom_trait_id,
    ) == [last_status_old]

    now += dt.timedelta(minutes=5)
    mocked_time.set(now)

    # change to processed status
    await update_brand_nomenclature()
    await update_prices(should_set_zero_price=False)
    await update_availability_and_stocks(should_reset_availability=False)

    default_assortment_last_status = {
        'assortment_id': new_assortment_id,
        'status': 'processed',
        'task_error': None,
        'task_error_details': None,
        'task_warnings': None,
        'status_or_text_changed_at': now.replace(tzinfo=pytz.UTC),
    }
    default_assortment_statuses.append(default_assortment_last_status)
    assert (
        sql_get_place_assortment_proc_last_status(place_id)
        == default_assortment_last_status
    )
    assert (
        sql_get_place_assortment_last_status_history(place_id)
        == default_assortment_statuses
    )


def _sql_set_place_stock_limit(pg_cursor, place_id, stock_reset_limit):
    pg_cursor.execute(
        """
        update eats_nomenclature.places
        set stock_reset_limit = %s
        where id = %s
        """,
        (stock_reset_limit, place_id),
    )
