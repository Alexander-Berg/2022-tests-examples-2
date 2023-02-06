import datetime as dt

import pytest
import pytz

PERIODIC_NAME = 'db-cleanup-periodic'
DEFAULT_INTERVAL_HOURS = 30
MOCK_NOW = dt.datetime(2021, 3, 2, 12, tzinfo=pytz.UTC)


def sql_count_records(pgsql, table_name):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select count(*)
        from eats_nomenclature.{table_name}
        """,
    )
    return list(cursor)[0][0]


def config(**kwargs):
    return {
        'EATS_NOMENCLATURE_DB_CLEANUP': {
            '__default__': {'interval-hours': DEFAULT_INTERVAL_HOURS},
            **kwargs,
        },
    }


@pytest.mark.parametrize(
    'data',
    [
        pytest.param(
            {
                'config': {'upload_tasks': {'interval-hours': 10}},
                'tables': [
                    {
                        'name': 'upload_tasks',
                        'count_records': 6,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'upload_task_status_history',
                        'count_records': 7,
                        'expected_count_records': 4,
                    },
                ],
            },
            id='upload_tasks: something deleted',
        ),
        pytest.param(
            {
                'config': {'upload_stock_tasks': {'interval-hours': 10}},
                'tables': [
                    {
                        'name': 'upload_stock_tasks',
                        'count_records': 6,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'upload_stock_task_status_history',
                        'count_records': 7,
                        'expected_count_records': 4,
                    },
                ],
            },
            id='upload_stock_tasks: something deleted',
        ),
        pytest.param(
            {
                'config': {
                    'upload_availability_tasks': {'interval-hours': 10},
                },
                'tables': [
                    {
                        'name': 'upload_availability_tasks',
                        'count_records': 7,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'upload_availability_task_status_history',
                        'count_records': 8,
                        'expected_count_records': 4,
                    },
                ],
            },
            id='upload_availability_tasks: something deleted',
        ),
        pytest.param(
            {
                'config': {
                    'assortments': {'interval-hours': 10},
                    'place_assortments_processing_last_status_history': {
                        'interval-hours': 20,
                    },
                },
                'tables': [
                    {
                        'name': 'categories_relations',
                        'count_records': 5,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'categories_products',
                        'count_records': 8,
                        'expected_count_records': 6,
                    },
                    {
                        'name': 'category_pictures',
                        'count_records': 5,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'places_categories',
                        'count_records': 5,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'categories',
                        'count_records': 5,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'upload_tasks',
                        'count_records': 6,
                        'expected_count_records': 4,
                    },
                    {
                        'name': 'upload_task_status_history',
                        'count_records': 7,
                        'expected_count_records': 5,
                    },
                    {
                        'name': 'upload_stock_tasks',
                        'count_records': 6,
                        'expected_count_records': 4,
                    },
                    {
                        'name': 'upload_stock_task_status_history',
                        'count_records': 7,
                        'expected_count_records': 5,
                    },
                    {
                        'name': 'upload_availability_tasks',
                        'count_records': 7,
                        'expected_count_records': 5,
                    },
                    {
                        'name': 'upload_availability_task_status_history',
                        'count_records': 8,
                        'expected_count_records': 6,
                    },
                    {
                        'name': 'assortment_enrichment_statuses',
                        'count_records': 5,
                        'expected_count_records': 3,
                    },
                    {
                        'name': (
                            'place_assortments_processing_last_status_history'
                        ),
                        'count_records': 5,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'assortments',
                        'count_records': 12,
                        'expected_count_records': 9,
                    },
                ],
            },
            id='assortments: something deleted',
        ),
        pytest.param(
            {
                'config': {
                    'upload_tasks': {'interval-hours': 10},
                    'upload_stock_tasks': {'interval-hours': 10},
                    'upload_availability_tasks': {'interval-hours': 10},
                    'assortments': {'interval-hours': 10},
                    'products': {'interval-hours': 14},
                    'not_picked_items': {'interval-hours': 10},
                    'products_usage': {'interval-hours': 10},
                    'places_processing_last_status_v2_history': {
                        'interval-hours': 10,
                    },
                    'place_assortments_processing_last_status_history': {
                        'interval-hours': 20,
                    },
                    'places_stats_history': {'interval-hours': 20},
                },
                'tables': [
                    {
                        'name': 'autodisabled_products',
                        'count_records': 6,
                        'expected_count_records': 5,
                    },
                    {
                        'name': 'products',
                        'count_records': 8,
                        'expected_count_records': 7,
                    },
                    {
                        'name': 'products_usage',
                        'count_records': 8,
                        'expected_count_records': 7,
                    },
                    {
                        'name': 'not_picked_items',
                        'count_records': 3,
                        'expected_count_records': 1,
                    },
                    {
                        'name': 'custom_categories_products',
                        'count_records': 1,
                        'expected_count_records': 0,
                    },
                    {
                        'name': 'stocks',
                        'count_records': 1,
                        'expected_count_records': 0,
                    },
                    {
                        'name': 'places_products',
                        'count_records': 6,
                        'expected_count_records': 5,
                    },
                    {
                        'name': 'product_barcodes',
                        'count_records': 6,
                        'expected_count_records': 5,
                    },
                    {
                        'name': 'product_pictures',
                        'count_records': 3,
                        'expected_count_records': 2,
                    },
                    {
                        'name': 'product_attributes',
                        'count_records': 1,
                        'expected_count_records': 0,
                    },
                    {
                        'name': 'categories_relations',
                        'count_records': 5,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'categories_products',
                        'count_records': 8,
                        'expected_count_records': 6,
                    },
                    {
                        'name': 'category_pictures',
                        'count_records': 5,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'places_categories',
                        'count_records': 5,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'categories',
                        'count_records': 5,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'upload_tasks',
                        'count_records': 6,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'upload_task_status_history',
                        'count_records': 7,
                        'expected_count_records': 4,
                    },
                    {
                        'name': 'upload_stock_tasks',
                        'count_records': 6,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'upload_stock_task_status_history',
                        'count_records': 7,
                        'expected_count_records': 4,
                    },
                    {
                        'name': 'upload_availability_tasks',
                        'count_records': 7,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'upload_availability_task_status_history',
                        'count_records': 8,
                        'expected_count_records': 4,
                    },
                    {
                        'name': 'assortment_enrichment_statuses',
                        'count_records': 5,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'assortments',
                        'count_records': 12,
                        'expected_count_records': 8,
                    },
                    {
                        'name': 'places_processing_last_status_v2_history',
                        'count_records': 5,
                        'expected_count_records': 2,
                    },
                    {
                        'name': (
                            'place_assortments_processing_last_status_history'
                        ),
                        'count_records': 5,
                        'expected_count_records': 3,
                    },
                    {
                        'name': 'places_stats_history',
                        'count_records': 4,
                        'expected_count_records': 2,
                    },
                    {
                        'name': 'place_assortments',
                        'count_records': 7,
                        'expected_count_records': 5,
                    },
                ],
            },
            id='all: something deleted',
        ),
        pytest.param(
            {
                'config': {},
                'tables': [
                    {
                        'name': 'autodisabled_products',
                        'count_records': 6,
                        'expected_count_records': 6,
                    },
                    {
                        'name': 'categories_relations',
                        'count_records': 5,
                        'expected_count_records': 5,
                    },
                    {
                        'name': 'categories_products',
                        'count_records': 8,
                        'expected_count_records': 8,
                    },
                    {
                        'name': 'category_pictures',
                        'count_records': 5,
                        'expected_count_records': 5,
                    },
                    {
                        'name': 'places_categories',
                        'count_records': 5,
                        'expected_count_records': 5,
                    },
                    {
                        'name': 'categories',
                        'count_records': 5,
                        'expected_count_records': 5,
                    },
                    {
                        'name': 'stocks',
                        'count_records': 1,
                        'expected_count_records': 1,
                    },
                    {
                        'name': 'places_products',
                        'count_records': 6,
                        'expected_count_records': 6,
                    },
                    {
                        'name': 'upload_tasks',
                        'count_records': 6,
                        'expected_count_records': 6,
                    },
                    {
                        'name': 'upload_task_status_history',
                        'count_records': 7,
                        'expected_count_records': 7,
                    },
                    {
                        'name': 'upload_stock_tasks',
                        'count_records': 6,
                        'expected_count_records': 6,
                    },
                    {
                        'name': 'upload_stock_task_status_history',
                        'count_records': 7,
                        'expected_count_records': 7,
                    },
                    {
                        'name': 'upload_availability_tasks',
                        'count_records': 7,
                        'expected_count_records': 7,
                    },
                    {
                        'name': 'upload_availability_task_status_history',
                        'count_records': 8,
                        'expected_count_records': 8,
                    },
                    {
                        'name': 'assortment_enrichment_statuses',
                        'count_records': 5,
                        'expected_count_records': 5,
                    },
                    {
                        'name': 'assortments',
                        'count_records': 12,
                        'expected_count_records': 12,
                    },
                    {
                        'name': 'places_processing_last_status_v2_history',
                        'count_records': 5,
                        'expected_count_records': 5,
                    },
                    {
                        'name': (
                            'place_assortments_processing_last_status_history'
                        ),
                        'count_records': 5,
                        'expected_count_records': 5,
                    },
                    {
                        'name': 'places_stats_history',
                        'count_records': 4,
                        'expected_count_records': 4,
                    },
                    {
                        'name': 'place_assortments',
                        'count_records': 7,
                        'expected_count_records': 7,
                    },
                ],
            },
            id='all: nothing deleted',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_to_cleanup.sql'],
)
async def test_db_cleanup(
        pgsql, testpoint, taxi_config, taxi_eats_nomenclature, data,
):
    if data['config'] != {}:
        taxi_config.set_values(
            {
                'EATS_NOMENCLATURE_DB_CLEANUP': {
                    '__default__': {'interval-hours': DEFAULT_INTERVAL_HOURS},
                    **data['config'],
                },
                'EATS_NOMENCLATURE_DB_CLEANUP_COMMON': {
                    'disabled_places_old_assortment_settings': {
                        'disabled_interval_hours': 8,
                        'assortment_activated_hours': 3,
                    },
                },
            },
        )
    else:
        taxi_config.set_values(
            {
                'EATS_NOMENCLATURE_DB_CLEANUP': {
                    '__default__': {'interval-hours': DEFAULT_INTERVAL_HOURS},
                    **data['config'],
                },
            },
        )

    @testpoint('db-cleanup-periodic-finished')
    def task_testpoint(param):
        pass

    # before cleanup
    for table in data['tables']:
        assert (
            sql_count_records(pgsql, table['name']) == table['count_records']
        )

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    # after cleanup
    assert task_testpoint.times_called == 1
    for table in data['tables']:
        assert (
            sql_count_records(pgsql, table['name'])
            == table['expected_count_records']
        )


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.parametrize(
    'assortment_activated_hours, expected_logged_places',
    [
        pytest.param(10, set(), id='nothing deleted'),
        pytest.param(5, set(), id='something deleted, but nothing logged'),
        pytest.param(2, {'2'}, id='something deleted, something logged'),
        pytest.param(0, {'2', '3'}, id='everything deleted, something logged'),
    ],
)
async def test_on_delete_active_assortment_log(
        pgsql,
        testpoint,
        taxi_config,
        taxi_eats_nomenclature,
        # parametrize
        assortment_activated_hours,
        expected_logged_places,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_DB_CLEANUP_COMMON': {
                'disabled_places_old_assortment_settings': {
                    'disabled_interval_hours': DEFAULT_INTERVAL_HOURS,
                    'assortment_activated_hours': assortment_activated_hours,
                },
            },
        },
    )

    sql_set_data_for_log_test(pgsql)

    @testpoint('db-cleanup-periodic-finished')
    def task_testpoint(param):
        pass

    logged_places = set()

    @testpoint('yt-logger-on-delete-active-assortment')
    def yt_logger(data):
        assert data['timestamp'] == MOCK_NOW.strftime('%Y-%m-%dT%H:%M:%S')
        logged_places.add(data['place_id'])

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    assert task_testpoint.times_called == 1
    assert yt_logger.times_called == len(expected_logged_places)
    assert logged_places == expected_logged_places


@pytest.mark.parametrize('is_enabled', [True, False, None])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_to_cleanup.sql'],
)
async def test_db_cleanup_is_enabled(
        pgsql, testpoint, taxi_config, taxi_eats_nomenclature, is_enabled,
):
    interval_hours = 10
    data = {
        'config': {'__default__': {'interval-hours': interval_hours}},
        'tables': [
            {
                'name': 'upload_tasks',
                'count_records': 6,
                'count_records_if_enabled': 3,
            },
            {
                'name': 'upload_task_status_history',
                'count_records': 7,
                'count_records_if_enabled': 4,
            },
            {
                'name': 'assortments',
                'count_records': 12,
                'count_records_if_enabled': 8,
            },
            {
                'name': 'products',
                'count_records': 8,
                'count_records_if_enabled': 6,
            },
            {
                'name': 'places_processing_last_status_v2_history',
                'count_records': 5,
                'count_records_if_enabled': 2,
            },
            {
                'name': 'place_assortments_processing_last_status_history',
                'count_records': 5,
                'count_records_if_enabled': 2,
            },
            {
                'name': 'places_stats_history',
                'count_records': 4,
                'count_records_if_enabled': 1,
            },
        ],
    }

    # use default value if is_enabled is None
    if is_enabled is not None:
        for table in data['tables']:
            table_name = table['name']
            data['config'][table_name] = {
                'is_enabled': is_enabled,
                'interval-hours': interval_hours,
            }

    taxi_config.set_values(config(**data['config']))

    @testpoint('db-cleanup-periodic-finished')
    def task_testpoint(param):
        pass

    # before cleanup
    for table in data['tables']:
        assert (
            sql_count_records(pgsql, table['name']) == table['count_records']
        ), table

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    # after cleanup
    assert task_testpoint.times_called == 1
    for table in data['tables']:
        if is_enabled or (is_enabled is None):
            assert (
                sql_count_records(pgsql, table['name'])
                == table['count_records_if_enabled']
            ), table
        else:
            assert (
                sql_count_records(pgsql, table['name'])
                == table['count_records']
            ), table


@pytest.mark.pgsql('eats_nomenclature', files=['fill_dictionaries.sql'])
async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def sql_set_data_for_log_test(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.brands(id)
        values (777);
        """,
    )
    cursor.execute(
        f"""
        insert into eats_nomenclature.assortment_traits(
            id, brand_id, assortment_name
        )
        values (1, 777, 'some assortment trait');
        """,
    )
    cursor.execute(
        f"""
        insert into eats_nomenclature.assortments(id)
        values (1), (2), (3), (4);
        """,
    )

    place_assortments = [
        # place has only custom assortment, so it shouldn't be logged
        {
            'place_id': 1,
            'trait_id': 1,
            'assortment_id': 1,
            'assortment_activated_hours': 8,
        },
        # place has custom and partner assortment
        {
            'place_id': 2,
            'trait_id': 1,
            'assortment_id': 2,
            'assortment_activated_hours': 6,
        },
        {
            'place_id': 2,
            'trait_id': 'null',
            'assortment_id': 3,
            'assortment_activated_hours': 3,
        },
        # place has only partner assortment
        {
            'place_id': 3,
            'trait_id': 'null',
            'assortment_id': 4,
            'assortment_activated_hours': 1,
        },
    ]
    for place_assortment in place_assortments:
        place_id = place_assortment['place_id']
        trait_id = place_assortment['trait_id']
        assortment_id = place_assortment['assortment_id']
        hours = place_assortment['assortment_activated_hours']
        cursor.execute(
            f"""
            insert into eats_nomenclature.places(
                id, slug, is_enabled, updated_at
            ) values (
                {place_id}, 'slug_{place_id}', false,
                now() - interval '10 days'
            )
            on conflict (id) do nothing;
            """,
        )
        cursor.execute(
            f"""
            insert into eats_nomenclature.place_assortments(
                place_id, trait_id, assortment_id, assortment_activated_at
            ) values (
                {place_id}, {trait_id}, {assortment_id},
                now() - interval '{hours} hours'
            );
            """,
        )
