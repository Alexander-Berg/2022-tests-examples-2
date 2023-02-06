import datetime as dt
import json
from typing import Any
from typing import Dict
from typing import Optional

from tests_driver_mode_subscription import driver


def get_scheduled_slots_meta(pgsql, slot_name: str):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        """
        SELECT slot_name, closed_at
        FROM booking.scheduled_slots_meta
        WHERE slot_name = %s
        """,
        (slot_name,),
    )
    rows = list(row for row in cursor)
    return rows


def get_scheduled_slots(pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        """
        SELECT
        name,
        starts_at,
        stops_at,
        mode,
        mode_settings
        FROM booking.scheduled_slots
        ORDER BY name, mode
        """,
    )
    rows = list(row for row in cursor)
    return rows


def get_reservations_by_slot(pgsql, slot_name: str, is_deleted: bool = False):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        """
        SELECT s.name, s.starts_at, s.stops_at,
        s.mode, s.mode_settings, q.name, q.count,
        r.accepted_mode_settings
        FROM booking.scheduled_slots s
        JOIN booking.scheduled_slots_reservations r ON s.id=r.slot_id
        JOIN booking.scheduled_slots_quotas q ON s.quota_id = q.id
        WHERE s.name = %s
        AND r.is_deleted = %s ORDER BY s.name
        """,
        (slot_name, is_deleted),
    )
    rows = list(row for row in cursor)
    return rows


def get_reservations_by_profile(
        pgsql, driver_profile: driver.Profile, is_deleted: bool = False,
):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        """
        SELECT s.name, s.starts_at, s.stops_at,
        s.mode, s.mode_settings, q.name, q.count,
        r.accepted_mode_settings, r.deletion_reason
        FROM booking.scheduled_slots s
        JOIN booking.scheduled_slots_reservations r ON s.id=r.slot_id
        JOIN booking.scheduled_slots_quotas q ON s.quota_id = q.id
        WHERE r.park_id = %s
        AND r.driver_id = %s AND r.is_deleted = %s ORDER BY s.name
        """,
        (driver_profile.park_id(), driver_profile.profile_id(), is_deleted),
    )
    rows = list(row for row in cursor)
    return rows


def make_update_slot_quota_query(
        quota_name: str, count: int, created_at: Optional[dt.datetime] = None,
):
    created_at_field = '' if created_at is None else ', created_at'
    created_at_value = (
        '' if created_at is None else f', \'{created_at.isoformat()}\''
    )

    return (
        'INSERT INTO booking.scheduled_slots_quotas '
        f'(name, count{created_at_field}) VALUES (\'{quota_name}\', '
        f'\'{count}\'{created_at_value})'
        ' ON CONFLICT (name) DO UPDATE '
        ' SET '
        ' count = excluded.count '
        ';'
    )


def make_insert_slot_quota_query(
        name: str,
        mode: str,
        mode_settings: Dict[str, Any],
        starts_at: dt.datetime,
        stops_at: dt.datetime,
        quota_name: str,
        quota_count: int,
        updated_ts: Optional[dt.datetime] = None,
):
    upsert_quota_query = f"""
        INSERT INTO booking.scheduled_slots_quotas (name, count)
        VALUES ('{quota_name}', '{quota_count}')
        ON CONFLICT (name) DO UPDATE
        SET count = excluded.count
        RETURNING id
        """

    updated_ts_field = '' if updated_ts is None else ', updated_ts'
    updated_ts_value = (
        '' if updated_ts is None else f',\'{updated_ts.isoformat()}\''
    )

    return (
        f'WITH quota AS ({upsert_quota_query}) '
        'INSERT INTO booking.scheduled_slots '
        f'(quota_id, name,  mode, mode_settings, '
        f'starts_at, stops_at{updated_ts_field}) '
        f'VALUES ((SELECT id FROM quota), \'{name}\', \'{mode}\', '
        f'\'{json.dumps(mode_settings)}\', '
        f'\'{starts_at.isoformat()}\', \'{stops_at.isoformat()}\''
        f'{updated_ts_value})'
    )


def make_insert_slot_meta_query(
        slot_name: str,
        closed_at: Optional[dt.datetime] = None,
        created_at: Optional[dt.datetime] = None,
):
    closed_at_db = f'\'{closed_at.isoformat()}\'' if closed_at else 'NULL'

    created_at_field = '' if created_at is None else 'created_at, '
    created_at_value = f'\'{created_at.isoformat()}\', ' if created_at else ''
    return f"""
        INSERT INTO booking.scheduled_slots_meta
        (slot_name, {created_at_field}closed_at)
        VALUES ('{slot_name}', {created_at_value}{closed_at_db})
        """


def make_insert_reservation_query(
        slot_name: str,
        mode: str,
        mode_settings: Optional[Dict[str, Any]],
        accepted_mode_settings: Optional[Dict[str, Any]],
        starts_at: dt.datetime,
        stops_at: dt.datetime,
        quota_name: str,
        quota_count: int,
        park_id: str,
        driver_id: str,
        is_deleted: bool = False,
):
    upsert_quota_query = f"""
        INSERT INTO booking.scheduled_slots_quotas (name, count)
        VALUES ('{quota_name}', '{quota_count}')
        ON CONFLICT (name) DO UPDATE
        SET count = excluded.count
        RETURNING id
        """
    upsert_slot_query = f"""
        INSERT INTO booking.scheduled_slots
        (quota_id, name,  mode, mode_settings, starts_at, stops_at)
        VALUES ((SELECT id FROM quota), '{slot_name}', '{mode}',
        {"'" + json.dumps(mode_settings) + "'"
        if mode_settings is not None else 'NULL'},
        '{starts_at.isoformat()}',
        '{stops_at.isoformat()}') RETURNING id
        """
    return f"""
        WITH quota AS ({upsert_quota_query}),
        slot AS ({upsert_slot_query})
        INSERT INTO booking.scheduled_slots_reservations
        (slot_id, park_id, driver_id, accepted_mode_settings, is_deleted)
        VALUES ((SELECT id FROM slot),
        '{park_id}', '{driver_id}',
        {"'" + json.dumps(accepted_mode_settings) + "'"
        if accepted_mode_settings is not None else 'NULL'},'
        {is_deleted}')
        """


def get_scheduled_quota(pgsql, name: str):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'SELECT q.name, q.count '
        'FROM booking.scheduled_slots_quotas q '
        f'WHERE q.name = \'{name}\'',
    )
    rows = list(row for row in cursor)
    return rows


def make_slot_reservation_query(
        mode: str,
        slot_name: str,
        driver_profile: driver.Profile,
        is_deleted: bool = False,
        updated_ts: Optional[dt.datetime] = None,
        deletion_reason: Optional[str] = None,
        created_at: Optional[dt.datetime] = None,
        accepted_mode_settings: Optional[Dict[str, Any]] = None,
):

    select_slot_query = f"""
        SELECT id from booking.scheduled_slots
        WHERE mode = '{mode}' AND name = '{slot_name}'
    """

    updated_ts_field = '' if updated_ts is None else ', updated_ts'
    updated_ts_value = (
        '' if updated_ts is None else f',\'{updated_ts.isoformat()}\''
    )

    created_at_field = '' if created_at is None else ', created_at'
    created_at_value = (
        '' if created_at is None else f',\'{created_at.isoformat()}\''
    )

    deletion_reason_str = (
        f'\'{deletion_reason}\'' if deletion_reason else 'null'
    )

    accepted_mode_settings_str = (
        f'\'{json.dumps(accepted_mode_settings)}\''
        if accepted_mode_settings
        else 'NULL'
    )

    return f"""
        WITH slot AS ({select_slot_query})
        INSERT INTO booking.scheduled_slots_reservations
        (slot_id, park_id, driver_id, is_deleted, deletion_reason,
        accepted_mode_settings
        {updated_ts_field} {created_at_field})
        VALUES
        ((SELECT id FROM slot),
        '{driver_profile.park_id()}',
        '{driver_profile.profile_id()}',
        '{is_deleted}',
        {deletion_reason_str},
        {accepted_mode_settings_str}
        {updated_ts_value}
        {created_at_value})
    """


def get_processed_events(pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        """
        SELECT reservation_id, event_type, processed_at
        FROM booking.scheduled_slots_processed_events
        """,
    )
    rows = list(row for row in cursor)
    return rows
