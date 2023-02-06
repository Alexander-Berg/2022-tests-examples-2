import pytest

from tests_deptrans_driver_status import utils


def _get_metrics(incremented_label):
    metrics = {
        'missing_profile': 0,
        'ids_mismatch': 0,
        'bind_for_temp_profile': 0,
        'already_approved': 0,
        'bind': 0,
        'unbind': 0,
        'bind_temp_as_approved': 0,
    }
    if incremented_label is not None:
        metrics[incremented_label] = 1
    return metrics


def _tags_for_status(driver_id_status, is_valid_bind):
    if not is_valid_bind:
        return {'kis_art_failed': {}}
    if driver_id_status == 'PERMANENT':
        return {'kis_art_approved': {}, 'kis_art_priority': {'ttl': 604800}}
    return {'kis_art_temp_issued': {}, 'kis_art_temp': {'ttl': 2592000}}


@pytest.mark.config(
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
        'failed': [{'name': 'kis_art_failed'}],
    },
    DEPTRANS_DRIVER_STATUS_TEMP_ACCOUNT_DAYS_TTL=5,
    DEPTRANS_DRIVER_STATUS_LICENSE_PREFIXES=utils.license_prefixes(),
    DEPTRANS_DRIVER_STATUS_SUPPORTED_COUNTRIES={
        'supported_countries': ['rus', 'oth', 'blr'],
    },
)
@pytest.mark.now('2021-01-01T12:00:00+00:00')
@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
@pytest.mark.parametrize(
    [
        'park_id',
        'driver_id',
        'requested_deptrans_id',
        'after_stq_deptrans_id',
        'driver_id_status',
        'import_date',
        'is_outdated',
        'updated_metric',
        'is_valid_bind',
        'skip_task',
    ],
    [
        pytest.param(
            'park4',
            'driver1',
            'some_id',
            'some_id',
            'PERMANENT',
            None,
            None,
            'bind',
            True,
            False,
            id='Valid Temp2Approved. Removing prefix DR',
        ),
        pytest.param(
            'park4',
            'driver2',
            'some_id',
            'some_id',
            'PERMANENT',
            None,
            None,
            'bind',
            True,
            False,
            id='Valid Temp2Approved. Not removing prefix LR',
        ),
        pytest.param(
            'park4',
            'driver3',
            'some_id',
            '13',
            'PERMANENT',
            None,
            None,
            None,
            False,
            False,
            id='Invalid Temp2Approved. No license country',
        ),
        pytest.param(
            'park4',
            'driver4',
            'some_id',
            '14',
            'PERMANENT',
            None,
            None,
            'bind_for_temp_profile',
            False,
            False,
            id='Invalid Temp2Approved. \'oth\' country, but no prefix',
        ),
        pytest.param(
            'park1',
            'driver2',
            '2',
            '2',
            'PERMANENT',
            None,
            None,
            'bind',
            True,
            False,
            id='Valid bind for new profile',
        ),
        pytest.param(
            'park1',
            'driver2',
            '2',
            '2',
            'PERMANENT',
            None,
            None,
            'unbind',
            False,
            False,
            id='Invalid bind for new profile',
        ),
        pytest.param(
            'park2',
            'driver2',
            '2',
            None,
            'PERMANENT',
            None,
            None,
            'missing_profile',
            True,
            True,
            id='Missing profile',
        ),
        pytest.param(
            'park1',
            'driver2',
            '3',
            '3',
            'PERMANENT',
            None,
            None,
            'ids_mismatch',
            True,
            True,
            id='ids missmatch when new profile',
        ),
        pytest.param(
            'park2',
            'driver1',
            '3',
            '3',
            'PERMANENT',
            None,
            None,
            'ids_mismatch',
            False,
            True,
            id="""ids missmatch because temporary profile
                   without checking_deptrans_id""",
        ),
        pytest.param(
            'park3',
            'driver4',
            'some_id',
            '8',
            'PERMANENT',
            None,
            None,
            'bind_for_temp_profile',
            False,
            False,
            id='Temp profile was not changed because invalid bind',
        ),
        pytest.param(
            'park3',
            'driver4',
            'some_id',
            'some_id',
            'TEMPORARY',
            None,
            False,
            'bind_temp_as_approved',
            True,
            False,
            id='Temp profile was changed to another temp because'
            ' valid bind without import_date',
        ),
        pytest.param(
            'park3',
            'driver4',
            'some_id',
            'some_id',
            'TEMPORARY',
            '2021-01-01T12:00:01.000+0300',
            False,
            'bind_temp_as_approved',
            True,
            False,
            id='Temp profile was changed to another temp because'
            ' valid bind with good import_date',
        ),
        pytest.param(
            'park3',
            'driver4',
            'some_id',
            '8',
            'TEMPORARY',
            '2020-01-01T12:00:01.000+0300',
            True,
            'bind_for_temp_profile',
            True,
            False,
            id='Temp profile was not changed to temp_outdated'
            ' because bad import_date',
        ),
        pytest.param(
            'park3',
            'driver4',
            'some_id',
            'some_id',
            'PERMANENT',
            None,
            None,
            'bind',
            True,
            False,
            id='Valid Temp2Approved',
        ),
        pytest.param(
            'park1',
            'driver1',
            '1',
            '1',
            'PERMANENT',
            None,
            None,
            'already_approved',
            True,
            True,
            id='Already approved',
        ),
        pytest.param(
            'park1',
            'driver2',
            '2',
            '2',
            'TEMPORARY',
            None,
            False,
            'bind_temp_as_approved',
            True,
            False,
            id='New temp without import_date',
        ),
        pytest.param(
            'park1',
            'driver2',
            '2',
            '2',
            'TEMPORARY',
            '2021-01-01T12:00:01.000+0300',
            False,
            'bind_temp_as_approved',
            True,
            False,
            id='New temp with good import_date',
        ),
        pytest.param(
            'park1',
            'driver2',
            '2',
            '2',
            'TEMPORARY',
            '2020-01-01T12:00:01.000+0300',
            True,
            'bind_temp_as_approved',
            True,
            False,
            id='New temp_outdated, because bad import_date',
        ),
        pytest.param(
            'park6',
            'driver1',
            'some_id',
            'some_id',
            'TEMPORARY',
            '2021-01-01T12:00:01.000+0300',
            False,
            'bind_temp_as_approved',
            True,
            False,
            id='New temp with good import_date. oth+prefix',
        ),
        pytest.param(
            'park6',
            'driver2',
            'some_id',
            'some_id',
            'TEMPORARY',
            '2021-01-01T12:00:01.000+0300',
            False,
            'bind_temp_as_approved',
            True,
            False,
            id='New temp with good import_date. rus+prefix',
        ),
        pytest.param(
            'park6',
            'driver3',
            'some_id',
            'some_id',
            'TEMPORARY',
            '2021-01-01T12:00:01.000+0300',
            False,
            None,
            False,
            False,
            id='New temp with good import_date. null+prefix',
        ),
        pytest.param(
            'park6',
            'driver4',
            'some_id',
            'some_id',
            'TEMPORARY',
            '2021-01-01T12:00:01.000+0300',
            False,
            'unbind',
            False,
            False,
            id='New temp with good import_date. oth',
        ),
    ],
)
async def test_binding(
        taxi_deptrans_driver_status,
        taxi_deptrans_driver_status_monitor,
        deptrans_ais_krt,
        client_notify,
        driver_profile,
        unique_drivers,
        tags,
        personal,
        mocked_time,
        pg_deptrans_driver_status,
        pg_deptrans_profile_status_logs,
        pgsql,
        stq_runner,
        park_id,
        driver_id,
        requested_deptrans_id,
        after_stq_deptrans_id,
        import_date,
        is_outdated,
        driver_id_status,
        updated_metric,
        is_valid_bind,
        skip_task,
):
    await taxi_deptrans_driver_status.tests_control(reset_metrics=True)

    profile = driver_profile(park_id, driver_id)
    license_pd_id = profile.license_pd_id
    license_id = utils.remove_dprlpr_in_license(
        profile.license_pd_id, profile.license_country,
    )

    initial_deptrans_profile = pg_deptrans_driver_status.get_deptrans_profile(
        license_pd_id, pgsql,
    )
    initial_status = (
        None
        if initial_deptrans_profile is None
        else initial_deptrans_profile[1]
    )

    deptrans_ais_krt.add_driver_id_status(
        requested_deptrans_id, driver_id_status,
    )
    if is_valid_bind:
        deptrans_ais_krt.add_license(requested_deptrans_id, license_id)
        if import_date:
            deptrans_ais_krt.add_import_date(
                requested_deptrans_id, import_date,
            )

    if is_outdated is not None and not is_outdated:
        tags.add_tags(
            'unique_driver_id_1',
            _tags_for_status(driver_id_status, is_valid_bind),
        )

    if profile.license_country is None:
        client_notify.set_message('null_country')
    elif not is_valid_bind:
        client_notify.set_message('bind_profile_fail')
    elif license_id == license_pd_id and profile.license_country == 'oth':
        client_notify.set_message('not_supported_country')
    else:
        if is_outdated and initial_status == 'temporary':
            client_notify.set_message('bind_temp_downgrade')
        elif updated_metric == 'bind_temp_as_approved':
            if is_outdated:
                client_notify.set_message('bind_temp_outdated_profile')
            else:
                client_notify.set_message('bind_temp_profile_successful')
        elif updated_metric == 'bind':
            client_notify.set_message('bind_profile_successful')

    await stq_runner.deptrans_driver_status_bind_ids.call(
        task_id='task_id',
        kwargs={
            'park_id': park_id,
            'driver_profile_id': driver_id,
            'deptrans_id': requested_deptrans_id,
            'taximeter_app': 'Taximeter 8.80 (562)',
            'accept_language': 'ru',
        },
        expect_fail=updated_metric == 'missing_profile',
    )

    mocked_time.sleep(60)
    await taxi_deptrans_driver_status.invalidate_caches()

    metrics = await taxi_deptrans_driver_status_monitor.get_metric(
        'bind_stats',
    )
    assert metrics == _get_metrics(updated_metric)

    if not skip_task:
        deptrans_driver_profile = (
            pg_deptrans_driver_status.get_deptrans_profile(
                license_pd_id, pgsql,
            )
        )
        assert client_notify.push.times_called == 1

        if is_valid_bind:
            if driver_id_status == 'PERMANENT':
                status = 'approved'
            elif is_outdated:
                status = 'temporary_outdated'
            else:
                status = 'temporary'

            if is_outdated and initial_status == 'temporary':
                assert deptrans_driver_profile == (
                    initial_deptrans_profile[0],
                    initial_deptrans_profile[1],
                    None,
                )
            else:
                assert deptrans_driver_profile == (
                    requested_deptrans_id,
                    status,
                    None,
                )
                assert tags.assign.times_called == 1
                assert pg_deptrans_profile_status_logs.fetch_logs(
                    license_pd_id, pgsql,
                ) == [(license_pd_id, requested_deptrans_id, status)]
        else:
            if initial_status:
                assert deptrans_driver_profile == (
                    after_stq_deptrans_id,
                    initial_status,
                    None,
                )
                assert (
                    pg_deptrans_profile_status_logs.fetch_logs(
                        license_pd_id, pgsql,
                    )
                    == []
                )
            else:
                assert deptrans_driver_profile is None
                assert pg_deptrans_profile_status_logs.fetch_logs(
                    license_pd_id, pgsql,
                ) == [(license_pd_id, after_stq_deptrans_id, 'invalidated')]


@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
async def test_fail(
        driver_profile, deptrans_ais_krt, unique_drivers, personal, stq_runner,
):
    deptrans_ais_krt.set_raise_error(True)
    license_pd_id = driver_profile('park1', 'driver2').license_pd_id
    deptrans_ais_krt.add_license('2', license_pd_id)

    await stq_runner.deptrans_driver_status_bind_ids.call(
        task_id='task_id',
        kwargs={
            'park_id': 'park1',
            'driver_profile_id': 'driver2',
            'deptrans_id': '2',
        },
        expect_fail=True,
    )
