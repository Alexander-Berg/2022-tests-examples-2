import datetime as dt
from typing import List

from tests_contractor_events_producer import geo_hierarchies
from tests_contractor_events_producer import online_events


def insert_online_events(events: List[online_events.OnlineDbEvent]):
    return (
        'INSERT INTO state.contractor_online_status '
        '(park_id, driver_id, status, updated_at) VALUES '
        + ', '.join(
            f'(\'{event.park_id}\', '
            f'\'{event.driver_id}\', '
            f' \'{event.status}\', '
            f'\'{event.updated_at.isoformat()}\')'
            for event in events
        )
        + ' ON CONFLICT (park_id, driver_id) DO UPDATE '
        + ' SET '
        + ' status = EXCLUDED.status, updated_at = EXCLUDED.updated_at '
        + ';'
    )


def insert_online_status_history(events: List[online_events.OnlineDbEvent]):
    return (
        'INSERT INTO state.contractor_online_events_outbox '
        '(park_id, driver_id, status, updated_at) VALUES '
        + ', '.join(
            f'(\'{event.park_id}\', '
            f'\'{event.driver_id}\', '
            f' \'{event.status}\', '
            f'\'{event.updated_at.isoformat()}\')'
            for event in events
        )
        + ';'
    )


def insert_geo_hierarchies(
        data: List[geo_hierarchies.GeoHierarchyDb], fetched_at=None,
):
    return f"""
        INSERT INTO
            state.contractor_geo_hierarchy (
                park_id,
                driver_id,
                geo_hierarchy_hash,
                updated_at,
                fetched_at
            )
        VALUES {
        ','.join(
            f'''
            (
                '{it.park_id}',
                '{it.driver_id}',
                '{it.geo_hierarchy_hash}',
                '{it.updated_at.isoformat()}',
                '{(fetched_at or it.updated_at).isoformat()}'
            )
            ''' for it in data
        )
        }
    """


def insert_geo_hierarchies_history(
        data: List[geo_hierarchies.GeoHierarchyOutboxDb],
):
    return f"""
        INSERT INTO
            state.contractor_geo_hierarchy_outbox (
                park_id,
                driver_id,
                geo_hierarchy,
                updated_at
            )
        VALUES {
        ','.join(
            f'''
            (
                '{it.park_id}',
                '{it.driver_id}',
                '{{{','.join(it.geo_hierarchy)}}}',
                '{it.updated_at.isoformat()}'
            )
            ''' for it in data
        )
        }
    """


def get_online_events(pgsql):
    cursor = pgsql['contractor_events_producer'].cursor()
    cursor.execute(
        'SELECT '
        'park_id, '
        'driver_id, '
        'status, '
        'updated_at AT TIME ZONE \'UTC\' '
        'FROM state.contractor_online_status '
        'ORDER BY park_id, driver_id',
    )
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append(
            online_events.OnlineDbEvent(
                row[0], row[1], row[2], row[3].replace(tzinfo=dt.timezone.utc),
            ),
        )
    return result


def get_geo_hierarchies(pgsql, should_sort=False):
    cursor = pgsql['contractor_events_producer'].cursor()
    cursor.execute(
        f"""
        SELECT
            park_id,
            driver_id,
            geo_hierarchy_hash,
            updated_at AT TIME ZONE 'UTC'
        FROM
            state.contractor_geo_hierarchy
        {'ORDER BY park_id, driver_id' if should_sort else ''}
        """,
    )
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append(
            geo_hierarchies.GeoHierarchyDb(
                row[0], row[1], row[2], row[3].replace(tzinfo=dt.timezone.utc),
            ),
        )
    return result


def get_online_events_in_outbox(pgsql):
    cursor = pgsql['contractor_events_producer'].cursor()
    cursor.execute(
        'SELECT '
        'park_id, '
        'driver_id, '
        'status, '
        'updated_at AT TIME ZONE \'UTC\' '
        'FROM state.contractor_online_events_outbox '
        'ORDER BY park_id, driver_id',
    )
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append(
            online_events.OnlineDbEvent(
                row[0], row[1], row[2], row[3].replace(tzinfo=dt.timezone.utc),
            ),
        )
    return result


def get_geo_hierarchies_in_outbox(pgsql, should_sort=False):
    cursor = pgsql['contractor_events_producer'].cursor()
    cursor.execute(
        f"""
        SELECT
            park_id,
            driver_id,
            geo_hierarchy,
            updated_at AT TIME ZONE 'UTC'
        FROM
            state.contractor_geo_hierarchy_outbox
        {'ORDER BY park_id, driver_id' if should_sort else ''}
        """,
    )
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append(
            geo_hierarchies.GeoHierarchyOutboxDb(
                row[0], row[1], row[2], row[3].replace(tzinfo=dt.timezone.utc),
            ),
        )
    return result
