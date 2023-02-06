# pylint: disable=redefined-outer-name
import pytest


from classifier_worker.generated.cron import run_cron


@pytest.fixture(name='mock_cars_catalog')
def _mock_cars_catalog(mockserver):
    @mockserver.json_handler(
        '/cars-catalog/cars-catalog/v1/autocomplete-models',
    )
    def _autocomplete_models(request):
        request_brand = request.query['brand']
        if request_brand == 'BMW':
            return {'brand': 'BMW', 'models': ['X2', 'X3', 'X6', 'X7']}
        if request_brand == 'Audi':
            return {
                'brand': 'Audi',
                'models': ['A7', 'TT', 'A6', 'A6 allroad'],
            }
        print('Unexpected brand in autocomplete models: ', request_brand)
        return {'brand': request_brand, 'models': []}

    @mockserver.json_handler(
        '/cars-catalog/cars-catalog/v1/autocomplete-brands',
    )
    def _autocomplete_brands(request):
        return {'brands': ['BMW', 'Audi']}


@pytest.mark.now('2020-08-22T23:00:00+03:00')
async def test_base_model_rules(
        cron_context, mongo, load_json, mock_cars_catalog,
):
    mongo_rules = load_json('base_model_rules.json')
    await mongo.classification_rules.insert_many(mongo_rules)

    await run_cron.main(
        [
            'classifier_worker.crontasks.classification_rules_migration',
            '-t',
            '0',
        ],
    )

    pool = cron_context.pg.master_pool
    async with pool.acquire() as connection:
        # check pg rules
        query, _ = cron_context.sqlt('get_all_classification_rules.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [
            (
                1,
                'Москва',
                'econom',
                None,
                None,
                False,
                'BMW',
                'X6',
                None,
                None,
                None,
                2020,
                None,
            ),
            (
                2,
                'Москва',
                'econom',
                None,
                None,
                True,
                'BMW',
                'X7',
                None,
                None,
                1990,
                None,
                None,
            ),
            (
                3,
                'Москва',
                'vip',
                None,
                None,
                True,
                'BMW',
                'X3',
                None,
                None,
                2013,
                None,
                None,
            ),
            (
                4,
                'Брянск',
                'uberx',
                None,
                None,
                True,
                'Audi',
                'TT',
                None,
                None,
                2000,
                None,
                None,
            ),
            (
                5,
                'Брянск',
                'vip',
                None,
                None,
                True,
                'Audi',
                'A6',
                None,
                None,
                1990,
                None,
                None,
            ),
        ]

        # check pg tariffs
        query, _ = cron_context.sqlt('get_all_tariffs.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [
            ('Москва', 'econom', True),
            ('Москва', 'vip', True),
            ('Брянск', 'uberx', True),
            ('Брянск', 'vip', True),
        ]

        # check pg classifiers
        query, _ = cron_context.sqlt('get_all_classifiers.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [('Москва', True), ('Брянск', True)]


@pytest.mark.now('2020-08-22T23:00:00+03:00')
async def test_stared_model_rules(
        cron_context, mockserver, mock_cars_catalog, mongo, load_json,
):
    @mockserver.json_handler('/cars-catalog/api/v1/cars/get_brand_models')
    def _mock_cars_catalog(request):
        return {}

    mongo_rules = load_json('stared_model_rules.json')
    await mongo.classification_rules.insert_many(mongo_rules)

    await run_cron.main(
        [
            'classifier_worker.crontasks.classification_rules_migration',
            '-t',
            '0',
        ],
    )

    pool = cron_context.pg.master_pool
    async with pool.acquire() as connection:
        # check pg rules
        query, _ = cron_context.sqlt('get_all_classification_rules.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [
            (
                1,
                'Москва',
                'business',
                None,
                None,
                True,
                None,
                None,
                None,
                None,
                2020,
                None,
                None,
            ),
            (
                2,
                'Москва',
                'business',
                None,
                None,
                True,
                'BMW',
                'X6*',
                None,
                None,
                2020,
                None,
                None,
            ),
            (
                3,
                'Москва',
                'business',
                None,
                None,
                True,
                'BMW',
                'X6',
                None,
                None,
                2020,
                None,
                None,
            ),
            (
                4,
                'Москва',
                'business',
                None,
                None,
                False,
                None,
                None,
                None,
                None,
                None,
                2004,
                None,
            ),
            (
                5,
                'Москва',
                'business',
                None,
                None,
                False,
                None,
                None,
                None,
                299999,
                None,
                None,
                None,
            ),
            (
                6,
                'Москва',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                None,
                None,
                2016,
                None,
            ),
            (
                7,
                'Москва',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                599999,
                None,
                None,
                None,
            ),
            (
                8,
                'Брянск',
                'uberx',
                None,
                None,
                True,
                None,
                None,
                None,
                None,
                2015,
                None,
                None,
            ),
            (
                9,
                'Брянск',
                'vip',
                None,
                None,
                True,
                'BMW',
                'X6',
                None,
                None,
                1990,
                None,
                None,
            ),
            (
                10,
                'Тбилиси',
                'child',
                None,
                None,
                False,
                'BMW',
                '*',
                None,
                None,
                None,
                2014,
                None,
            ),
            (
                11,
                'Тбилиси',
                'child',
                None,
                None,
                True,
                'audi',
                't*',
                None,
                None,
                2013,
                None,
                None,
            ),
            (
                12,
                'Химки',
                'child',
                None,
                None,
                True,
                'Audi',
                'A7',
                None,
                None,
                2015,
                None,
                None,
            ),
            (
                13,
                'Химки',
                'child',
                None,
                None,
                True,
                'Audi',
                'TT',
                None,
                None,
                2015,
                None,
                None,
            ),
            (
                14,
                'Химки',
                'child',
                None,
                None,
                True,
                'Audi',
                'A6',
                None,
                None,
                2015,
                None,
                None,
            ),
            (
                15,
                'Химки',
                'child',
                None,
                None,
                True,
                'Audi',
                'A6 allroad',
                None,
                None,
                2015,
                None,
                None,
            ),
            (
                16,
                'Химки',
                'child',
                None,
                None,
                False,
                'BMW',
                'X6',
                None,
                None,
                None,
                2012,
                None,
            ),
        ]

        # check pg tariffs
        query, _ = cron_context.sqlt('get_all_tariffs.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [
            ('Москва', 'business', True),
            ('Москва', 'econom', True),
            ('Брянск', 'uberx', False),
            ('Брянск', 'vip', True),
            ('Тбилиси', 'child', True),
            ('Химки', 'child', True),
        ]

        # check pg classifiers
        query, _ = cron_context.sqlt('get_all_classifiers.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [
            ('Москва', True),
            ('Брянск', True),
            ('Тбилиси', True),
            ('Химки', True),
        ]


@pytest.mark.now('2020-08-22T23:00:00+03:00')
async def test_global_not_allowing_price_rule(
        cron_context, mongo, load_json, mock_cars_catalog,
):
    mongo_rules = load_json('global_not_allowing_price_rule.json')
    await mongo.classification_rules.insert_many(mongo_rules)

    await run_cron.main(
        [
            'classifier_worker.crontasks.classification_rules_migration',
            '-t',
            '0',
        ],
    )

    pool = cron_context.pg.master_pool
    async with pool.acquire() as connection:
        # check pg rules
        query, _ = cron_context.sqlt('get_all_classification_rules.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [
            (
                1,
                'Брянск',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                None,
                None,
                2018,
                None,
            ),
            (
                2,
                'Брянск',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                99999997,
                None,
                None,
                None,
            ),
        ]

        # check pg tariffs
        query, _ = cron_context.sqlt('get_all_tariffs.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [
            ('Москва', 'econom', False),
            ('Брянск', 'econom', True),
        ]

        # check pg classifiers
        query, _ = cron_context.sqlt('get_all_classifiers.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [('Москва', True), ('Брянск', True)]


@pytest.mark.now('2020-08-22T23:00:00+03:00')
async def test_allowing_price_rules(
        cron_context, mongo, load_json, mock_cars_catalog,
):
    mongo_rules = load_json('allowing_price_rules.json')
    await mongo.classification_rules.insert_many(mongo_rules)

    await run_cron.main(
        [
            'classifier_worker.crontasks.classification_rules_migration',
            '-t',
            '0',
        ],
    )

    pool = cron_context.pg.master_pool
    async with pool.acquire() as connection:
        # check pg rules
        query, _ = cron_context.sqlt('get_all_classification_rules.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [
            (
                1,
                'Тбилиси',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                None,
                None,
                2016,
                None,
            ),
            (
                2,
                'Тбилиси',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                12313,
                None,
                None,
                None,
            ),
            (
                3,
                'Брянск',
                'econom',
                None,
                None,
                False,
                'BMW',
                'X6',
                None,
                None,
                None,
                2014,
                None,
            ),
        ]

        # check pg tariffs
        query, _ = cron_context.sqlt('get_all_tariffs.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [
            ('Москва', 'econom', True),
            ('Тбилиси', 'econom', True),
            ('Брянск', 'econom', True),
        ]

        # check pg classifiers
        query, _ = cron_context.sqlt('get_all_classifiers.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [
            ('Москва', True),
            ('Тбилиси', True),
            ('Брянск', True),
        ]


@pytest.mark.now('2020-08-22T23:00:00+03:00')
@pytest.mark.pgsql('classifier', files=['classifier.sql'])
async def test_stairs_price_rules(
        cron_context, mongo, load_json, mock_cars_catalog,
):
    mongo_rules = load_json('stairs_price_rules.json')
    await mongo.classification_rules.insert_many(mongo_rules)

    await run_cron.main(
        [
            'classifier_worker.crontasks.classification_rules_migration',
            '-t',
            '0',
        ],
    )

    pool = cron_context.pg.master_pool
    async with pool.acquire() as connection:
        # check pg rules
        query, _ = cron_context.sqlt('get_all_classification_rules.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [
            (
                3,
                'Москва',
                'econom',
                None,
                None,
                True,
                'Audi',
                'TT',
                None,
                None,
                2016,
                None,
                None,
            ),
            (
                4,
                'Москва',
                'econom',
                None,
                None,
                False,
                None,
                None,
                0,
                99999,
                2012,
                2020,
                None,
            ),
            (
                5,
                'Москва',
                'econom',
                None,
                None,
                False,
                None,
                None,
                0,
                199999,
                2010,
                2011,
                None,
            ),
            (
                6,
                'Москва',
                'econom',
                None,
                None,
                False,
                None,
                None,
                0,
                299999,
                2005,
                2009,
                None,
            ),
            (
                7,
                'Москва',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                None,
                None,
                2004,
                None,
            ),
            (
                8,
                'Москва',
                'vip',
                None,
                None,
                False,
                'BMW',
                'X3',
                None,
                None,
                None,
                2020,
                None,
            ),
        ]
        # check pg tariffs
        query, _ = cron_context.sqlt('get_all_tariffs.sqlt', {})
        rows = await connection.fetch(query)
        tuples = [row['row'] for row in rows]
        assert tuples == [('Москва', 'econom', True), ('Москва', 'vip', True)]
        # check pg classifiers
        query, _ = cron_context.sqlt('get_all_classifiers.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [('Москва', True)]


@pytest.mark.now('2020-08-22T23:00:00+03:00')
async def test_complex_price_rules(
        cron_context, mongo, load_json, mock_cars_catalog,
):
    mongo_rules = load_json('complex_price_rules.json')
    await mongo.classification_rules.insert_many(mongo_rules)
    await run_cron.main(
        [
            'classifier_worker.crontasks.classification_rules_migration',
            '-t',
            '0',
        ],
    )
    pool = cron_context.pg.master_pool
    async with pool.acquire() as connection:
        # check pg rules
        query, _ = cron_context.sqlt('get_all_classification_rules.sqlt', {})
        rows = await connection.fetch(query)
        tuples = [row['row'] for row in rows]
        assert tuples == [
            (
                1,
                'Москва',
                'econom',
                None,
                None,
                False,
                None,
                None,
                0,
                99999,
                2010,
                2020,
                None,
            ),
            (
                2,
                'Москва',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                None,
                None,
                2009,
                None,
            ),
            (
                3,
                'Брянск',
                'econom',
                None,
                None,
                False,
                None,
                None,
                0,
                199999,
                2012,
                2020,
                None,
            ),
            (
                4,
                'Брянск',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                None,
                None,
                2011,
                None,
            ),
            (
                5,
                'Тбилиси',
                'econom',
                None,
                None,
                False,
                None,
                None,
                0,
                99999,
                2005,
                2020,
                None,
            ),
            (
                6,
                'Тбилиси',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                None,
                None,
                2004,
                None,
            ),
            (
                7,
                'Лондон',
                'econom',
                None,
                None,
                False,
                None,
                None,
                0,
                299999,
                2010,
                2020,
                None,
            ),
            (
                8,
                'Лондон',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                None,
                None,
                2009,
                None,
            ),
            (
                9,
                'Урюпинск',
                'econom',
                None,
                None,
                False,
                None,
                None,
                0,
                99999,
                2010,
                2020,
                None,
            ),
            (
                10,
                'Урюпинск',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                None,
                None,
                2009,
                None,
            ),
            (
                11,
                'Хацапетовка',
                'econom',
                None,
                None,
                False,
                None,
                None,
                0,
                99999,
                2005,
                2020,
                None,
            ),
            (
                12,
                'Хацапетовка',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                None,
                None,
                2004,
                None,
            ),
            (
                13,
                'Санкт-Петербург',
                'econom',
                None,
                None,
                False,
                None,
                None,
                0,
                0,
                1919,
                2020,
                None,
            ),
            (
                14,
                'Санкт-Петербург',
                'econom',
                None,
                None,
                False,
                None,
                None,
                None,
                None,
                None,
                1918,
                None,
            ),
        ]
        # check pg tariffs
        query, _ = cron_context.sqlt('get_all_tariffs.sqlt', {})
        rows = await connection.fetch(query)

        tuples = [row['row'] for row in rows]
        assert tuples == [
            ('Москва', 'econom', True),
            ('Брянск', 'econom', True),
            ('Тбилиси', 'econom', True),
            ('Лондон', 'econom', True),
            ('Урюпинск', 'econom', True),
            ('Хацапетовка', 'econom', True),
            ('Санкт-Петербург', 'econom', True),
        ]
        # check pg classifiers
        query, _ = cron_context.sqlt('get_all_classifiers.sqlt', {})
        rows = await connection.fetch(query)
        tuples = [row['row'] for row in rows]
        assert tuples == [
            ('Москва', True),
            ('Брянск', True),
            ('Тбилиси', True),
            ('Лондон', True),
            ('Урюпинск', True),
            ('Хацапетовка', True),
            ('Санкт-Петербург', True),
        ]
