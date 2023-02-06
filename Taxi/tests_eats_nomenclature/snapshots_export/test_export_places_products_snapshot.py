import pytest

import tests_eats_nomenclature.parametrize.pennies_in_price as pennies_utils


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


@pytest.mark.parametrize('should_include_pennies_in_price', [True, False])
@pytest.mark.parametrize('stocks_reset_limit', [0, 1, 5])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_products.sql'],
)
async def test_places_products_export(
        stq_runner,
        testpoint,
        taxi_config,
        pg_cursor,
        # parametrize
        stocks_reset_limit,
        should_include_pennies_in_price,
):
    brand_id_with_pennies = 778

    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_PRICE_ROUNDING': {
                '__default__': {'should_include_pennies_in_price': False},
                str(brand_id_with_pennies): {
                    'should_include_pennies_in_price': (
                        should_include_pennies_in_price
                    ),
                },
            },
        },
    )

    logged_data = []
    place_id_with_stock_limit = 1
    place_id_with_pennies = 4
    place_ids = [place_id_with_stock_limit, 2, 3, place_id_with_pennies]

    @testpoint('export-places-products-snapshot')
    def yt_logger(row):
        snapshot = {
            'place_id': row['place_id'],
            'product_id': row['product_id'],
            'stocks': row.get('stocks'),
            'price': row['price'],
            'old_price': row.get('old_price'),
            'vat': row.get('vat'),
        }
        logged_data.append(snapshot)

    _sql_set_place_stock_limit(
        pg_cursor, place_id_with_stock_limit, stocks_reset_limit,
    )

    for i, place_id in enumerate(place_ids):
        await put_task_into_stq(stq_runner, place_id=place_id, task_id=str(i))
        assert yt_logger.has_calls

    expected_data = _get_expected_data()
    for place_id in place_ids:
        if (
                should_include_pennies_in_price
                and place_id == place_id_with_pennies
        ):
            continue
        _apply_rounded_price(expected_data, place_id)
    _apply_stock_limit_to_data(
        expected_data, place_id_with_stock_limit, stocks_reset_limit,
    )

    assert _sorted_data(expected_data) == _sorted_data(logged_data)


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_error=2),
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_products.sql'],
)
async def test_stq_error_limit(taxi_config, stq_runner, testpoint):
    @testpoint('export-places-products-snapshot-injected-error')
    def task_testpoint(param):
        return {'inject_failure': True}

    place_id = 1
    task_id = '1'
    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']

    for i in range(max_retries_on_error):
        await put_task_into_stq(
            stq_runner,
            place_id=place_id,
            task_id=task_id,
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await put_task_into_stq(
        stq_runner,
        place_id=place_id,
        task_id=task_id,
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_products.sql'],
)
async def test_no_partner_assortment(stq_runner, testpoint):
    place_id_without_assortment = 5

    @testpoint('export-places-products-snapshot')
    def yt_logger():
        pass

    await put_task_into_stq(
        stq_runner,
        place_id=place_id_without_assortment,
        task_id=str(place_id_without_assortment),
    )
    assert not yt_logger.has_calls


async def put_task_into_stq(
        stq_runner, place_id, task_id='1', expect_fail=False, exec_tries=None,
):
    await stq_runner.eats_nomenclature_export_places_products_snapshot.call(
        task_id=task_id,
        args=[],
        kwargs={'place_id': place_id},
        expect_fail=expect_fail,
        exec_tries=exec_tries,
    )


def _get_expected_data():
    return [
        {
            'place_id': 1,
            'product_id': '11111111-1111-1111-1111-111111111111',
            'stocks': 0,
            'price': '0.000000',
            'old_price': None,
            'vat': None,
        },
        {
            'place_id': 1,
            'product_id': '22222222-2222-2222-2222-222222222222',
            'stocks': 20,
            'price': '999.000000',
            'old_price': '10.100000',
            'vat': 10,
        },
        {
            'place_id': 1,
            'product_id': '33333333-3333-3333-3333-333333333333',
            'stocks': None,
            'price': '200.000000',
            'old_price': '150.000000',
            'vat': -10,
        },
        {
            'place_id': 1,
            'product_id': '00000000-0000-0000-0000-000000000010',
            'stocks': 3,
            'price': '201.000000',
            'old_price': '151.000000',
            'vat': None,
        },
        {
            'place_id': 4,
            'product_id': '88888888-8888-8888-8888-888888888888',
            'stocks': 10,
            'price': '201.000000',
            'old_price': '151.000000',
            'vat': 20,
        },
    ]


def _sorted_data(data):
    data.sort(key=lambda k: (k['place_id'], k['product_id']))
    return data


def _apply_stock_limit_to_data(data, place_id, stocks_reset_limit):
    for product in data:
        product_stock = product['stocks'] or 0
        if (
                product['place_id'] == place_id
                and product_stock != 0
                and product_stock < stocks_reset_limit
        ):
            product['stocks'] = 0


def _apply_rounded_price(products, place_id):
    for product in products:
        if product['place_id'] != place_id:
            continue

        product['price'] = _proper_round_str(product['price'])
        old_price = product.get('old_price')
        if old_price:
            product['old_price'] = _proper_round_str(product['old_price'])


def _proper_round_str(price):
    return str(pennies_utils.proper_round(float(price))) + '.000000'


def _sql_set_place_stock_limit(pg_cursor, place_id, stock_reset_limit):
    pg_cursor.execute(
        """
        update eats_nomenclature.places
        set stock_reset_limit = %s
        where id = %s
        """,
        (stock_reset_limit, place_id),
    )
