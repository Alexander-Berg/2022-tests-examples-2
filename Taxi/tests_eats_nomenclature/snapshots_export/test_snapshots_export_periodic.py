# pylint: disable=line-too-long
import pytest


MOCK_NOW = '2021-03-04T09:00:00+00:00'
PERIODIC_NAME = 'snapshots-export-periodic'
THRESHOLD = 30


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    EATS_NOMENCLATURE_PERIODICS={
        '__default__': {'is_enabled': True, 'period_in_sec': 60},
    },
)
@pytest.mark.parametrize(
    'reason',
    ['not_appropriate_time', 'not_first_export_today', 'periodic_failed'],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_brand_places.sql'],
)
async def test_export_periodic_error(
        pg_realdict_cursor,
        stq,
        taxi_config,
        taxi_eats_nomenclature,
        testpoint,
        reason,
):
    if reason == 'not_appropriate_time':
        taxi_config.set_values(
            {
                'EATS_NOMENCLATURE_EXPORT_SNAPSHOTS': {
                    'disabled_at_threshold_in_minutes': THRESHOLD,
                    'periodic_start_hour': 1,
                    'periodic_end_hour': 2,
                },
            },
        )
    elif reason == 'not_first_export_today':
        taxi_config.set_values(
            {
                'EATS_NOMENCLATURE_EXPORT_SNAPSHOTS': {
                    'disabled_at_threshold_in_minutes': THRESHOLD,
                    'periodic_start_hour': 1,
                    'periodic_end_hour': 23,
                },
            },
        )
        mock_date = MOCK_NOW[:10]
        _sql_set_yt_export_status(pg_realdict_cursor, mock_date)
    elif reason == 'periodic_failed':
        taxi_config.set_values(
            {
                'EATS_NOMENCLATURE_EXPORT_SNAPSHOTS': {
                    'disabled_at_threshold_in_minutes': THRESHOLD,
                    'periodic_start_hour': 1,
                    'periodic_end_hour': 23,
                },
            },
        )

        @testpoint(
            'eats-nomenclature-snapshots-export-periodic::fail-before-export',
        )
        def export_testpoint(param):
            return {'inject_failure': True}

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)
    assert (
        not stq.eats_nomenclature_export_places_products_snapshot.times_called
    )
    assert not stq.eats_nomenclature_export_categories_snapshots.times_called
    assert not stq.eats_nomenclature_export_products_snapshot.times_called
    assert (
        not stq.eats_nomenclature_export_default_assortments_snapshots.times_called  # noqa: E501 pylint: disable=line-too-long
    )
    if reason == 'periodic_failed':
        mock_date = MOCK_NOW[:10]
        assert _sql_get_yt_export_status(pg_realdict_cursor, mock_date) == {
            'export_date': mock_date,
            'status': 'init_failed',
        }
        assert export_testpoint.has_calls


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    EATS_NOMENCLATURE_PERIODICS={
        '__default__': {'is_enabled': True, 'period_in_sec': 60},
    },
)
@pytest.mark.config(
    EATS_NOMENCLATURE_EXPORT_SNAPSHOTS={
        'disabled_at_threshold_in_minutes': THRESHOLD,
        'periodic_start_hour': 1,
        'periodic_end_hour': 23,
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_brand_places.sql'],
)
async def test_export_periodic(
        pg_realdict_cursor, stq, taxi_eats_nomenclature,
):
    brands_to_export = _sql_get_brands(pg_realdict_cursor, THRESHOLD)
    places_to_export = _sql_get_places(pg_realdict_cursor, THRESHOLD)

    await taxi_eats_nomenclature.run_distlock_task(PERIODIC_NAME)

    places_from_pp_tasks = []
    for _ in range(
            stq.eats_nomenclature_export_places_products_snapshot.times_called,
    ):
        places_from_pp_tasks.append(
            stq.eats_nomenclature_export_places_products_snapshot.next_call()[
                'kwargs'
            ]['place_id'],
        )
    assert sorted(places_from_pp_tasks) == sorted(places_to_export)

    places_from_categories_tasks = []
    for _ in range(
            stq.eats_nomenclature_export_categories_snapshots.times_called,
    ):
        places_from_categories_tasks.append(
            stq.eats_nomenclature_export_categories_snapshots.next_call()[
                'kwargs'
            ]['place_id'],
        )
    assert sorted(places_from_categories_tasks) == sorted(places_to_export)

    brands_from_products_tasks = []
    brands_from_def_assort_tasks = []
    for _ in range(
            stq.eats_nomenclature_export_products_snapshot.times_called,
    ):
        brands_from_products_tasks.append(
            stq.eats_nomenclature_export_products_snapshot.next_call()[
                'kwargs'
            ]['brand_id'],
        )
    assert sorted(brands_from_products_tasks) == sorted(brands_to_export)

    for _ in range(
            stq.eats_nomenclature_export_default_assortments_snapshots.times_called,  # noqa: E501 pylint: disable=line-too-long
    ):
        brands_from_def_assort_tasks.append(
            stq.eats_nomenclature_export_default_assortments_snapshots.next_call()[  # noqa: E501 pylint: disable=line-too-long
                'kwargs'
            ][
                'brand_id'
            ],
        )
    assert sorted(brands_from_def_assort_tasks) == sorted(brands_to_export)
    mock_date = MOCK_NOW[:10]
    assert _sql_get_yt_export_status(pg_realdict_cursor, mock_date) == {
        'export_date': mock_date,
        'status': 'init_finished',
    }


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_products.sql'],
)
async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _sql_get_places(pg_realdict_cursor, minutes):
    pg_realdict_cursor.execute(
        f"""
        select id
        from eats_nomenclature.places p
        where is_enabled or updated_at > now() - interval '{minutes} minutes'
        """,
    )
    places_from_db = pg_realdict_cursor.fetchall()
    return [place['id'] for place in places_from_db]


def _sql_get_brands(pg_realdict_cursor, minutes):
    pg_realdict_cursor.execute(
        f"""
        select id
        from eats_nomenclature.brands
        where is_enabled or updated_at > now() - interval '{minutes} minutes'
        """,
    )
    brands_from_db = pg_realdict_cursor.fetchall()
    return [brand['id'] for brand in brands_from_db]


def _sql_set_yt_export_status(pg_realdict_cursor, date):
    pg_realdict_cursor.execute(
        f"""
        insert into
        eats_nomenclature.yt_snapshot_export_statuses (export_date, status)
        values ('{date}', 'init_started');
        """,
    )


def _sql_get_yt_export_status(pg_realdict_cursor, date):
    pg_realdict_cursor.execute(
        f"""
        select export_date, status
        from eats_nomenclature.yt_snapshot_export_statuses
        where export_date='{date}'
        """,
    )
    return pg_realdict_cursor.fetchone()
