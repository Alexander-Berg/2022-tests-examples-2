# pylint: disable=import-error
import base64
import datetime as dt

from arc_market.idx.datacamp.proto.api import ExportMessage_pb2
from google.protobuf import json_format
import pytest
import pytz


MOCK_NOW = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
PERIODIC_NAME = 'market-yt-products-sync-periodic'
QUEUE_NAME = 'eats_nomenclature_market_yt_products_sync'
BRAND_ID = 777
BRAND_ID_2 = 778
BUSINESS_ID = 10
BUSINESS_ID_2 = 70


def settings(
        max_retries_on_error=3,
        max_retries_on_busy=3,
        max_busy_time_in_ms=100000,
        retry_on_busy_delay_ms=1000,
):
    return {
        '__default__': {
            'max_retries_on_error': max_retries_on_error,
            'max_retries_on_busy': max_retries_on_busy,
            'max_busy_time_in_ms': max_busy_time_in_ms,
            'retry_on_busy_delay_ms': retry_on_busy_delay_ms,
            'insert_batch_size': 1000,
            'lookup_batch_size': 1000,
        },
    }


@pytest.mark.parametrize(
    'brand_ids_black_list,business_ids_black_list',
    [([], []), ([BRAND_ID], [BUSINESS_ID])],
)
@pytest.mark.parametrize('should_add_measure_in_name', [True, False])
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_products.sql'],
)
async def test_products_sync(
        pg_realdict_cursor,
        stq,
        stq_call_forward,
        taxi_eats_nomenclature,
        testpoint,
        update_taxi_config,
        # parametrize params
        brand_ids_black_list,
        business_ids_black_list,
        should_add_measure_in_name,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_PERIODICS',
        {PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 60}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_MARKET_YT_PRODUCTS_SYNC',
        {
            'sync_batch_size': 2,
            'brand_settings': {
                '__default__': {
                    'should_add_measure_in_name': True,
                    'barcodes_min_length': 6,
                },
                f'{BRAND_ID}': {
                    'should_add_measure_in_name': should_add_measure_in_name,
                },
                f'{BRAND_ID_2}': {
                    'should_add_measure_in_name': should_add_measure_in_name,
                },
            },
        },
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_EXPORT_TO_MARKET_BRANDS_BLACK_LIST',
        {'brand_ids': brand_ids_black_list},
    )

    logged_data = []

    @testpoint('yt-logger-market-product')
    def yt_logger(row):
        decoded_data = base64.b64decode(row['data'])
        export_message = ExportMessage_pb2.ExportMessage()
        export_message.ParseFromString(decoded_data)
        message_dict = json_format.MessageToDict(
            export_message, use_integers_for_enums=False,
        )
        row['data'] = message_dict
        logged_data.append(row)

    market_brands = [
        row['brand_id']
        for row in _sql_get_market_brands(pg_realdict_cursor)
        if row['brand_id'] not in brand_ids_black_list
    ]

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    assert stq.eats_nomenclature_market_yt_products_sync.times_called == len(
        market_brands,
    )
    requested_brands = set()
    for _ in range(len(market_brands)):
        task_info = stq.eats_nomenclature_market_yt_products_sync.next_call()
        requested_brands.add(task_info['kwargs']['brand_id'])
        await stq_call_forward(task_info)
    assert requested_brands == {str(brand_id) for brand_id in market_brands}

    assert yt_logger.has_calls
    logged_data = sorted(logged_data, key=lambda item: item['offer_id'])
    expected_data = sorted(
        _get_expected_yt_logger_data(should_add_measure_in_name),
        key=lambda item: item['offer_id'],
    )
    expected_data = [
        data
        for data in expected_data
        if data['business_id'] not in business_ids_black_list
    ]
    assert logged_data == expected_data


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_error=2),
)
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_one_place_product.sql'],
)
async def test_stq_error_limit(taxi_config, task_enqueue_v2, testpoint):
    @testpoint('yt-logger-market-product-injected-error')
    def task_testpoint(param):
        return {'inject_failure': True}

    task_id = f'{BRAND_ID}'
    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']

    for i in range(max_retries_on_error):
        await task_enqueue_v2(
            QUEUE_NAME,
            task_id=task_id,
            kwargs={'brand_id': f'{BRAND_ID}'},
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await task_enqueue_v2(
        QUEUE_NAME,
        task_id=task_id,
        kwargs={'brand_id': f'{BRAND_ID}'},
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_products.sql'],
)
async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _sql_get_market_brands(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        f"""
        select distinct brand_id
        from eats_nomenclature.market_brand_places
        """,
    )
    return pg_realdict_cursor.fetchall()


def _get_expected_yt_logger_data(should_add_measure_in_name):
    return [
        {
            'business_id': BUSINESS_ID,
            'offer_id': '11111111-1111-1111-1111-111111111111',
            'data': {
                'offer': {
                    'businessId': BUSINESS_ID,
                    'offerId': '11111111-1111-1111-1111-111111111111',
                    'originalPictures': [
                        {'url': 'processed_url_2', 'source': 'DIRECT_LINK'},
                        {'url': 'processed_url_1', 'source': 'DIRECT_LINK'},
                    ],
                    'originalContent': {
                        'shopVendor': 'vendor_1',
                        'description': 'abc',
                        'countryOfOrigin': ['country_1'],
                        'adult': False,
                        'bruttoWeightInGrams': '1000',
                        'name': 'Товар 1',
                        'ingredients': ['composition1'],
                    },
                    'originalSku': 'item_origin_1',
                    'timestamp': '2021-03-02T12:00:00Z',
                    'delivery': {'pickup': True, 'delivery': True},
                },
            },
        },
        {
            'business_id': BUSINESS_ID,
            'offer_id': '22222222-2222-2222-2222-222222222222',
            'data': {
                'offer': {
                    'businessId': BUSINESS_ID,
                    'offerId': '22222222-2222-2222-2222-222222222222',
                    'originalPictures': [
                        {'url': 'processed_url_1', 'source': 'DIRECT_LINK'},
                        {'url': 'processed_url_3', 'source': 'DIRECT_LINK'},
                    ],
                    'originalContent': {
                        'shopVendor': 'vendor_1',
                        'description': 'def',
                        'countryOfOrigin': ['country_1'],
                        'adult': True,
                        'bruttoWeightInGrams': '1000000',
                        'name': (
                            'Товар 2'
                            if not should_add_measure_in_name
                            else 'Товар 2, 1000 кг'
                        ),
                        'ingredients': ['composition2'],
                    },
                    'originalSku': 'item_origin_2',
                    'timestamp': '2021-03-02T12:00:00Z',
                    'delivery': {'delivery': True},
                },
            },
        },
        {
            'business_id': BUSINESS_ID,
            'offer_id': '33333333-3333-3333-3333-333333333333',
            'data': {
                'offer': {
                    'businessId': BUSINESS_ID,
                    'offerId': '33333333-3333-3333-3333-333333333333',
                    'originalPictures': [
                        {'url': 'processed_url_2', 'source': 'DIRECT_LINK'},
                    ],
                    'originalContent': {
                        'shopVendor': 'vendor_2',
                        'description': 'ghi',
                        'countryOfOrigin': ['country_2'],
                        'adult': False,
                        'barcode': ['999UUU', '123ETR456'],
                        'name': 'Товар 3',
                    },
                    'originalSku': 'item_origin_3',
                    'timestamp': '2021-03-02T12:00:00Z',
                    'delivery': {'delivery': True},
                },
            },
        },
        {
            'business_id': BUSINESS_ID,
            'offer_id': '44444444-4444-4444-4444-444444444444',
            'data': {
                'offer': {
                    'businessId': BUSINESS_ID,
                    'offerId': '44444444-4444-4444-4444-444444444444',
                    'originalContent': {
                        'shopVendor': 'vendor_2',
                        'description': 'jkl',
                        'countryOfOrigin': ['country_2'],
                        'adult': True,
                        'bruttoWeightInGrams': '50000',
                        'name': 'Товар 4',
                    },
                    'originalSku': 'item_origin_4',
                    'timestamp': '2021-03-02T12:00:00Z',
                    'delivery': {'pickup': True},
                },
            },
        },
        {
            'business_id': BUSINESS_ID,
            'offer_id': '55555555-5555-5555-5555-555555555555',
            'data': {
                'offer': {
                    'businessId': BUSINESS_ID,
                    'offerId': '55555555-5555-5555-5555-555555555555',
                    'originalContent': {
                        'shopVendor': 'vendor_3',
                        'description': 'mno',
                        'countryOfOrigin': ['country_3'],
                        'adult': True,
                        'bruttoWeightInGrams': '150',
                        'name': (
                            'Товар 5'
                            if not should_add_measure_in_name
                            else 'Товар 5, 150 мл'
                        ),
                    },
                    'originalSku': 'item_origin_5',
                    'timestamp': '2021-03-02T12:00:00Z',
                    'delivery': {'pickup': True},
                },
            },
        },
        {
            'business_id': BUSINESS_ID_2,
            'offer_id': '66666666-6666-6666-6666-666666666666',
            'data': {
                'offer': {
                    'businessId': BUSINESS_ID_2,
                    'offerId': '66666666-6666-6666-6666-666666666666',
                    'originalContent': {
                        'shopVendor': 'vendor_3',
                        'description': 'pqr',
                        'countryOfOrigin': ['country_3'],
                        'adult': False,
                        'bruttoWeightInGrams': '1400',
                        'name': (
                            'Товар 6'
                            if not should_add_measure_in_name
                            else 'Товар 6, 1.4 л'
                        ),
                    },
                    'originalSku': 'item_origin_6',
                    'timestamp': '2021-03-02T12:00:00Z',
                    'delivery': {'pickup': True},
                },
            },
        },
        {
            'business_id': BUSINESS_ID_2,
            'offer_id': '77777777-7777-7777-7777-777777777777',
            'data': {
                'offer': {
                    'businessId': BUSINESS_ID_2,
                    'offerId': '77777777-7777-7777-7777-777777777777',
                    'originalContent': {
                        'shopVendor': 'vendor_3',
                        'description': 'stu',
                        'countryOfOrigin': ['country_3'],
                        'adult': False,
                        'bruttoWeightInGrams': '1000',
                        'name': 'Товар 7',
                    },
                    'originalSku': 'item_origin_7',
                    'timestamp': '2021-03-02T12:00:00Z',
                    'delivery': {'pickup': True},
                },
            },
        },
        {
            'business_id': BUSINESS_ID_2,
            'offer_id': '88888888-8888-8888-8888-888888888888',
            'data': {
                'offer': {
                    'businessId': BUSINESS_ID_2,
                    'offerId': '88888888-8888-8888-8888-888888888888',
                    'originalContent': {
                        'shopVendor': 'vendor_3',
                        'description': 'vwx',
                        'countryOfOrigin': ['country_3'],
                        'adult': False,
                        'bruttoWeightInGrams': '2600',
                        'name': 'Товар 8',
                    },
                    'originalSku': 'item_origin_8',
                    'timestamp': '2021-03-02T12:00:00Z',
                    'delivery': {'pickup': True},
                },
            },
        },
        {
            'business_id': BUSINESS_ID_2,
            'data': {
                'offer': {
                    'businessId': BUSINESS_ID_2,
                    'delivery': {'pickup': True},
                    'offerId': '99999999-9999-9999-9999-999999999999',
                    'originalContent': {
                        'adult': False,
                        'countryOfOrigin': ['country_3'],
                        'description': 'azaza',
                        'bruttoWeightInGrams': '2000',
                        'name': 'Товар 9',
                        'shopVendor': 'vendor_3',
                    },
                    'originalSku': 'item_with_no_category',
                    'timestamp': '2021-03-02T12:00:00Z',
                },
            },
            'offer_id': '99999999-9999-9999-9999-999999999999',
        },
        {
            'business_id': 70,
            'data': {
                'offer': {
                    'businessId': 70,
                    'delivery': {'pickup': True},
                    'offerId': '00000000-0000-0000-0000-000000000010',
                    'originalContent': {
                        'adult': False,
                        'bruttoWeightInGrams': '2000',
                        'countryOfOrigin': ['country_3'],
                        'description': 'azaza',
                        'name': 'item_10',
                        'shopVendor': 'vendor_3',
                    },
                    'originalSku': 'item_for_stock_limit_test',
                    'timestamp': '2021-03-02T12:00:00Z',
                },
            },
            'offer_id': '00000000-0000-0000-0000-000000000010',
        },
    ]
