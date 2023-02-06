import datetime
import json

import pytest


def convert_datetime_to_yt_format(timestamp: str) -> str:
    return datetime.datetime.strptime(
        timestamp, '%Y-%m-%dT%H:%M:%S%z',
    ).strftime('%Y-%m-%d %H:%M:%S')


NOW = datetime.datetime.now(datetime.timezone.utc)

GEOJSON_DEFAULT = (
    '{"coordinates": [[[30.301934,59.898485],[30.302144,59.897809], [30.301418,59.897801],'  # noqa: E501
    '[30.301323,59.898107], [30.301608,59.898129],[30.301574,59.898242], [30.301451,59.898232],'  # noqa: E501
    '[30.301386,59.898442], [30.301934,59.898485]]], "type": "Polygon"}'  # noqa: E501
)

SYNC_SETTINGS_CONFIG = {
    'enabled': True,
    'chunk_size': 10,
    'yt_read_timeout': 3000,
    'sync_period_seconds': 60,
    'yt_table_path': '//home/testsuite/geooffer_zones_raw',
}


@pytest.mark.config(
    GROCERY_DELIVERY_CONDITIONS_GEOOFFER_SYNC_SETTINGS=SYNC_SETTINGS_CONFIG,
)
@pytest.mark.yt(
    schemas=['yt_geooffer_zones_raw_schema.yaml'],
    dyn_table_data=['yt_geooffer_zones_raw_basic.yaml'],
)
@pytest.mark.now(NOW.isoformat())
async def test_basic(taxi_grocery_delivery_conditions, yt_apply, pgsql):
    await taxi_grocery_delivery_conditions.invalidate_caches()

    await taxi_grocery_delivery_conditions.run_periodic_task(
        'sync_geooffer_zones-periodic',
    )

    cursor = pgsql['grocery_delivery_conditions'].cursor()
    cursor.execute(
        'SELECT * FROM grocery_delivery_conditions.geooffer_zones', (),
    )
    rows = cursor.fetchall()

    dt_ts = datetime.datetime.fromtimestamp(
        1647000373 / 1000.0, tz=datetime.timezone.utc,
    )

    assert len(rows) == 2
    assert rows == [
        ('1', '271', GEOJSON_DEFAULT, 'active', dt_ts, dt_ts),
        ('2', '272', GEOJSON_DEFAULT, 'inactive', dt_ts, dt_ts),
    ]

    cursor.execute(
        """
            SELECT meta_cursor FROM grocery_delivery_conditions.cursors WHERE table_name = %s;
        """,  # noqa: E501
        ('geooffer_zones',),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0] == ({'last_id': 2, 'last_update': 1647000373},)


@pytest.mark.config(
    GROCERY_DELIVERY_CONDITIONS_GEOOFFER_SYNC_SETTINGS=SYNC_SETTINGS_CONFIG,
)
@pytest.mark.yt(
    schemas=['yt_geooffer_zones_raw_schema.yaml'],
    dyn_table_data=['yt_geooffer_zones_raw_update.yaml'],
)
@pytest.mark.now(NOW.isoformat())
async def test_update(taxi_grocery_delivery_conditions, yt_apply, pgsql):
    cursor = pgsql['grocery_delivery_conditions'].cursor()
    meta_cursor = json.dumps({'last_update': 1647000374, 'last_id': 1})
    cursor.execute(
        'INSERT INTO grocery_delivery_conditions.cursors(table_name, meta_cursor)'  # noqa: E501
        'VALUES (%s, %s)',
        ('geooffer_zones', meta_cursor),
    )

    await taxi_grocery_delivery_conditions.invalidate_caches()
    await taxi_grocery_delivery_conditions.run_periodic_task(
        'sync_geooffer_zones-periodic',
    )

    cursor.execute(
        'SELECT * FROM grocery_delivery_conditions.geooffer_zones', (),
    )
    rows = cursor.fetchall()

    updated_ts = datetime.datetime.fromtimestamp(
        1650600373 / 1000.0, tz=datetime.timezone.utc,
    )
    created_ts = datetime.datetime.fromtimestamp(
        1647000373 / 1000.0, tz=datetime.timezone.utc,
    )

    assert len(rows) == 1
    assert rows == [
        ('2', '272', GEOJSON_DEFAULT, 'inactive', updated_ts, created_ts),
    ]

    cursor.execute(
        """
            SELECT meta_cursor FROM grocery_delivery_conditions.cursors WHERE table_name = %s;
        """,  # noqa: E501
        ('geooffer_zones',),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0] == ({'last_id': 2, 'last_update': 1650600373},)


@pytest.mark.config(
    GROCERY_DELIVERY_CONDITIONS_GEOOFFER_SYNC_SETTINGS=SYNC_SETTINGS_CONFIG,
)
@pytest.mark.yt(
    schemas=['yt_geooffer_zones_raw_schema.yaml'],
    dyn_table_data=['yt_geooffer_zones_raw_update_deleted.yaml'],
)
@pytest.mark.now(NOW.isoformat())
async def test_update_deleted(
        taxi_grocery_delivery_conditions, yt_apply, pgsql,
):
    cursor = pgsql['grocery_delivery_conditions'].cursor()
    meta_cursor = json.dumps({'last_update': 1647000374, 'last_id': 1})
    cursor.execute(
        'INSERT INTO grocery_delivery_conditions.cursors(table_name, meta_cursor)'  # noqa: E501
        'VALUES (%s, %s)',
        ('geooffer_zones', meta_cursor),
    )

    await taxi_grocery_delivery_conditions.invalidate_caches()
    await taxi_grocery_delivery_conditions.run_periodic_task(
        'sync_geooffer_zones-periodic',
    )

    cursor.execute(
        'SELECT * FROM grocery_delivery_conditions.geooffer_zones', (),
    )
    rows = cursor.fetchall()

    updated_ts = datetime.datetime.fromtimestamp(
        1650600373 / 1000.0, tz=datetime.timezone.utc,
    )
    created_ts = datetime.datetime.fromtimestamp(
        1647000373 / 1000.0, tz=datetime.timezone.utc,
    )

    assert len(rows) == 1
    assert rows == [
        ('2', '272', GEOJSON_DEFAULT, 'deleted', updated_ts, created_ts),
    ]

    cursor.execute(
        """
            SELECT meta_cursor FROM grocery_delivery_conditions.cursors WHERE table_name = %s;
        """,  # noqa: E501
        ('geooffer_zones',),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0] == ({'last_id': 2, 'last_update': 1650600373},)
