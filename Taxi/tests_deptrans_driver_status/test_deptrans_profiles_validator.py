import datetime

import psycopg2
import pytest

from tests_deptrans_driver_status import utils

JOB_NAME = 'deptrans-profiles-validator'


def _get_metrics(diff):
    metrics = {
        'equals': 0,
        'temp_actual_approved': 0,
        'approved_actual_temp': 0,
        'temp_outdated': 0,
        'outdated_actual_approved': 0,
        'outdated_restored': 0,
        'invalid_binding': 0,
        'failed_restored': 0,
        'dry_run_enabled': 0,
    }
    return {**metrics, **diff}


def _settings(*, enabled=True, profiles_batch_size=100, dry_run_enabled=False):
    return {
        'enabled': enabled,
        'job-throttling-delay-ms': 1,
        'job-run-interval-s': 1,
        'profiles-batch-size': profiles_batch_size,
        'status_filter': {
            'temporary': True,
            'temporary_outdated': True,
            'approved': True,
        },
        'dry_run_enabled': dry_run_enabled,
    }


async def _wait_iteration(taxi_deptrans_driver_status, testpoint, enabled):
    @testpoint(f'{JOB_NAME}-finished')
    def task_finished(arg):
        pass

    async with taxi_deptrans_driver_status.spawn_task(JOB_NAME):
        finished = await task_finished.wait_call()
        assert finished['arg']['mode'] == enabled


@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_LICENSE_PREFIXES=utils.license_prefixes(),
    DEPTRANS_DRIVER_STATUS_PROFILES_VALIDATOR_SETTINGS=_settings(
        enabled=False,
    ),
)
async def test_disabled(taxi_deptrans_driver_status, testpoint, pgsql):
    await _wait_iteration(taxi_deptrans_driver_status, testpoint, False)


@pytest.mark.now('2021-01-01T12:00:00+00:00')
@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_LICENSE_PREFIXES=utils.license_prefixes(),
    DEPTRANS_DRIVER_STATUS_SUPPORTED_COUNTRIES={
        'supported_countries': ['rus', 'oth', 'blr'],
    },
    DEPTRANS_DRIVER_STATUS_PROFILES_VALIDATOR_SETTINGS=_settings(
        dry_run_enabled=True,
    ),
)
async def test_worker_dry_run(
        taxi_deptrans_driver_status,
        taxi_deptrans_driver_status_monitor,
        testpoint,
        pgsql,
        pg_deptrans_driver_status,
        pg_deptrans_profile_status_logs,
        deptrans_profile,
        mocked_time,
        personal,
        deptrans_ais_krt,
):
    await taxi_deptrans_driver_status.tests_control(reset_metrics=True)

    for profile in deptrans_profile.get_all():
        deptrans_id = profile.checking_deptrans_id or profile.deptrans_id
        deptrans_ais_krt.add_license(deptrans_id, profile.license_pd_id)
        deptrans_ais_krt.add_driver_id_status(deptrans_id, 'PERMANENT')

    await _wait_iteration(taxi_deptrans_driver_status, testpoint, True)

    mocked_time.sleep(60)
    await taxi_deptrans_driver_status.invalidate_caches()

    assert personal['bulk_retrieve'].times_called == 1
    assert personal['bulk_retrieve_licenses'].times_called == 1
    assert deptrans_ais_krt.check_driver.times_called == 9

    metrics = await taxi_deptrans_driver_status_monitor.get_metric(
        'profile_validator_stats',
    )
    assert metrics == _get_metrics(
        {
            'invalid_binding': 1,
            'outdated_actual_approved': 2,
            'total': 9,
            'equals': 1,
            'temp_actual_approved': 5,
            'dry_run_enabled': 1,
        },
    )
    for profile in deptrans_profile.get_all():
        assert (
            pg_deptrans_driver_status.get_deptrans_profile(
                profile.license_pd_id, pgsql,
            )
            == (
                profile.deptrans_id,
                profile.status,
                profile.checking_deptrans_id,
            )
        )
        assert (
            pg_deptrans_profile_status_logs.fetch_logs(
                profile.license_pd_id, pgsql,
            )
            == []
        )


@pytest.mark.now('2021-01-01T12:00:00+00:00')
@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_LICENSE_PREFIXES=utils.license_prefixes(),
    DEPTRANS_DRIVER_STATUS_SUPPORTED_COUNTRIES={
        'supported_countries': ['rus', 'oth', 'blr'],
    },
    DEPTRANS_DRIVER_STATUS_PROFILES_VALIDATOR_SETTINGS=_settings(),
    DEPTRANS_DRIVER_STATUS_PROFILE_TAGS={
        'approved': [
            {'name': 'kis_art_approved'},
            {'name': 'kis_art_priority', 'ttl': 604800},
        ],
        'temporary': [
            {'name': 'kis_art_temp_issued'},
            {'name': 'kis_art_temp', 'ttl': 2592000},
        ],
        'temporary_requested': [],
        'temporary_outdated': [],
        'failed': [],
    },
)
@pytest.mark.parametrize(
    ['actual_status', 'metric_diff', 'personal_calls', 'licenses_calls'],
    [
        pytest.param(
            'PERMANENT',
            {
                'total': 9,
                'equals': 1,
                'temp_actual_approved': 6,
                'outdated_actual_approved': 2,
            },
            1,
            1,
            id='All perm',
        ),
        pytest.param(
            'TEMPORARY',
            {
                'total': 9,
                'equals': 1,
                'approved_actual_temp': 1,
                'outdated_restored': 2,
            },
            1,
            1,
            id='All temp',
        ),
        pytest.param(
            None, {'total': 9, 'invalid_binding': 9}, 1, 1, id='All invalid',
        ),
        pytest.param(
            'PERMANENT',
            {
                'total': 9,
                'equals': 1,
                'temp_actual_approved': 6,
                'outdated_actual_approved': 2,
            },
            11,
            11,
            marks=pytest.mark.config(
                DEPTRANS_DRIVER_STATUS_PROFILES_VALIDATOR_SETTINGS=_settings(
                    profiles_batch_size=1,
                ),
            ),
            id='All perm by single profile',
        ),
    ],
)
async def test_worker_enabled(
        taxi_deptrans_driver_status,
        taxi_deptrans_driver_status_monitor,
        testpoint,
        pgsql,
        pg_deptrans_driver_status,
        pg_deptrans_profile_status_logs,
        deptrans_profile,
        mocked_time,
        personal,
        unique_drivers,
        tags,
        deptrans_ais_krt,
        actual_status,
        metric_diff,
        personal_calls,
        licenses_calls,
):
    await taxi_deptrans_driver_status.tests_control(reset_metrics=True)

    if actual_status:
        for profile in deptrans_profile.get_all():
            license_id = utils.remove_dprlpr_in_license(
                profile.license_pd_id, profile.license_country,
            )
            deptrans_id = profile.checking_deptrans_id or profile.deptrans_id
            deptrans_ais_krt.add_license(deptrans_id, license_id)
            deptrans_ais_krt.add_driver_id_status(deptrans_id, actual_status)
            unique_drivers.add_license_mapping(
                profile.license_pd_id, f'udid_{deptrans_id}',
            )

    await _wait_iteration(taxi_deptrans_driver_status, testpoint, True)

    assert personal['bulk_retrieve'].times_called == personal_calls
    assert personal['bulk_retrieve_licenses'].times_called == licenses_calls
    assert deptrans_ais_krt.check_driver.times_called == 9

    mocked_time.sleep(60)
    await taxi_deptrans_driver_status.invalidate_caches()

    metrics = await taxi_deptrans_driver_status_monitor.get_metric(
        'profile_validator_stats',
    )
    assert metrics == _get_metrics(metric_diff)

    for profile in deptrans_profile.get_all():
        if profile.checking_deptrans_id:
            continue
        if actual_status:
            status = (
                'approved' if actual_status == 'PERMANENT' else 'temporary'
            )
            assert pg_deptrans_driver_status.get_deptrans_profile(
                profile.license_pd_id, pgsql,
            ) == (profile.deptrans_id, status, None)
            if status != profile.status:
                assert pg_deptrans_profile_status_logs.fetch_logs(
                    profile.license_pd_id, pgsql,
                ) == [(profile.license_pd_id, profile.deptrans_id, status)]
        else:
            status = 'failed'
            assert pg_deptrans_driver_status.get_deptrans_profile(
                profile.license_pd_id, pgsql,
            ) == (profile.deptrans_id, status, None)
            assert pg_deptrans_profile_status_logs.fetch_logs(
                profile.license_pd_id, pgsql,
            ) == [(profile.license_pd_id, profile.deptrans_id, status)]


@pytest.mark.now('2021-01-01T12:00:00+00:00')
@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_LICENSE_PREFIXES=utils.license_prefixes(),
    DEPTRANS_DRIVER_STATUS_SUPPORTED_COUNTRIES={
        'supported_countries': ['rus', 'oth', 'blr'],
    },
    DEPTRANS_DRIVER_STATUS_PROFILES_VALIDATOR_SETTINGS=_settings(),
    DEPTRANS_DRIVER_STATUS_PROFILE_TAGS={
        'approved': [],
        'temporary': [
            {'name': 'kis_art_temp_issued'},
            {'name': 'kis_art_temp', 'ttl': 2592000},
        ],
        'temporary_requested': [],
        'temporary_outdated': [],
        'failed': [],
    },
)
async def test_worker_import_date(
        taxi_deptrans_driver_status,
        taxi_deptrans_driver_status_monitor,
        testpoint,
        pgsql,
        deptrans_profile,
        mocked_time,
        personal,
        tags,
        unique_drivers,
        deptrans_ais_krt,
):
    await taxi_deptrans_driver_status.tests_control(reset_metrics=True)

    for profile in deptrans_profile.get_all():
        license_id = utils.remove_dprlpr_in_license(
            profile.license_pd_id, profile.license_country,
        )
        deptrans_id = profile.checking_deptrans_id or profile.deptrans_id
        deptrans_ais_krt.add_license(deptrans_id, license_id)
        deptrans_ais_krt.add_driver_id_status(deptrans_id, 'TEMPORARY')
        deptrans_ais_krt.add_import_date(
            deptrans_id, '2021-01-01T12:00:01.000+0300',
        )
        if profile.checking_deptrans_id is None:
            unique_drivers.add_license_mapping(
                profile.license_pd_id, f'udid_{deptrans_id}',
            )
            tags.add_tags(
                f'udid_{deptrans_id}',
                {'kis_art_temp_issued': {}, 'kis_art_temp': {'ttl': 2592000}},
            )

    await _wait_iteration(taxi_deptrans_driver_status, testpoint, True)

    assert personal['bulk_retrieve'].times_called == 1
    assert personal['bulk_retrieve_licenses'].times_called == 1
    assert unique_drivers.retrieve_by_license.times_called == 1
    assert tags.assign.times_called == 1
    assert deptrans_ais_krt.check_driver.times_called == 9

    mocked_time.sleep(60)
    await taxi_deptrans_driver_status.invalidate_caches()

    metrics = await taxi_deptrans_driver_status_monitor.get_metric(
        'profile_validator_stats',
    )
    assert metrics == _get_metrics(
        {'total': 9, 'approved_actual_temp': 1, 'outdated_restored': 2},
    )

    cursor = pgsql['deptrans_driver_status'].cursor()
    cursor.execute(
        'SELECT '
        'driver_license_pd_id, status, import_date '
        'FROM deptrans.profiles WHERE checking_deptrans_id IS NULL '
        'ORDER BY driver_license_pd_id',
    )
    assert [row for row in cursor] == [
        (
            profile.license_pd_id,
            'temporary',
            datetime.datetime(
                2021,
                1,
                1,
                12,
                0,
                1,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180),
            ),
        )
        for profile in deptrans_profile.get_all()
        if profile.checking_deptrans_id is None
    ]


@pytest.mark.now('2021-01-07T12:00:00+00:00')
@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_LICENSE_PREFIXES=utils.license_prefixes(),
    DEPTRANS_DRIVER_STATUS_SUPPORTED_COUNTRIES={
        'supported_countries': ['rus', 'oth', 'blr'],
    },
    DEPTRANS_DRIVER_STATUS_PROFILES_VALIDATOR_SETTINGS=_settings(),
    DEPTRANS_DRIVER_STATUS_TEMP_ACCOUNT_DAYS_TTL=5,
    DEPTRANS_DRIVER_STATUS_PROFILE_TAGS={
        'approved': [],
        'temporary': [],
        'temporary_requested': [],
        'temporary_outdated': [{'name': 'kis_art_temp_outdated'}],
        'failed': [],
    },
)
async def test_worker_outdated(
        taxi_deptrans_driver_status,
        taxi_deptrans_driver_status_monitor,
        testpoint,
        pgsql,
        mocked_time,
        personal,
        deptrans_profile,
        tags,
        unique_drivers,
        deptrans_ais_krt,
):
    await taxi_deptrans_driver_status.tests_control(reset_metrics=True)

    for profile in deptrans_profile.get_all():
        license_id = utils.remove_dprlpr_in_license(
            profile.license_pd_id, profile.license_country,
        )
        deptrans_id = profile.checking_deptrans_id or profile.deptrans_id
        deptrans_ais_krt.add_license(deptrans_id, license_id)
        deptrans_ais_krt.add_driver_id_status(deptrans_id, 'TEMPORARY')
        deptrans_ais_krt.add_import_date(
            deptrans_id, '2021-01-01T12:00:01.000+0300',
        )
        if profile.checking_deptrans_id is None:
            unique_drivers.add_license_mapping(
                profile.license_pd_id, f'udid_{deptrans_id}',
            )
            tags.add_tags(f'udid_{deptrans_id}', {'kis_art_temp_outdated': {}})

    await _wait_iteration(taxi_deptrans_driver_status, testpoint, True)

    assert personal['bulk_retrieve'].times_called == 1
    assert personal['bulk_retrieve_licenses'].times_called == 1
    assert unique_drivers.retrieve_by_license.times_called == 1
    assert tags.assign.times_called == 1
    assert deptrans_ais_krt.check_driver.times_called == 9

    mocked_time.sleep(60)
    await taxi_deptrans_driver_status.invalidate_caches()

    metrics = await taxi_deptrans_driver_status_monitor.get_metric(
        'profile_validator_stats',
    )
    assert metrics == _get_metrics(
        {'total': 9, 'approved_actual_temp': 1, 'temp_outdated': 6},
    )

    cursor = pgsql['deptrans_driver_status'].cursor()
    cursor.execute(
        'SELECT '
        'driver_license_pd_id, status, import_date '
        'FROM deptrans.profiles WHERE checking_deptrans_id IS NULL '
        'ORDER BY driver_license_pd_id',
    )
    assert [row for row in cursor] == [
        (
            profile.license_pd_id,
            'temporary_outdated',
            datetime.datetime(
                2021,
                1,
                1,
                12,
                0,
                1,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180),
            ),
        )
        for profile in deptrans_profile.get_all()
        if profile.checking_deptrans_id is None
    ]
