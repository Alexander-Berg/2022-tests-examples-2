import datetime

import pytest

from cars_catalog.generated.cron import run_cron


@pytest.mark.now('2019-05-14T21:03:00+0000')
@pytest.mark.config(CRON_TASK_ENABLED=True)
@pytest.mark.pgsql('cars_catalog', files=['default.sql'])
@pytest.mark.config(
    CARS_CATALOG_PRICES_CLARIFICATION={
        'enable': True,
        'default_price': 123,
        'override': {'Ford Galaxy 2017': 321},
        'exclude': [{'brand': 'toyota', 'model': 'Corolla'}],
    },
)
async def test_normalize_cars_fields_full(cron_context, patch_misspells_get):
    await run_cron.main(
        ['cars_catalog.crontasks.normalize_cars_fields', '-t', '0'],
    )
    result = await _main_process(cron_context, is_large=True)
    _assert_prices_large(result)
    _assert_brand_models_large(result)
    _assert_colors_large(result)


def _assert_prepared_prices_large(result):
    assert result['prepared_prices'] == {
        ('FORD', 'GALAXY', 2010, '350000.7'),
        ('TOYOTA', 'CAMRY', 2013, '123'),
        ('FORD', 'GALAXY', 2017, '684068.6'),
        ('TOYOTA', 'COROLLA', 2010, '-1'),
    }


def _assert_prices_large(result):
    assert set(result['prices']) == {
        ('FORD', 'GALAXY', 2010, 2010, 350000.7),
        ('FORD', 'GALAXY', None, 2014, 490000.98000000016),
        ('FORD', 'GALAXY', 2017, 2017, 684068.6),
        ('TOYOTA', 'CAMRY', 2013, 2013, 484068.5),
        ('TOYOTA', 'COROLLA', 2010, 2010, 584068.3),
    }


def _assert_colors_large(result):
    res = sorted(result['colors'])
    assert list(res) == [
        ('43B4B2', 'Бирюза', 'бирюза'),
        ('43B4B2', 'бирюза', 'бирюза'),
        ('555555', 'Бронза', 'бронза'),
        ('AAAEA0', ' БРОнЗа ', 'бронза'),
    ]


def _assert_brand_models_large(result):
    assert sorted(result['brand_models']) == [
        ('ford', 'Galaxy', 'FORD', 'GALAXY', 'ford Galaxy'),
        ('ford', 'Mustang', 'FORD', 'MUSTANG', 'ford Mustang'),
        ('toyota', 'Camry', 'TOYOTA', 'CAMRY', 'toyota Camry'),
        ('toyota', 'Corolla', 'TOYOTA', 'COROLLA', 'toyota Corolla'),
    ]


@pytest.mark.now('2019-05-14T21:03:00+0000')
@pytest.mark.config(CRON_TASK_ENABLED=True)
@pytest.mark.parametrize(
    'last_updated_ts,last_inc,colors_not_processed,brand_not_processed,'
    'prices_not_processed',
    [
        (
            1000001,
            1,
            ['черный'],
            [('toyota', 'Camry')],
            [('TOYOTA', 'CAMRY', 2013)],
        ),
        (999999, 10, [], [], []),
        (
            1000002,
            4,
            ['черный', ' БРОнЗа ', 'БРЮнза ', 'Бирюза', 'бирюза'],
            [('toyota', 'Camry'), ('ford', 'Galaxy'), ('toyota', 'Corolla')],
            [
                ('FORD', 'GALAXY', 2010),
                ('FORD', 'GALAXY', None),
                ('FORD', 'GALAXY', 2017),
                ('TOYOTA', 'CAMRY', 2013),
                ('TOYOTA', 'COROLLA', 2010),
            ],
        ),
        (
            1000002,
            1,
            ['черный', ' БРОнЗа ', 'БРЮнза '],
            [('toyota', 'Camry'), ('toyota', 'Corolla')],
            [
                ('FORD', 'GALAXY', 2010),
                ('TOYOTA', 'CAMRY', 2013),
                ('TOYOTA', 'COROLLA', 2010),
            ],
        ),
    ],
)
@pytest.mark.config(
    CARS_CATALOG_PRICES_CLARIFICATION={
        'enable': True,
        'default_price': 123,
        'override': {'Ford Galaxy 2017': 321},
        'exclude': [{'brand': 'toyota', 'model': 'Corolla'}],
    },
)
@pytest.mark.pgsql('cars_catalog', files=['partialy.sql'])
async def test_normalize_cars_fields_partialy(
        cron_context,
        last_updated_ts,
        last_inc,
        colors_not_processed,
        brand_not_processed,
        prices_not_processed,
        patch_misspells_get,
):
    pool = cron_context.pg.master_pool

    if last_updated_ts is not None:
        async with pool.acquire() as connection:
            large = datetime.datetime(2019, 5, 14, 21, 0)
            query, args = cron_context.sqlt(
                'insert_meta.sqlt',
                {
                    'last_updated_ts': last_updated_ts,
                    'last_inc': last_inc,
                    'large_task_completed': large,
                    'small_task_completed': None,
                },
            )
            meta = await connection.fetchrow(query, *args)
            assert meta
            assert meta['last_updated_ts'] == last_updated_ts
            assert meta['last_inc'] == last_inc
            assert meta['large_task_completed'] == large
            assert meta['small_task_completed'] is None

    await run_cron.main(
        ['cars_catalog.crontasks.normalize_cars_fields', '-t', '0'],
    )
    result = await _main_process(cron_context, is_large=False)

    _assert_prices_small(result, prices_not_processed)
    _assert_prepared_prices_small(result, prices_not_processed)
    _assert_colors_small(result, colors_not_processed)
    _assert_brand_models_small(result, brand_not_processed)


def _assert_prepared_prices_small(result, prices_not_processed):
    expected = set()
    if ('FORD', 'GALAXY', 2010) not in prices_not_processed:
        expected.add(('FORD', 'GALAXY', 2010, '350000.7'))

    if ('FORD', 'GALAXY', 2017) not in prices_not_processed:
        expected.add(('FORD', 'GALAXY', 2017, '684068.6'))

    if ('TOYOTA', 'CAMRY', 2013) not in prices_not_processed:
        expected.add(('TOYOTA', 'CAMRY', 2013, '511195.0'))
    else:
        expected.add(('TOYOTA', 'CAMRY', 2013, '100'))

    if ('TOYOTA', 'COROLLA', 2010) not in prices_not_processed:
        expected.add(('TOYOTA', 'COROLLA', 2010, '584068.3'))

    assert result['prepared_prices'] == expected


def _assert_prices_small(result, prices_not_processed):
    expected = set()
    if ('FORD', 'GALAXY', 2010) not in prices_not_processed:
        expected.add(('FORD', 'GALAXY', 2010, 2010, 350000.7))

    if ('FORD', 'GALAXY', None) not in prices_not_processed:
        expected.add(('FORD', 'GALAXY', None, 2014, 490000.98000000016))

    if ('FORD', 'GALAXY', 2017) not in prices_not_processed:
        expected.add(('FORD', 'GALAXY', 2017, 2017, 684068.6))

    if ('TOYOTA', 'CAMRY', 2013) not in prices_not_processed:
        expected.add(('TOYOTA', 'CAMRY', 2013, 2013, 484068.5))
    else:
        expected.add(('TOYOTA', 'CAMRY', 2013, 2003, 100))

    if ('TOYOTA', 'COROLLA', 2010) not in prices_not_processed:
        expected.add(('TOYOTA', 'COROLLA', 2010, 2010, 584068.3))

    assert set(result['prices']) == expected


def _assert_colors_small(result, colors_not_processed):
    expected = [
        ('333333', 'БРОнза ', 'бронза'),
        ('43B4B2', 'Бирюза', 'бирюза'),
        ('43B4B2', 'бирюза', 'бирюза'),
        ('AAAEA0', ' БРОнЗа ', 'бронза'),
    ]
    expected = [
        item for item in expected if item[1] not in colors_not_processed
    ]
    assert sorted(result['colors']) == sorted(expected)


def _assert_brand_models_small(result, brand_not_processed):
    expected = []
    if ('ford', 'Galaxy') not in brand_not_processed:
        expected.append(('ford', 'Galaxy', 'FORD', 'GALAXY', 'ford Galaxy'))

    if ('toyota', 'Camry') not in brand_not_processed:
        expected.append(('toyota', 'Camry', 'TOYOTA', 'CAMRY', 'toyota Camry'))
    else:
        expected.append(('toyota', 'Camry', 'TOYETA', 'COMRE', 'toyota Camry'))

    if ('toyota', 'Corolla') not in brand_not_processed:
        expected.append(
            ('toyota', 'Corolla', 'TOYOTA', 'COROLLA', 'toyota Corolla'),
        )

    assert sorted(result['brand_models']) == expected


async def _main_process(cron_context, is_large):
    pool = cron_context.pg.master_pool
    async with pool.acquire() as connection:
        colors_raw = await _get_colors(cron_context, connection)
        brand_models_raw = await _get_brand_models(cron_context, connection)
        prices = await _get_prices(cron_context, connection)
        prepared_prices = await _get_prepared_prices(connection)
        meta = await _get_meta(cron_context, connection)

    current = datetime.datetime(2019, 5, 14, 21, 3)
    small = None if is_large else current
    large = datetime.datetime(2019, 5, 14, 21, 0)

    assert meta
    assert meta['last_updated_ts'] == 1000002
    assert meta['last_inc'] == 4
    assert meta['small_task_completed'] == small
    assert meta['large_task_completed'] == large

    result = {
        'colors': [],
        'brand_models': [],
        'prices': [],
        'prepared_prices': set(),
    }
    for row in colors_raw:
        result['colors'].append(
            (row['color_code'], row['raw_color'], row['normalized_color']),
        )
    for row in brand_models_raw:
        result['brand_models'].append(
            (
                row['raw_brand'],
                row['raw_model'],
                row['normalized_mark_code'],
                row['normalized_model_code'],
                row['corrected_model'],
            ),
        )
    for row in prices:
        result['prices'].append(
            (
                row['normalized_mark_code'],
                row['normalized_model_code'],
                row['car_year'],
                row['car_age'],
                float(row['car_price']),
            ),
        )
    for row in prepared_prices:
        result['prepared_prices'].add(
            (
                row['mark_code'],
                row['model_code'],
                row['year'],
                str(row['price']),
            ),
        )
    return result


async def _get_prices(cron_context, connection):
    query, _ = cron_context.sqlt('get_all_prices.sqlt', {})
    rows = await connection.fetch(query)
    return rows


async def _get_prepared_prices(connection):
    return await connection.fetch('SELECT * FROM cars_catalog.prepared_prices')


async def _get_brand_models(cron_context, connection):
    query, _ = cron_context.sqlt('get_all_brand_models.sqlt', {})
    rows = await connection.fetch(query)
    return rows


async def _get_colors(cron_context, connection):
    query, _ = cron_context.sqlt('get_all_colors.sqlt', {})
    rows = await connection.fetch(query)
    return rows


async def _get_meta(cron_context, connection):
    query, _ = cron_context.sqlt('get_meta.sqlt')
    meta = await connection.fetchrow(query)
    return meta
