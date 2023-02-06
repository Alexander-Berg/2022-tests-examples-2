# pylint: disable=import-only-modules
import datetime

import pytest

from . import geo_hierarchies_consumer as ghc
from .utils import select_named


@pytest.mark.uservice_oneshot
@pytest.mark.pgsql(
    'reposition',
    files=['drivers.sql', 'reset_geo_hierarchies.sql'],
    queries=[
        """
        INSERT INTO etag_data.drivers_update_state(
            driver_id_id,
            updated_at
        ) VALUES (
            IdId('uuid', 'dbid'),
            '2021-05-01T00:00:00.000+00:00'
        )
        """,
    ],
)
@pytest.mark.parametrize(
    'raw_events,'
    'expected_metrics,'
    'expected_etag_updated_ats,'
    'expected_unknown_drivers',
    (
        pytest.param(
            [
                ghc.build_raw_event(
                    0, 1, 'invalid', '2021-05-01T00:00:00.000+00:00',
                ),
            ],
            {
                'ok_total_messages': 1,
                'ok_processed_messages': 0,
                'ok_excluded_drivers': 0,
                'ok_processed_known_drivers': 0,
                'ok_processed_unknown_drivers': 0,
                'ok_become_known_drivers': 0,
                'ok_processed_adopted_drivers': 0,
                'warn_long_processing': 0,
                'warn_unknown_drivers': 0,
                'warn_known_driver_processing': 0,
                'warn_unknown_driver_processing': 0,
                'warn_still_unknown_drivers': 0,
                'error_parsings': 1,
                'error_dropped_drivers': 0,
                'error_unknown_drivers_selections': 0,
                'error_adopted_drivers_processing': 0,
            },
            [{'updated_at': datetime.datetime(2021, 5, 1, 0, 0, 0)}],
            [],
            marks=[
                pytest.mark.config(
                    REPOSITION_API_GEO_HIERARCHIES_CONSUMER_SETTINGS={
                        'enabled': True,
                        'pipeline_size': 10,
                        'deadline_interval_s': 1,
                        'retry_interval_ms': 100,
                        'orphan_geo_hierarchies_processing_chunk': 2,
                    },
                ),
            ],
            id='invalid message',
        ),
        pytest.param(
            [
                ghc.build_raw_event(
                    'unknown',
                    'unknown',
                    ['br_moscow', 'br_russia', 'br_root'],
                    '2021-05-01T00:00:00.000+00:00',
                ),
                ghc.build_raw_event(
                    'unknown',
                    'unknown',
                    ['br_spb', 'br_russia', 'br_root'],
                    '2021-06-01T00:00:00.000+00:00',
                ),
                ghc.build_raw_event(
                    'eda',
                    'uuid',
                    ['br_perm', 'br_russia', 'br_root'],
                    '2021-06-01T00:00:00.000+00:00',
                ),
            ],
            {
                'ok_total_messages': 3,
                'ok_processed_messages': 3,
                'ok_excluded_drivers': 1,
                'ok_processed_known_drivers': 0,
                'ok_processed_unknown_drivers': 2,
                'ok_become_known_drivers': 0,
                'ok_processed_adopted_drivers': 0,
                'warn_long_processing': 0,
                'warn_unknown_drivers': 2,
                'warn_known_driver_processing': 0,
                'warn_unknown_driver_processing': 0,
                'warn_still_unknown_drivers': 0,
                'error_parsings': 0,
                'error_dropped_drivers': 0,
                'error_unknown_drivers_selections': 0,
                'error_adopted_drivers_processing': 0,
            },
            [{'updated_at': datetime.datetime(2021, 5, 1, 0, 0, 0)}],
            [
                {
                    'driver_id': '(unknown,unknown)',
                    'geo_hierarchy': ['br_spb', 'br_russia', 'br_root'],
                },
            ],
            marks=[
                pytest.mark.config(
                    REPOSITION_API_GEO_HIERARCHIES_CONSUMER_SETTINGS={
                        'enabled': True,
                        'pipeline_size': 10,
                        'deadline_interval_s': 1,
                        'retry_interval_ms': 100,
                        'orphan_geo_hierarchies_processing_chunk': 2,
                    },
                ),
            ],
            id='unknown/excluded drivers',
        ),
        pytest.param(
            [
                ghc.build_raw_event(
                    'dbid',
                    'uuid',
                    ['br_moscow', 'br_russia', 'br_root'],
                    '2021-05-01T00:00:00.000+00:00',
                ),
            ],
            {
                'ok_total_messages': 1,
                'ok_processed_messages': 1,
                'ok_excluded_drivers': 0,
                'ok_processed_known_drivers': 1,
                'ok_processed_unknown_drivers': 0,
                'ok_become_known_drivers': 0,
                'ok_processed_adopted_drivers': 0,
                'warn_long_processing': 0,
                'warn_unknown_drivers': 0,
                'warn_known_driver_processing': 0,
                'warn_unknown_driver_processing': 0,
                'warn_still_unknown_drivers': 0,
                'error_parsings': 0,
                'error_dropped_drivers': 0,
                'error_unknown_drivers_selections': 0,
                'error_adopted_drivers_processing': 0,
            },
            # updated_at is reset on successful processing
            [{'updated_at': None}],
            [],
            marks=[
                pytest.mark.config(
                    REPOSITION_API_GEO_HIERARCHIES_CONSUMER_SETTINGS={
                        'enabled': True,
                        'pipeline_size': 10,
                        'deadline_interval_s': 1,
                        'retry_interval_ms': 100,
                        'orphan_geo_hierarchies_processing_chunk': 2,
                    },
                ),
            ],
            id='valid driver',
        ),
    ),
)
async def test_consumer(
        taxi_reposition_api,
        taxi_reposition_api_monitor,
        pgsql,
        testpoint,
        raw_events,
        expected_metrics,
        expected_etag_updated_ats,
        expected_unknown_drivers,
):
    @testpoint('logbroker_commit')
    def lb_commit(cookie):
        assert cookie == 'cookie'

    for raw_event in raw_events:
        await ghc.post_event(taxi_reposition_api, raw_event)
        await lb_commit.wait_call()

    metrics = await taxi_reposition_api_monitor.get_metric(
        'geo-hierarchies-consumer',
    )

    del metrics['lag_sec']

    assert metrics == expected_metrics

    etag_updated_ats = select_named(
        """
        SELECT
            updated_at
        FROM
            etag_data.drivers_update_state
        WHERE
            driver_id_id = IdId('uuid', 'dbid')
        """,
        pgsql['reposition'],
    )

    assert etag_updated_ats == expected_etag_updated_ats

    unknown_drivers = select_named(
        """
        SELECT
            driver_id,
            geo_hierarchy
        FROM
            state.orphan_geo_hierarchies
        """,
        pgsql['reposition'],
    )

    assert unknown_drivers == expected_unknown_drivers


@pytest.mark.parametrize(
    'expected_geo_hierarchies, expected_orphan_geo_hierarchies',
    (
        pytest.param(
            [],
            [
                {
                    'driver_id': '(dbid,uuid1)',
                    'geo_hierarchy': ['br_spb', 'br_russia', 'br_root'],
                    'updated_at': datetime.datetime(2021, 5, 1, 0, 0, 0),
                },
                {
                    'driver_id': '(dbid,uuid2)',
                    'geo_hierarchy': ['br_perm', 'br_russia', 'br_root'],
                    'updated_at': datetime.datetime(2021, 5, 1, 0, 0, 0),
                },
            ],
            marks=[
                pytest.mark.now('2021-05-01T00:00:00.000+00:00'),
                pytest.mark.pgsql(
                    'reposition',
                    files=['orphans.sql'],
                    queries=[
                        """
                        UPDATE
                            state.orphan_geo_hierarchies
                        SET
                            updated_at = '2020-05-01T00:00:00.000+00:00'
                        WHERE
                            driver_id = ('dbid','uuid')::db.driver_id
                        """,
                    ],
                ),
                pytest.mark.config(
                    REPOSITION_API_GEO_HIERARCHIES_CONSUMER_SETTINGS={
                        'enabled': True,
                        'pipeline_size': 10,
                        'deadline_interval_s': 1,
                        'retry_interval_ms': 100,
                        'orphan_geo_hierarchies_processing_chunk': 100,
                        'orphan_geo_hierarchies_ttl_h': 24,
                    },
                ),
            ],
            id='expired and still unknown',
        ),
        pytest.param(
            [],
            [
                {
                    'driver_id': '(dbid,uuid)',
                    'geo_hierarchy': ['br_moscow', 'br_russia', 'br_root'],
                    'updated_at': datetime.datetime(2021, 5, 1, 0, 0, 0),
                },
                {
                    'driver_id': '(dbid,uuid1)',
                    'geo_hierarchy': ['br_spb', 'br_russia', 'br_root'],
                    'updated_at': datetime.datetime(2021, 5, 1, 0, 0, 0),
                },
                {
                    'driver_id': '(dbid,uuid2)',
                    'geo_hierarchy': ['br_perm', 'br_russia', 'br_root'],
                    'updated_at': datetime.datetime(2021, 5, 1, 0, 0, 0),
                },
            ],
            marks=[
                pytest.mark.pgsql('reposition', files=['orphans.sql']),
                pytest.mark.config(
                    REPOSITION_API_GEO_HIERARCHIES_CONSUMER_SETTINGS={
                        'enabled': True,
                        'pipeline_size': 10,
                        'deadline_interval_s': 1,
                        'retry_interval_ms': 100,
                        'orphan_geo_hierarchies_processing_chunk': 100,
                    },
                ),
            ],
            id='still unknown',
        ),
        pytest.param(
            [
                {
                    'geo_hierarchy': ['br_moscow', 'br_russia', 'br_root'],
                    'updated_at': datetime.datetime(2021, 5, 1, 0, 0, 0),
                },
                {
                    'geo_hierarchy': ['br_spb', 'br_russia', 'br_root'],
                    'updated_at': datetime.datetime(2021, 5, 1, 0, 0, 0),
                },
            ],
            [
                {
                    'driver_id': '(dbid,uuid2)',
                    'geo_hierarchy': ['br_perm', 'br_russia', 'br_root'],
                    'updated_at': datetime.datetime(2021, 5, 1, 0, 0, 0),
                },
            ],
            marks=[
                pytest.mark.pgsql(
                    'reposition',
                    files=[
                        'drivers.sql',
                        'reset_geo_hierarchies.sql',
                        'orphans.sql',
                    ],
                ),
                pytest.mark.config(
                    REPOSITION_API_GEO_HIERARCHIES_CONSUMER_SETTINGS={
                        'enabled': True,
                        'pipeline_size': 10,
                        'deadline_interval_s': 1,
                        'retry_interval_ms': 100,
                        'orphan_geo_hierarchies_processing_chunk': 2,
                    },
                ),
            ],
            id='become known',
        ),
    ),
)
async def test_orphan_geo_hierarchies_processor(
        taxi_reposition_api,
        pgsql,
        expected_geo_hierarchies,
        expected_orphan_geo_hierarchies,
):
    assert (
        await taxi_reposition_api.post(
            '/service/cron',
            json={'task_name': 'ophran-geo-hierarchies-processor'},
        )
    ).status_code == 200

    geo_hierarchies = select_named(
        """
        SELECT
            geo_hierarchy,
            updated_at
        FROM
            state.geo_hierarchies
        ORDER BY
            driver_id_id
        """,
        pgsql['reposition'],
    )
    assert expected_geo_hierarchies == geo_hierarchies

    orphan_geo_hierarchies = select_named(
        """
        SELECT
            driver_id,
            geo_hierarchy,
            updated_at
        FROM
            state.orphan_geo_hierarchies
        ORDER BY
            driver_id
        """,
        pgsql['reposition'],
    )
    assert expected_orphan_geo_hierarchies == orphan_geo_hierarchies
