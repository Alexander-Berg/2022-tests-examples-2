import datetime as dt
import hashlib
import json
from typing import Any
from typing import Dict
from typing import Optional

from tests_driver_mode_subscription import driver

COMPENSATION_POLICY_ALLOW = 'allow'
COMPENSATION_POLICY_FORBID = 'forbid'


SAGA_STATUS_EXECUTED = 'executed'
SAGA_STATUS_COMPENSATED = 'compensated'

SOURCE_MANUAL_MODE_CHANGE = 'manual_mode_change'
SOURCE_SERVICE_MODE_CHANGE = 'service_mode_change'
SOURCE_SERVICE_MODE_RESET = 'service_mode_reset'
SOURCE_SUBSCRIPTION_SAGA = 'subscription_saga'
SOURCE_SUBSCRIPTION_SYNC = 'subscription_sync'
SOURCE_FLEET_MODE_CHANGE = 'fleet_mode_change'
SOURCE_SCHEDULED_MODE_CHANGE = 'scheduled_mode_reset'
SOURCE_LOGISTIC_WORKSHIFT_STOP = 'logistic_workshift_stop'
SOURCE_LOGISTIC_WORKSHIFT_START = 'logistic_workshift_start'

REASON_SCHEDULED_SLOT_STOP = 'scheduled_slot_stop'
REASON_SCHEDULED_SLOT_RESUBSCRIBE = 'scheduled_slot_resubscribe'
REASON_CURRENT_MODE_UNAVAILABLE = 'current_mode_unavailable'

SAGA_SETTINGS_ENABLE_COMPENSATION = {
    'enable_saga_persistent': True,
    'allow_saga_compensation': True,
}

SAGA_SETTINGS_ENABLE_FAILED_COMPENSATION = {
    'enable_saga_persistent': True,
    'allow_saga_compensation': True,
    'compensate_failed_saga_timeout_s': 1,
}


def has_saga(profile: driver.Profile, pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        f"""SELECT id FROM state.sagas
         WHERE park_id = '{profile.park_id()}'
         AND driver_id = '{profile.profile_id()}';""",
    )
    rows = list(row for row in cursor)
    return len(rows) == 1


def get_saga_statuses(pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        """SELECT saga_id, status
           FROM state.saga_results ORDER BY saga_id""",
    )
    rows = list(row for row in cursor)
    return rows


def get_saga_statuses_with_tokens(pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        """SELECT saga_id, status, park_id, driver_id, mode_change_token
           FROM state.saga_results ORDER BY saga_id""",
    )
    rows = list(row for row in cursor)
    return rows


def delete_sagas(pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute('delete FROM state.sagas returning id')
    rows = list(row for row in cursor)
    return rows


def insert_saga_status(
        saga_id: int,
        status: str,
        profile: driver.Profile,
        mode_change_token: str,
        created_at: dt.datetime,
        pgsql,
):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        f"""INSERT INTO state.saga_results (saga_id, status, park_id, driver_id,
                                            mode_change_token, created_at)
         VALUES ({saga_id},'{status}',
                '{profile.park_id()}','{profile.profile_id()}',
                '{mode_change_token}', '{created_at.isoformat()}')""",
    )


def make_insert_saga_query(
        park_id: str,
        driver_id: str,
        next_mode: str,
        next_mode_timepoint: str,
        next_mode_settings: Optional[Dict[str, Any]],
        prev_mode: Optional[str] = None,
        prev_mode_timepoint: Optional[str] = None,
        prev_mode_settings: Optional[Dict[str, Any]] = None,
        source: str = SOURCE_MANUAL_MODE_CHANGE,
        change_reason: Optional[str] = None,
        started_at: Optional[dt.datetime] = None,
):
    change_reason_str = f'\'{change_reason }\'' if change_reason else 'null'

    legacy_created_at_default = '2020-05-16'
    started_at_str = (
        started_at.isoformat() if started_at else legacy_created_at_default
    )

    next_mode_settings_value = (
        f'\'{json.dumps(next_mode_settings)}\''
        if next_mode_settings
        else 'null'
    )

    prev_mode_value = f'\'{prev_mode}\'' if prev_mode else 'null'
    prev_mode_timepoint_value = (
        f'\'{prev_mode_timepoint}\'' if prev_mode_timepoint else 'null'
    )
    prev_mode_settings_value = (
        f'\'{json.dumps(prev_mode_settings)}\''
        if prev_mode_settings
        else 'null'
    )

    return f"""
        INSERT INTO state.sagas
        (started_at, park_id, driver_id, unique_driver_id,
         next_mode, next_mode_timepoint, next_mode_settings,
         prev_mode, prev_mode_timepoint, prev_mode_settings,
         external_ref, accept_language, compensation_policy,
         source, change_reason)
        VALUES
        ('{started_at_str}', '{park_id}', '{driver_id}', 'udi1',
         '{next_mode}','{next_mode_timepoint}',
         {next_mode_settings_value},
         {prev_mode_value}, {prev_mode_timepoint_value},
         {prev_mode_settings_value},
         'some_unique_key', 'ru', 'allow', '{source}',{change_reason_str});
        """


def get_all_sagas_db_data(pgsql, profile: Optional[driver.Profile] = None):
    if profile:
        condition_str = (
            f'WHERE park_id = \'{profile.park_id()}\' and '
            f'driver_id = \'{profile.profile_id()}\';'
        )
    else:
        condition_str = ''
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'SELECT id, '
        'started_at AT TIME ZONE \'UTC\','
        'park_id,'
        'driver_id,'
        'unique_driver_id,'
        'next_mode,'
        'next_mode_timepoint AT TIME ZONE \'UTC\','
        'next_mode_settings,'
        'external_ref,'
        'accept_language, '
        'lock_id, '
        'compensation_policy, '
        'source, '
        'change_reason '
        f'FROM state.sagas {condition_str}',
    )
    rows = list(row for row in cursor)
    return rows


def get_saga_db_data(profile: driver.Profile, pgsql):
    rows = get_all_sagas_db_data(pgsql, profile)
    assert len(rows) == 1
    return rows[0]


def saga_prev_mode(profile: driver.Profile, pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'SELECT prev_mode, prev_mode_timepoint AT TIME ZONE \'UTC\','
        ' prev_mode_settings FROM state.sagas '
        f'WHERE park_id = \'{profile.park_id()}\' '
        f'and driver_id = \'{profile.profile_id()}\';',
    )
    return cursor.fetchone()


def get_saga_context(profile: driver.Profile, pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'SELECT context FROM state.sagas '
        f'WHERE park_id = \'{profile.park_id()}\' '
        f'AND driver_id = \'{profile.profile_id()}\';',
    )
    return cursor.fetchone()[0]


def get_saga_steps_db_data(pgsql, saga_id: int):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'SELECT name, '
        'execution_status, '
        'compensation_status '
        'FROM state.saga_steps '
        f'WHERE saga_id = {saga_id} ORDER BY name ASC ',
    )
    rows = list(row for row in cursor)
    return rows


def build_saga_args_raw(dbid: str, driver_profile_id: str):
    return {'dbid': dbid, 'uuid': driver_profile_id}


def build_saga_kwargs_raw(dbid: str, driver_profile_id: str):
    return {'dbid_uuid': build_saga_args_raw(dbid, driver_profile_id)}


def build_saga_kwargs(profile: driver.Profile):
    return build_saga_kwargs_raw(profile.park_id(), profile.profile_id())


async def call_stq_saga_task(
        stq_runner, profile: driver.Profile, expect_fail: bool = False,
):
    await stq_runner.subscription_saga.call(
        task_id=profile.dbid_uuid(),
        kwargs=build_saga_kwargs(profile),
        expect_fail=expect_fail,
    )


def get_compensation_policy(set_by_session: bool):
    if set_by_session:
        return COMPENSATION_POLICY_ALLOW

    return COMPENSATION_POLICY_FORBID


def get_saga_source(set_by_session: bool):
    if set_by_session:
        return SOURCE_MANUAL_MODE_CHANGE

    return SOURCE_SERVICE_MODE_CHANGE


_SALT_GENERIC_STEP = '55e9811ed5c6476c83675d7baa2c4d5f'


def make_idempotency_key(saga_id: int, step_name: str, is_compensation: bool):
    key = _SALT_GENERIC_STEP + str(saga_id) + step_name
    key += 'compensate' if is_compensation else 'execute'
    return hashlib.sha256(key.encode('ascii')).hexdigest()
