import dataclasses
import datetime as dt
from typing import Any
from typing import List
from typing import Optional

from tests_segments_provider import launch_tools


@dataclasses.dataclass
class UploadState:
    total_append_table_rows: int
    total_remove_table_rows: int
    total_snapshot_table_rows: int
    processed_append_table_rows: int
    processed_remove_table_rows: int
    appended_tags: int
    removed_tags: int
    malformed_rows: int


@dataclasses.dataclass
class UploadTask:
    launch_uuid: str
    status: str
    is_failed: bool
    error_messages: List[str]
    started_at: dt.datetime
    upload_state: Optional[UploadState]


def get_insert_upload_task_query(task: UploadTask) -> str:
    strings_delimiter = '\',\''

    errors = (
        f'ARRAY[\'{strings_delimiter.join(task.error_messages)}\']'
        if task.error_messages
        else 'ARRAY[]::text[]'
    )

    launch_id = (
        f'(SELECT id FROM state.launches WHERE uuid = \'{task.launch_uuid}\')'
    )

    total_append_table_rows: Any = 'null'
    total_remove_table_rows: Any = 'null'
    total_snapshot_table_rows: Any = 'null'
    processed_append_table_rows: Any = 'null'
    processed_remove_table_rows: Any = 'null'
    appended_tags: Any = 'null'
    removed_tags: Any = 'null'
    malformed_rows: Any = 'null'
    if task.upload_state:
        total_append_table_rows = task.upload_state.total_append_table_rows
        total_remove_table_rows = task.upload_state.total_remove_table_rows
        total_snapshot_table_rows = task.upload_state.total_snapshot_table_rows
        processed_append_table_rows = (
            task.upload_state.processed_append_table_rows
        )
        processed_remove_table_rows = (
            task.upload_state.processed_remove_table_rows
        )
        appended_tags = task.upload_state.appended_tags
        removed_tags = task.upload_state.removed_tags
        malformed_rows = task.upload_state.malformed_rows

    query = f"""
        INSERT INTO state.tags_upload_tasks (
            launch_id,
            status,
            is_failed,
            error_messages,
            started_at,
            total_append_table_rows,
            total_remove_table_rows,
            total_snapshot_table_rows,
            processed_append_table_rows,
            processed_remove_table_rows,
            appended_tags,
            removed_tags,
            malformed_rows
        )
        VALUES (
            {launch_id},
            '{task.status}',
            {task.is_failed},
            {errors},
            '{task.started_at.isoformat()}',
            {total_append_table_rows},
            {total_remove_table_rows},
            {total_snapshot_table_rows},
            {processed_append_table_rows},
            {processed_remove_table_rows},
            {appended_tags},
            {removed_tags},
            {malformed_rows}
        )
    """
    return query


def insert_upload_task(pgsql, task: UploadTask):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(get_insert_upload_task_query(task))


def find_upload_task(pgsql, launch_uuid: str) -> UploadTask:
    launch_id = launch_tools.get_launch_id(pgsql, launch_uuid)

    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        SELECT
            launch_id,
            status,
            is_failed,
            error_messages,
            started_at,
            total_append_table_rows,
            total_remove_table_rows,
            total_snapshot_table_rows,
            processed_append_table_rows,
            processed_remove_table_rows,
            appended_tags,
            removed_tags,
            malformed_rows
        FROM state.tags_upload_tasks
        WHERE launch_id = {launch_id}
        """,
    )

    rows = []
    for row in cursor:
        launch_id = row[0]
        status = row[1]
        is_failed = row[2]
        error_messages = row[3]
        started_at = row[4]
        total_append_table_rows = row[5]
        total_remove_table_rows = row[6]
        total_snapshot_table_rows = row[7]
        processed_append_table_rows = row[8]
        processed_remove_table_rows = row[9]
        appended_tags = row[10]
        removed_tags = row[11]
        malformed_rows = row[12]
        upload_state: Optional[UploadState] = None

        if total_append_table_rows is not None:
            assert total_remove_table_rows is not None
            assert total_snapshot_table_rows is not None
            assert processed_append_table_rows is not None
            assert processed_remove_table_rows is not None
            assert appended_tags is not None
            assert removed_tags is not None
            assert malformed_rows is not None
            upload_state = UploadState(
                total_append_table_rows=total_append_table_rows,
                total_remove_table_rows=total_remove_table_rows,
                total_snapshot_table_rows=total_snapshot_table_rows,
                processed_append_table_rows=processed_append_table_rows,
                processed_remove_table_rows=processed_remove_table_rows,
                appended_tags=appended_tags,
                removed_tags=removed_tags,
                malformed_rows=malformed_rows,
            )
        else:
            assert total_remove_table_rows is None
            assert total_snapshot_table_rows is None
            assert processed_append_table_rows is None
            assert processed_remove_table_rows is None
            assert appended_tags is None
            assert removed_tags is None
            assert malformed_rows is None

        rows.append(
            UploadTask(
                launch_uuid=launch_uuid,
                status=status,
                is_failed=is_failed,
                error_messages=error_messages,
                started_at=started_at,
                upload_state=upload_state,
            ),
        )

    assert len(rows) == 1
    return rows[0]


@dataclasses.dataclass
class DiscardTask:
    launch_uuid: str
    total_snapshot_records: int
    processed_snapshot_records: int


def find_discard_task(pgsql, launch_uuid: str) -> DiscardTask:
    launch_id = launch_tools.get_launch_id(pgsql, launch_uuid)

    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        SELECT
            total_snapshot_records,
            processed_snapshot_records
        FROM state.tags_discard_tasks
        WHERE launch_id = {launch_id}
        """,
    )

    rows = [
        DiscardTask(
            launch_uuid=launch_uuid,
            total_snapshot_records=row[0],
            processed_snapshot_records=row[1],
        )
        for row in cursor
    ]

    assert len(rows) == 1
    return rows[0]


def find_discard_tasks(pgsql) -> List[DiscardTask]:
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        SELECT
            launches.uuid,
            tags_discard_tasks.total_snapshot_records,
            tags_discard_tasks.processed_snapshot_records
        FROM state.tags_discard_tasks
        JOIN state.launches
            ON tags_discard_tasks.launch_id = launches.id
        """,
    )

    return [
        DiscardTask(
            launch_uuid=row[0],
            total_snapshot_records=row[1],
            processed_snapshot_records=row[2],
        )
        for row in cursor
    ]


def get_insert_discard_task_query(task: DiscardTask) -> str:
    launch_id = (
        f'(SELECT id FROM state.launches WHERE uuid = \'{task.launch_uuid}\')'
    )

    query = f"""
        INSERT INTO state.tags_discard_tasks (
            launch_id,
            total_snapshot_records,
            processed_snapshot_records
        )
        VALUES (
            {launch_id},
            {task.total_snapshot_records},
            {task.processed_snapshot_records}
        )
    """
    return query


def insert_discard_task(pgsql, task: DiscardTask):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(get_insert_discard_task_query(task))
