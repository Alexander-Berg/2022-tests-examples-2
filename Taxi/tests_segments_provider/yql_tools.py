import dataclasses
import datetime as dt
from typing import List
from typing import Optional

from tests_segments_provider import launch_tools


def _optional_text_value(text: Optional[str]):
    return f'\'{text}\'' if text else 'null'


def _optional_datetime_value(value: Optional[dt.datetime]):
    return f'\'{value.isoformat()}\'' if value else 'null'


@dataclasses.dataclass
class YqlTask:
    launch_uuid: str
    status: str
    started_at: dt.datetime
    error_messages: List[str]
    operation_id: Optional[str] = None
    operation_started_at: Optional[dt.datetime] = None
    operation_finished_at: Optional[dt.datetime] = None
    is_failed: bool = False


def get_insert_yql_task_query(task: YqlTask):
    strings_delimiter = '\',\''

    errors = (
        f'ARRAY[\'{strings_delimiter.join(task.error_messages)}\']'
        if task.error_messages
        else 'ARRAY[]::text[]'
    )

    launch_id = (
        f'(SELECT id FROM state.launches WHERE uuid = \'{task.launch_uuid}\')'
    )

    query = f"""
        INSERT INTO state.yql_tasks (launch_id, status, started_at,
            operation_id, operation_started_at, is_failed, error_messages)
        VALUES (
            {launch_id},
            '{task.status}',
            '{task.started_at.isoformat()}',
            {_optional_text_value(task.operation_id)},
            {_optional_datetime_value(task.operation_started_at)},
            {str(task.is_failed)},
            {errors})
    """
    return query


def find_yql_task(pgsql, launch_uuid: str):
    launch_id = launch_tools.get_launch_id(pgsql, launch_uuid)

    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        SELECT
            yql_tasks.launch_id,
            yql_tasks.status,
            yql_tasks.started_at,
            yql_tasks.operation_id,
            yql_tasks.operation_started_at,
            yql_tasks.operation_finished_at,
            yql_tasks.is_failed,
            yql_tasks.error_messages
        FROM state.yql_tasks
        WHERE yql_tasks.launch_id = {launch_id}
        """,
    )

    rows = [
        YqlTask(
            launch_uuid=launch_uuid,
            status=row[1],
            started_at=row[2],
            operation_id=row[3],
            operation_started_at=row[4],
            operation_finished_at=row[5],
            is_failed=row[6],
            error_messages=row[7],
        )
        for row in cursor
    ]

    rows_count = len(rows)
    assert rows_count <= 1
    if rows_count == 1:
        return rows[0]
    return None
