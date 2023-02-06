import copy
import datetime as dt
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest
import pytz

from tests_segments_provider import launch_tools
from tests_segments_provider import shipment_tools
from tests_segments_provider import tags_tools
from tests_segments_provider import yql_tools
from tests_segments_provider import yt_tools


_TZ_MOSCOW = pytz.timezone('Europe/Moscow')

_CREATED_AT = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 15, 0, 0))
_UPDATED_AT = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 16, 0, 0))
_NOW = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 15, 0, 5))
_NOW_MINUS_1_HOUR = _NOW - dt.timedelta(hours=1)
_NOW_PLUS_10_SEC = _NOW + dt.timedelta(seconds=10)

# sha256(tags.shipment_name)
_TASK_ID = '85335d4133d28c3b1b163aac8387bae71c4ff0d7c957216332b050cec58c8bf0'


_SHIPMENT = shipment_tools.DbShipment(
    name='shipment_name',
    ticket='A-2',
    maintainers=['developer'],
    is_enabled=True,
    labels=['CLICKHOUSE', 'passenger-tags'],
    schedule=shipment_tools.Schedule(
        start_at=_NOW, unit=shipment_tools.UnitOfTime.MINUTES, count=5,
    ),
    source=shipment_tools.YqlQuery(
        shipment_tools.YqlSyntax.CLICKHOUSE, 'SELECT 2',
    ),
    consumer=shipment_tools.TagsConsumerSettings(['tag3']),
    created_at=_CREATED_AT,
    updated_at=_UPDATED_AT,
    status=shipment_tools.Status.RUNNING,
    last_modifier='loginef',
)

_PREV_LAUNCH_UUID = 'd4b9b6c69076402982f75872535b426e'
_CURRENT_LAUNCH_UUID = 'cb6cd0434a674845940cd9137d8ff73b'

_SNAPSHOT_TABLE = yt_tools.YtTable(
    launch_uuid=_CURRENT_LAUNCH_UUID,
    alias='snapshot',
    path='//path/to/yt',
    lifespan='persistent',
    is_marked_for_deletion=False,
)
_APPEND_TABLE = yt_tools.YtTable(
    launch_uuid=_CURRENT_LAUNCH_UUID,
    alias='append',
    path='//path/to/yt',
    lifespan='till_end_of_launch',
    is_marked_for_deletion=False,
)


def _marked_for_deletion(table: yt_tools.YtTable):
    result = copy.deepcopy(table)
    result.is_marked_for_deletion = True
    return result


_STQ_RESCHEDULE_NOW = {
    'args': None,
    'eta': _NOW.astimezone(pytz.UTC).replace(tzinfo=None),
    'kwargs': None,
    'queue': 'segments_shipment',
    'id': _TASK_ID,
}

_STQ_RESCHEDULE_10_SEC = {
    'args': None,
    'eta': _NOW_PLUS_10_SEC.astimezone(pytz.UTC).replace(tzinfo=None),
    'kwargs': None,
    'queue': 'segments_shipment',
    'id': _TASK_ID,
}


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags',
            _SHIPMENT,
            tag_provider_name_override='seagull_shipment_name',
        ),
        launch_tools.get_launch_insert_query(
            'tags',
            'shipment_name',
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='executing_source',
                errors=[],
                snapshot_status='preparing',
                record_counts=None,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'expected_launch, expected_stq_arguments',
    [
        pytest.param(
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='executing_source',
                errors=[],
                snapshot_status='preparing',
                record_counts=None,
            ),
            _STQ_RESCHEDULE_10_SEC,
            marks=[
                pytest.mark.pgsql(
                    'segments_provider',
                    queries=[
                        yql_tools.get_insert_yql_task_query(
                            yql_tools.YqlTask(
                                launch_uuid=_CURRENT_LAUNCH_UUID,
                                status='new',
                                started_at=_NOW,
                                error_messages=[],
                                operation_id=None,
                                operation_started_at=None,
                                operation_finished_at=None,
                                is_failed=False,
                            ),
                        ),
                    ],
                ),
            ],
            id='yql_task_new',
        ),
        pytest.param(
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='executing_source',
                errors=[],
                snapshot_status='preparing',
                record_counts=None,
            ),
            _STQ_RESCHEDULE_10_SEC,
            marks=[
                pytest.mark.pgsql(
                    'segments_provider',
                    queries=[
                        yql_tools.get_insert_yql_task_query(
                            yql_tools.YqlTask(
                                launch_uuid=_CURRENT_LAUNCH_UUID,
                                status='running',
                                started_at=_NOW,
                                error_messages=[],
                                operation_id='operation_id',
                                operation_started_at=_NOW,
                                operation_finished_at=None,
                                is_failed=False,
                            ),
                        ),
                        yt_tools.get_insert_yt_table_query(_SNAPSHOT_TABLE),
                        yt_tools.get_insert_yt_table_query(_APPEND_TABLE),
                    ],
                ),
            ],
            id='yql_task_running',
        ),
        pytest.param(
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='executing_consumer',
                errors=[],
                snapshot_status='prepared',
                record_counts=None,
            ),
            _STQ_RESCHEDULE_NOW,
            marks=[
                pytest.mark.pgsql(
                    'segments_provider',
                    queries=[
                        yql_tools.get_insert_yql_task_query(
                            yql_tools.YqlTask(
                                launch_uuid=_CURRENT_LAUNCH_UUID,
                                status='finished',
                                started_at=_NOW,
                                error_messages=[],
                                operation_id='operation_id',
                                operation_started_at=_NOW,
                                operation_finished_at=_NOW,
                                is_failed=False,
                            ),
                        ),
                        yt_tools.get_insert_yt_table_query(_SNAPSHOT_TABLE),
                        yt_tools.get_insert_yt_table_query(_APPEND_TABLE),
                    ],
                ),
            ],
            id='yql_task_completed',
        ),
        pytest.param(
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=True,
                status='cleanup',
                errors=['operation failed: ERROR'],
                snapshot_status='outdated',
                record_counts=None,
            ),
            _STQ_RESCHEDULE_NOW,
            marks=[
                pytest.mark.pgsql(
                    'segments_provider',
                    queries=[
                        yql_tools.get_insert_yql_task_query(
                            yql_tools.YqlTask(
                                launch_uuid=_CURRENT_LAUNCH_UUID,
                                status='finished',
                                started_at=_NOW,
                                error_messages=['operation failed: ERROR'],
                                operation_id='operation_id',
                                operation_started_at=_NOW,
                                operation_finished_at=_NOW,
                                is_failed=True,
                            ),
                        ),
                        yt_tools.get_insert_yt_table_query(_SNAPSHOT_TABLE),
                        yt_tools.get_insert_yt_table_query(_APPEND_TABLE),
                    ],
                ),
            ],
            id='yql_task_failed',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_status_executing_source(
        taxi_segments_provider,
        pgsql,
        stq,
        stq_runner,
        mockserver,
        expected_launch: launch_tools.Launch,
        expected_stq_arguments: Dict[str, Any],
):
    await stq_runner.segments_shipment.call(
        task_id=_TASK_ID,
        args=[],
        kwargs={'consumer_name': 'tags', 'shipment_name': 'shipment_name'},
        expect_fail=False,
    )

    assert stq.segments_shipment.has_calls
    stq_args = stq.segments_shipment.next_call()
    assert stq_args == expected_stq_arguments

    launches = launch_tools.fetch_launches(pgsql, 'tags', 'shipment_name')
    assert launches == [expected_launch]


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags',
            _SHIPMENT,
            tag_provider_name_override='seagull_shipment_name',
        ),
        launch_tools.get_launch_insert_query(
            'tags',
            'shipment_name',
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='executing_consumer',
                errors=[],
                snapshot_status='prepared',
                record_counts=None,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'existing_upload_task, expected_launch, expected_stq_arguments',
    [
        pytest.param(
            None,
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='executing_consumer',
                errors=[],
                snapshot_status='prepared',
                record_counts=None,
            ),
            _STQ_RESCHEDULE_10_SEC,
            id='no_tags_upload_task',
        ),
        pytest.param(
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_UUID,
                status='new',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=None,
            ),
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='executing_consumer',
                errors=[],
                snapshot_status='prepared',
                record_counts=None,
            ),
            _STQ_RESCHEDULE_10_SEC,
            id='tags_upload_task_new',
        ),
        pytest.param(
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_UUID,
                status='checking',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=5,
                    total_remove_table_rows=3,
                    total_snapshot_table_rows=10,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='executing_consumer',
                errors=[],
                snapshot_status='prepared',
                record_counts=None,
            ),
            _STQ_RESCHEDULE_10_SEC,
            id='tags_upload_task_checking',
        ),
        pytest.param(
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_UUID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=5,
                    total_remove_table_rows=3,
                    total_snapshot_table_rows=10,
                    processed_append_table_rows=3,
                    processed_remove_table_rows=0,
                    appended_tags=2,
                    removed_tags=0,
                    malformed_rows=1,
                ),
            ),
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='executing_consumer',
                errors=[],
                snapshot_status='prepared',
                record_counts=None,
            ),
            _STQ_RESCHEDULE_10_SEC,
            id='tags_upload_task_uploading',
        ),
        pytest.param(
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_UUID,
                status='finished',
                is_failed=True,
                error_messages=['error_message'],
                started_at=_NOW,
                upload_state=None,
            ),
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=True,
                status='cleanup',
                errors=['error_message'],
                snapshot_status='outdated',
                record_counts=None,
            ),
            _STQ_RESCHEDULE_NOW,
            id='tags_upload_task_failed_no_statistics',
        ),
        pytest.param(
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_UUID,
                status='finished',
                is_failed=True,
                error_messages=['error_message'],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=5,
                    total_remove_table_rows=3,
                    total_snapshot_table_rows=10,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=True,
                status='cleanup',
                errors=['error_message'],
                snapshot_status='outdated',
                record_counts=launch_tools.RecordCounts(
                    snapshot=10, appended=0, removed=0, malformed=0,
                ),
            ),
            _STQ_RESCHEDULE_NOW,
            id='tags_upload_task_failed_with_statistics',
        ),
        pytest.param(
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_UUID,
                status='finished',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=5,
                    total_remove_table_rows=3,
                    total_snapshot_table_rows=10,
                    processed_append_table_rows=5,
                    processed_remove_table_rows=3,
                    appended_tags=2,
                    removed_tags=3,
                    malformed_rows=1,
                ),
            ),
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='cleanup',
                errors=[],
                snapshot_status='fully_applied',
                record_counts=launch_tools.RecordCounts(
                    snapshot=10, appended=2, removed=3, malformed=1,
                ),
            ),
            _STQ_RESCHEDULE_NOW,
            id='tags_upload_task_completed',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_status_executing_consumer(
        taxi_segments_provider,
        pgsql,
        stq,
        stq_runner,
        mockserver,
        existing_upload_task: Optional[tags_tools.UploadTask],
        expected_launch: launch_tools.Launch,
        expected_stq_arguments: Dict[str, Any],
):
    if existing_upload_task:
        tags_tools.insert_upload_task(pgsql, existing_upload_task)

    await stq_runner.segments_shipment.call(
        task_id=_TASK_ID,
        args=[],
        kwargs={'consumer_name': 'tags', 'shipment_name': 'shipment_name'},
        expect_fail=False,
    )

    assert stq.segments_shipment.has_calls
    stq_args = stq.segments_shipment.next_call()
    assert stq_args == expected_stq_arguments

    launches = launch_tools.fetch_launches(pgsql, 'tags', 'shipment_name')
    assert launches == [expected_launch]


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags',
            _SHIPMENT,
            tag_provider_name_override='seagull_shipment_name',
        ),
        launch_tools.get_launch_insert_query(
            'tags',
            'shipment_name',
            launch_tools.Launch(
                uuid=_PREV_LAUNCH_UUID,
                started_at=_NOW_MINUS_1_HOUR,
                is_failed=False,
                status='finished',
                errors=[],
                snapshot_status='fully_applied',
                record_counts=None,
            ),
        ),
        launch_tools.get_launch_insert_query(
            'tags',
            'shipment_name',
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='executing_consumer',
                errors=[],
                snapshot_status='prepared',
                record_counts=None,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'existing_upload_task, expected_launches',
    [
        pytest.param(
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_UUID,
                status='finished',
                is_failed=True,
                error_messages=['error_message'],
                started_at=_NOW,
                upload_state=None,
            ),
            [
                launch_tools.Launch(
                    uuid=_PREV_LAUNCH_UUID,
                    started_at=_NOW_MINUS_1_HOUR,
                    is_failed=False,
                    status='finished',
                    errors=[],
                    snapshot_status='fully_applied',
                    record_counts=None,
                ),
                launch_tools.Launch(
                    uuid=_CURRENT_LAUNCH_UUID,
                    started_at=_NOW,
                    is_failed=True,
                    status='cleanup',
                    errors=['error_message'],
                    snapshot_status='outdated',
                    record_counts=None,
                ),
            ],
            id='tags_upload_task_failed',
        ),
        pytest.param(
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_UUID,
                status='finished',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=5,
                    total_remove_table_rows=3,
                    total_snapshot_table_rows=10,
                    processed_append_table_rows=5,
                    processed_remove_table_rows=3,
                    appended_tags=2,
                    removed_tags=3,
                    malformed_rows=1,
                ),
            ),
            [
                launch_tools.Launch(
                    uuid=_PREV_LAUNCH_UUID,
                    started_at=_NOW_MINUS_1_HOUR,
                    is_failed=False,
                    status='finished',
                    errors=[],
                    snapshot_status='outdated',
                    record_counts=None,
                ),
                launch_tools.Launch(
                    uuid=_CURRENT_LAUNCH_UUID,
                    started_at=_NOW,
                    is_failed=False,
                    status='cleanup',
                    errors=[],
                    snapshot_status='fully_applied',
                    record_counts=launch_tools.RecordCounts(
                        snapshot=10, appended=2, removed=3, malformed=1,
                    ),
                ),
            ],
            id='tags_upload_task_completed',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_executing_consumer_update_snapshot_status(
        taxi_segments_provider,
        pgsql,
        stq,
        stq_runner,
        mockserver,
        existing_upload_task: Optional[tags_tools.UploadTask],
        expected_launches: List[launch_tools.Launch],
):
    if existing_upload_task:
        tags_tools.insert_upload_task(pgsql, existing_upload_task)

    await stq_runner.segments_shipment.call(
        task_id=_TASK_ID,
        args=[],
        kwargs={'consumer_name': 'tags', 'shipment_name': 'shipment_name'},
        expect_fail=False,
    )

    launches = launch_tools.fetch_launches(pgsql, 'tags', 'shipment_name')
    assert launches == expected_launches


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags',
            _SHIPMENT,
            tag_provider_name_override='seagull_shipment_name',
        ),
    ],
)
@pytest.mark.parametrize(
    'launch, yt_tables, expected_launch, expected_yt_tables',
    [
        pytest.param(
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='cleanup',
                errors=[],
                snapshot_status='fully_applied',
                record_counts=None,
            ),
            [_marked_for_deletion(_APPEND_TABLE), _SNAPSHOT_TABLE],
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='finished',
                errors=[],
                snapshot_status='fully_applied',
                record_counts=None,
            ),
            [_marked_for_deletion(_APPEND_TABLE), _SNAPSHOT_TABLE],
            id='no_errors',
        ),
        pytest.param(
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=True,
                status='cleanup',
                errors=['operation failed: ERROR'],
                snapshot_status='outdated',
                record_counts=None,
            ),
            [_APPEND_TABLE, _SNAPSHOT_TABLE],
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=True,
                status='finished',
                errors=['operation failed: ERROR'],
                snapshot_status='outdated',
                record_counts=None,
            ),
            [
                _marked_for_deletion(_APPEND_TABLE),
                _marked_for_deletion(_SNAPSHOT_TABLE),
            ],
            id='error',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_status_cleanup(
        taxi_segments_provider,
        pgsql,
        stq,
        stq_runner,
        launch: launch_tools.Launch,
        yt_tables: List[yt_tools.YtTable],
        expected_launch: launch_tools.Launch,
        expected_yt_tables: List[yt_tools.YtTable],
):
    launch_tools.insert_launch(pgsql, 'tags', 'shipment_name', launch)
    for table in yt_tables:
        yt_tools.insert_yt_table(pgsql, table)

    await stq_runner.segments_shipment.call(
        task_id=_TASK_ID,
        args=[],
        kwargs={'consumer_name': 'tags', 'shipment_name': 'shipment_name'},
        expect_fail=False,
    )

    assert stq.segments_shipment.has_calls
    stq_args = stq.segments_shipment.next_call()
    assert stq_args == _STQ_RESCHEDULE_NOW

    launches = launch_tools.fetch_launches(pgsql, 'tags', 'shipment_name')
    assert launches == [expected_launch]

    yt_tables = yt_tools.find_yt_tables(pgsql, _CURRENT_LAUNCH_UUID)
    assert yt_tables == expected_yt_tables


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags',
            _SHIPMENT,
            tag_provider_name_override='seagull_shipment_name',
        ),
        launch_tools.get_launch_insert_query(
            'tags',
            'shipment_name',
            launch_tools.Launch(
                uuid=_CURRENT_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='finished',
                errors=[],
                snapshot_status='fully_applied',
                record_counts=None,
            ),
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_status_finished(taxi_segments_provider, pgsql, stq, stq_runner):
    await stq_runner.segments_shipment.call(
        task_id=_TASK_ID,
        args=[],
        kwargs={'consumer_name': 'tags', 'shipment_name': 'shipment_name'},
        expect_fail=False,
    )

    assert stq.segments_shipment.has_calls
    stq_args = stq.segments_shipment.next_call()
    assert stq_args == _STQ_RESCHEDULE_NOW

    expected_shipment = copy.deepcopy(_SHIPMENT)
    expected_shipment.status = shipment_tools.Status.READY

    shipment = shipment_tools.find_shipment(pgsql, 'tags', 'shipment_name')
    assert shipment == expected_shipment
