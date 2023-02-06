# pylint: disable=import-error
import base64
import datetime as dt

from arc_market.idx.datacamp.proto.api import ExportMessage_pb2
from google.protobuf import json_format
import pytest
import pytz


MOCK_NOW = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)
PERIODIC_NAME = 'market-yt-full-place-products-sync-periodic'
QUEUE_NAME = 'eats_nomenclature_market_yt_full_place_products_sync'


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
    'brand_ids_black_list,business_ids_black_list', [([], []), ([777], [10])],
)
@pytest.mark.parametrize('stocks_reset_limit', [0, 1, 5])
@pytest.mark.config(
    EATS_NOMENCLATURE_MARKET_YT_FULL_PLACE_PRODUCTS_SYNC={
        'lookup_batch_size': 2,
    },
)
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_products.sql',
        'fill_categories_multiple_place_products.sql',
        'fill_additional_place_data.sql',
    ],
)
async def test_full_place_products_sync(
        pg_realdict_cursor,
        stq,
        stq_call_forward,
        taxi_eats_nomenclature,
        testpoint,
        update_taxi_config,
        # parametrize params
        stocks_reset_limit,
        brand_ids_black_list,
        business_ids_black_list,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_PERIODICS',
        {PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 60}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_EXPORT_TO_MARKET_BRANDS_BLACK_LIST',
        {'brand_ids': brand_ids_black_list},
    )

    place_id_with_stock_limit = '1'
    offer_id_with_stock_limit = '00000000-0000-0000-0000-000000000010'
    logged_data = []

    @testpoint('yt-logger-market-place-product')
    def yt_logger(row):
        decoded_data = base64.b64decode(row['data'])
        export_message = ExportMessage_pb2.ExportMessage()
        export_message.ParseFromString(decoded_data)
        message_dict = json_format.MessageToDict(
            export_message, use_integers_for_enums=False,
        )
        row['data'] = message_dict
        logged_data.append(row)

    _sql_set_place_stock_limit(
        pg_realdict_cursor, place_id_with_stock_limit, stocks_reset_limit,
    )
    market_brand_places = _sql_get_market_brand_places(pg_realdict_cursor)
    if brand_ids_black_list:
        market_brand_places = _filter_market_brand_places(
            market_brand_places, brand_ids_black_list,
        )

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    assert (
        stq.eats_nomenclature_market_yt_full_place_products_sync.times_called
        == len(market_brand_places)
    )
    requested_places = set()
    for _ in range(len(market_brand_places)):
        task_info = (
            stq.eats_nomenclature_market_yt_full_place_products_sync.next_call()  # noqa: E501
        )
        requested_places.add(task_info['kwargs']['place_id'])
        await stq_call_forward(task_info)
    assert requested_places == set(
        str(row['place_id']) for row in market_brand_places
    )

    assert yt_logger.has_calls

    expected_data = _get_expected_yt_logger_data()
    if business_ids_black_list:
        expected_data = _filter_expected_data(
            expected_data, business_ids_black_list,
        )

    _apply_limit_to_logged_data(
        expected_data, offer_id_with_stock_limit, stocks_reset_limit,
    )
    assert _sort_logged_data(logged_data) == _sort_logged_data(expected_data)


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_error=2),
)
@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_one_place_product.sql',
        'fill_categories_one_place_product.sql',
    ],
)
async def test_stq_error_limit(taxi_config, task_enqueue_v2, testpoint):
    @testpoint('yt-logger-market-place-product-injected-error')
    def task_testpoint(param):
        return {'inject_failure': True}

    place_id = '1'
    task_id = '1'
    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']

    for i in range(max_retries_on_error):
        await task_enqueue_v2(
            QUEUE_NAME,
            task_id=task_id,
            kwargs={'place_id': place_id},
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await task_enqueue_v2(
        QUEUE_NAME,
        task_id=task_id,
        kwargs={'place_id': place_id},
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_products.sql',
        'fill_categories_multiple_place_products.sql',
    ],
)
async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _sql_set_place_stock_limit(pg_cursor, place_id, stock_reset_limit):
    pg_cursor.execute(
        """
        update eats_nomenclature.places
        set stock_reset_limit = %s
        where id = %s
        """,
        (stock_reset_limit, place_id),
    )


def _sql_get_market_brand_places(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        f"""
        select
            brand_id,
            place_id,
            business_id,
            partner_id,
            feed_id
        from eats_nomenclature.market_brand_places
        """,
    )
    return pg_realdict_cursor.fetchall()


def _apply_limit_to_logged_data(data, offer_id, stocks_reset_limit):
    for elem in data:
        if elem['offer_id'] == offer_id and stocks_reset_limit > 3:
            # this offer has stock value equal to 3,
            # so it should be disabled when stocks_reset_limit is above
            elem['data']['offer']['shopStatuses'][0]['disableStatus'][3][
                'flag'
            ] = True


def _sort_logged_data(data):
    for i, _ in enumerate(data):
        if 'navigationPaths' in data[i]['data']['offer']:
            data[i]['data']['offer']['navigationPaths'].sort(
                key=lambda item: item['nodes'][0]['id'],
            )
    return sorted(data, key=lambda item: item['offer_id'])


def _filter_market_brand_places(market_brand_places, brand_ids_black_list):
    return list(
        filter(
            lambda market_brand_place: market_brand_place['brand_id']
            not in brand_ids_black_list,
            market_brand_places,
        ),
    )


def _filter_expected_data(expected_data, business_ids_black_list):
    return list(
        filter(
            lambda expected_data_item: expected_data_item['business_id']
            not in business_ids_black_list,
            expected_data,
        ),
    )


def _get_expected_yt_logger_data():
    return [
        {
            # place_id = 1, assortment_id = 1
            'business_id': 10,
            'offer_id': '11111111-1111-1111-1111-111111111111',
            'shop_id': 20,
            'feed_id': 30,
            'data': {
                'offer': {
                    'businessId': 10,
                    'offerId': '11111111-1111-1111-1111-111111111111',
                    'originalSku': 'item_origin_1',
                    'shopId': 20,
                    'feedId': 30,
                    'navigationPaths': [
                        {'nodes': [{'id': 1, 'name': 'category_1'}]},
                    ],
                    'shopPrices': [
                        {
                            'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                            'shopId': 20,
                            'price': {'currency': 'RUR', 'price': '0'},
                            'vat': 'NO_VAT',
                        },
                    ],
                    'shopStatuses': [
                        {
                            'shopId': 20,
                            'disableStatus': {
                                3: {
                                    'meta': {
                                        'timestamp': '2021-03-02T12:00:00Z',
                                    },
                                    'flag': True,
                                },
                            },
                        },
                    ],
                },
            },
            'is_delete': False,
        },
        {
            # place_id = 5, assortment_id = 4
            'business_id': 10,
            'offer_id': '11111111-1111-1111-1111-111111111111',
            'shop_id': 100,
            'feed_id': 120,
            'data': {
                'offer': {
                    'businessId': 10,
                    'offerId': '11111111-1111-1111-1111-111111111111',
                    'originalSku': 'item_origin_1',
                    'shopId': 100,
                    'feedId': 120,
                    'navigationPaths': [
                        {'nodes': [{'id': 1, 'name': 'category_1'}]},
                    ],
                    'shopPrices': [
                        {
                            'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                            'shopId': 100,
                            'price': {'currency': 'RUR', 'price': '0'},
                            'vat': 'NO_VAT',
                        },
                    ],
                    'shopStatuses': [
                        {
                            'shopId': 100,
                            'disableStatus': {
                                3: {
                                    'meta': {
                                        'timestamp': '2021-03-02T12:00:00Z',
                                    },
                                    'flag': True,
                                },
                            },
                        },
                    ],
                },
            },
            'is_delete': False,
        },
        {
            # place_id = 6, assortment_id = 6
            'business_id': 70,
            'offer_id': '22222222-2222-2222-2222-222222222222',
            'shop_id': 130,
            'feed_id': 150,
            'data': {
                'offer': {
                    'businessId': 70,
                    'offerId': '22222222-2222-2222-2222-222222222222',
                    'originalSku': 'item_origin_2',
                    'shopId': 130,
                    'feedId': 150,
                    'navigationPaths': [
                        {'nodes': [{'id': 2, 'name': 'category_2'}]},
                    ],
                    'shopPrices': [
                        {
                            'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                            'shopId': 130,
                            'price': {
                                'currency': 'RUR',
                                'price': '9990000000',
                                'oldPrice': '100000000',
                            },
                            'vat': 'VAT_10',
                        },
                    ],
                    'shopStatuses': [
                        {
                            'shopId': 130,
                            'disableStatus': {
                                3: {
                                    'meta': {
                                        'timestamp': '2021-03-02T12:00:00Z',
                                    },
                                    'flag': True,
                                },
                            },
                        },
                    ],
                },
            },
            'is_delete': False,
        },
        {
            # place_id = 1, assortment_id = 1
            'business_id': 10,
            'offer_id': '22222222-2222-2222-2222-222222222222',
            'shop_id': 20,
            'feed_id': 30,
            'data': {
                'offer': {
                    'businessId': 10,
                    'offerId': '22222222-2222-2222-2222-222222222222',
                    'originalSku': 'item_origin_2',
                    'shopId': 20,
                    'feedId': 30,
                    'navigationPaths': [
                        {'nodes': [{'id': 1, 'name': 'category_1'}]},
                        {
                            'nodes': [
                                {'id': 2, 'name': 'category_2'},
                                {'id': 3, 'name': 'category_3'},
                                {'id': 4, 'name': 'category_4'},
                            ],
                        },
                    ],
                    'shopPrices': [
                        {
                            'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                            'shopId': 20,
                            'price': {
                                'currency': 'RUR',
                                'price': '9990000000',
                                'oldPrice': '100000000',
                            },
                            'vat': 'VAT_10',
                        },
                    ],
                    'shopStatuses': [
                        {
                            'shopId': 20,
                            'disableStatus': {
                                3: {
                                    'meta': {
                                        'timestamp': '2021-03-02T12:00:00Z',
                                    },
                                    'flag': True,
                                },
                            },
                        },
                    ],
                },
            },
            'is_delete': False,
        },
        {
            # place_id = 5, assortment_id = 4
            'business_id': 10,
            'offer_id': '22222222-2222-2222-2222-222222222222',
            'shop_id': 100,
            'feed_id': 120,
            'data': {
                'offer': {
                    'businessId': 10,
                    'offerId': '22222222-2222-2222-2222-222222222222',
                    'originalSku': 'item_origin_2',
                    'shopId': 100,
                    'feedId': 120,
                    'navigationPaths': [
                        {'nodes': [{'id': 1, 'name': 'category_1'}]},
                        {
                            'nodes': [
                                {'id': 2, 'name': 'category_2'},
                                {'id': 3, 'name': 'category_3'},
                                {'id': 4, 'name': 'category_4'},
                            ],
                        },
                    ],
                    'shopPrices': [
                        {
                            'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                            'shopId': 100,
                            'price': {
                                'currency': 'RUR',
                                'price': '9990000000',
                                'oldPrice': '100000000',
                            },
                            'vat': 'VAT_10',
                        },
                    ],
                    'shopStatuses': [
                        {
                            'shopId': 100,
                            'disableStatus': {
                                3: {
                                    'meta': {
                                        'timestamp': '2021-03-02T12:00:00Z',
                                    },
                                    'flag': True,
                                },
                            },
                        },
                    ],
                },
            },
            'is_delete': False,
        },
        {
            # place_id = 1, assortment_id = 1
            'business_id': 10,
            'offer_id': '33333333-3333-3333-3333-333333333333',
            'shop_id': 20,
            'feed_id': 30,
            'data': {
                'offer': {
                    'businessId': 10,
                    'offerId': '33333333-3333-3333-3333-333333333333',
                    'originalSku': 'item_origin_3',
                    'shopId': 20,
                    'feedId': 30,
                    'navigationPaths': [
                        {
                            'nodes': [
                                {'id': 2, 'name': 'category_2'},
                                {'id': 3, 'name': 'category_3'},
                                {'id': 4, 'name': 'category_4'},
                            ],
                        },
                    ],
                    'shopPrices': [
                        {
                            'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                            'shopId': 20,
                            'price': {
                                'currency': 'RUR',
                                'price': '2000000000',
                                'oldPrice': '1500000000',
                            },
                            'vat': 'WRONG_VAT',
                        },
                    ],
                    'shopStatuses': [
                        {
                            'shopId': 20,
                            'disableStatus': {
                                3: {
                                    'meta': {
                                        'timestamp': '2021-03-02T12:00:00Z',
                                    },
                                    'flag': True,
                                },
                            },
                        },
                    ],
                },
            },
            'is_delete': False,
        },
        {
            # place_id = 5, assortment_id = 4
            'business_id': 10,
            'offer_id': '33333333-3333-3333-3333-333333333333',
            'shop_id': 100,
            'feed_id': 120,
            'data': {
                'offer': {
                    'businessId': 10,
                    'offerId': '33333333-3333-3333-3333-333333333333',
                    'originalSku': 'item_origin_3',
                    'shopId': 100,
                    'feedId': 120,
                    'navigationPaths': [
                        {
                            'nodes': [
                                {'id': 2, 'name': 'category_2'},
                                {'id': 3, 'name': 'category_3'},
                                {'id': 4, 'name': 'category_4'},
                            ],
                        },
                    ],
                    'shopPrices': [
                        {
                            'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                            'shopId': 100,
                            'price': {
                                'currency': 'RUR',
                                'price': '2000000000',
                                'oldPrice': '1500000000',
                            },
                            'vat': 'WRONG_VAT',
                        },
                    ],
                    'shopStatuses': [
                        {
                            'shopId': 100,
                            'disableStatus': {
                                3: {
                                    'meta': {
                                        'timestamp': '2021-03-02T12:00:00Z',
                                    },
                                    'flag': True,
                                },
                            },
                        },
                    ],
                },
            },
            'is_delete': False,
        },
        {
            'business_id': 10,
            'data': {
                'offer': {
                    'businessId': 10,
                    'feedId': 30,
                    'navigationPaths': [
                        {'nodes': [{'id': 1, 'name': 'category_1'}]},
                    ],
                    'offerId': '00000000-0000-0000-0000-000000000010',
                    'originalSku': 'item_for_stock_limit_test',
                    'shopId': 20,
                    'shopPrices': [
                        {
                            'meta': {'timestamp': '2021-03-02T12:00:00Z'},
                            'price': {
                                'currency': 'RUR',
                                'oldPrice': '1510000000',
                                'price': '2010000000',
                            },
                            'shopId': 20,
                            'vat': 'NO_VAT',
                        },
                    ],
                    'shopStatuses': [
                        {
                            'disableStatus': {
                                3: {
                                    'flag': False,
                                    'meta': {
                                        'timestamp': '2021-03-02T12:00:00Z',
                                    },
                                },
                            },
                            'shopId': 20,
                        },
                    ],
                },
            },
            'feed_id': 30,
            'is_delete': False,
            'offer_id': '00000000-0000-0000-0000-000000000010',
            'shop_id': 20,
        },
    ]
