import copy
import dataclasses
import datetime as dt
from typing import Any
from typing import List
from typing import Optional

import pytz


@dataclasses.dataclass
class RecordCounts:
    snapshot: int
    appended: int
    removed: int
    malformed: int


@dataclasses.dataclass
class Launch:
    uuid: str
    started_at: dt.datetime
    is_failed: bool
    status: str
    errors: List[str]
    snapshot_status: str
    record_counts: Optional[RecordCounts]

    def normalized_for_comparizon(self):
        result = copy.deepcopy(self)
        result.uuid = '00000000000000000000000000000000'
        result.started_at = result.started_at.astimezone(pytz.UTC)
        return result


def get_launch_insert_query(
        consumer_name: str, shipment_name: str, launch: Launch,
):
    strings_delimiter = '\',\''

    errors = (
        f'ARRAY[\'{strings_delimiter.join(launch.errors)}\']'
        if launch.errors
        else 'ARRAY[]::text[]'
    )

    snapshot_records_count: Any = 'null'
    appended_records_count: Any = 'null'
    removed_records_count: Any = 'null'
    malformed_records_count: Any = 'null'
    if launch.record_counts:
        snapshot_records_count = launch.record_counts.snapshot
        appended_records_count = launch.record_counts.appended
        removed_records_count = launch.record_counts.removed
        malformed_records_count = launch.record_counts.malformed

    query = f"""
        INSERT INTO state.launches (shipment_id, uuid, started_at, is_failed,
            status, error_messages, snapshot_status, snapshot_records_count,
            appended_records_count, removed_records_count,
            malformed_records_count)
        SELECT
            shipments.id,
            '{launch.uuid}',
            '{launch.started_at.isoformat()}',
            {launch.is_failed},
            '{launch.status}',
            {errors},
            '{launch.snapshot_status}',
            {snapshot_records_count},
            {appended_records_count},
            {removed_records_count},
            {malformed_records_count}
        FROM config.shipments
        JOIN config.consumers ON shipments.consumer_id = consumers.id
        WHERE shipments.name = '{shipment_name}'
          AND consumers.name = '{consumer_name}'
    """
    return query


def insert_launch(
        pgsql, consumer_name: str, shipment_name: str, launch: Launch,
):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        get_launch_insert_query(
            consumer_name=consumer_name,
            shipment_name=shipment_name,
            launch=launch,
        ),
    )
    assert cursor.rowcount == 1, (
        'Launch not inserted, probably no shipment '
        f'{shipment_name} for consumer {consumer_name}'
    )


def fetch_launches(pgsql, consumer_name: str, shipment_name: str):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        SELECT
            launches.uuid,
            launches.started_at::timestamptz,
            launches.is_failed,
            launches.status,
            launches.error_messages,
            launches.snapshot_status,
            launches.snapshot_records_count,
            launches.appended_records_count,
            launches.removed_records_count,
            launches.malformed_records_count
        FROM state.launches
        JOIN config.shipments ON launches.shipment_id = shipments.id
        JOIN config.consumers ON shipments.consumer_id = consumers.id
        WHERE shipments.name = '{shipment_name}'
          AND consumers.name = '{consumer_name}'
        ORDER BY launches.started_at, launches.uuid
        """,
    )
    rows = []
    for row in cursor:
        uuid = row[0]
        started_at = row[1]
        is_failed = row[2]
        status = row[3]
        error_messages = row[4]
        snapshot_status = row[5]
        snapshot_records_count = row[6]
        appended_records_count = row[7]
        removed_records_count = row[8]
        malformed_records_count = row[9]
        record_counts: Optional[RecordCounts] = None

        if snapshot_records_count is not None:
            assert appended_records_count is not None
            assert removed_records_count is not None
            assert malformed_records_count is not None
            record_counts = RecordCounts(
                snapshot=snapshot_records_count,
                appended=appended_records_count,
                removed=removed_records_count,
                malformed=malformed_records_count,
            )
        else:
            assert appended_records_count is None
            assert removed_records_count is None
            assert malformed_records_count is None
        rows.append(
            Launch(
                uuid=uuid,
                started_at=started_at,
                is_failed=is_failed,
                status=status,
                errors=error_messages,
                snapshot_status=snapshot_status,
                record_counts=record_counts,
            ),
        )
    return rows


def get_launch_id(pgsql, launch_uuid: str):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        SELECT id FROM state.launches WHERE uuid = '{launch_uuid}'
        """,
    )
    rows = [row[0] for row in cursor]
    assert len(rows) == 1
    return rows[0]
