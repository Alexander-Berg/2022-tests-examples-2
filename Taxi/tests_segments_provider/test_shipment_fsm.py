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
from tests_segments_provider import yt_tools


_TZ_MOSCOW = pytz.timezone('Europe/Moscow')

_CREATED_AT = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 15, 0, 0))
_NOW_MINUS_1_HOUR = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 14, 0, 5))
_NOW_MINUS_1_MINUTE = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 14, 59, 5))
_NOW = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 15, 0, 5))
_NOW_PLUS_4_MIN = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 15, 4, 5))
_NOW_PLUS_5_MIN = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 15, 5, 5))
_NOW_PLUS_10_MIN = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 15, 10, 5))
_UPDATED_AT = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 16, 0, 0))

# sha256(tags.shipment_name)
_TASK_ID = '85335d4133d28c3b1b163aac8387bae71c4ff0d7c957216332b050cec58c8bf0'

_LAUNCH_UUID = '5c3224b7aa1a4820b69c67c2f222d555'


def insert_shipment(
        pgsql,
        is_enabled: bool,
        status: shipment_tools.Status,
        start_at: dt.datetime = _NOW_PLUS_10_MIN,
):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        shipment_tools.get_shipment_insert_query(
            'tags',
            shipment_tools.DbShipment(
                name='shipment_name',
                ticket='A-2',
                maintainers=['developer'],
                is_enabled=is_enabled,
                labels=['CLICKHOUSE', 'passenger-tags'],
                schedule=shipment_tools.Schedule(
                    start_at=start_at,
                    unit=shipment_tools.UnitOfTime.MINUTES,
                    count=5,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.CLICKHOUSE, 'SELECT 2',
                ),
                consumer=shipment_tools.TagsConsumerSettings(['tag3']),
                created_at=_CREATED_AT,
                updated_at=_UPDATED_AT,
                status=status,
            ),
            tag_provider_name_override='seagull_shipment_name',
        ),
    )


@pytest.mark.pgsql('segments_provider', queries=[])
@pytest.mark.parametrize(
    'is_enabled_value, fail_provider_creation, expect_task_failure, '
    'expected_status, expected_stq_arguments',
    [
        pytest.param(
            True,
            False,
            False,
            shipment_tools.Status.READY,
            {
                'args': None,
                'eta': _NOW.astimezone(pytz.UTC).replace(tzinfo=None),
                'kwargs': None,
                'queue': 'segments_shipment',
                'id': _TASK_ID,
            },
            id='enabled',
        ),
        pytest.param(
            False,
            False,
            False,
            shipment_tools.Status.DISABLING,
            {
                'args': None,
                'eta': _NOW.astimezone(pytz.UTC).replace(tzinfo=None),
                'kwargs': None,
                'queue': 'segments_shipment',
                'id': _TASK_ID,
            },
            id='disabled',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_status_new(
        taxi_segments_provider,
        pgsql,
        stq,
        stq_runner,
        mockserver,
        is_enabled_value: bool,
        fail_provider_creation: bool,
        expect_task_failure: bool,
        expected_status: str,
        expected_stq_arguments: Optional[Dict[str, Any]],
):
    insert_shipment(pgsql, is_enabled_value, shipment_tools.Status.NEW)

    @mockserver.json_handler(
        'tags/v1/segments/providers/seagull_shipment_name',
    )
    def _providers_search_handler(request):
        return mockserver.make_response(
            status=404, json={'code': 'NOT_FOUND', 'message': 'not exists'},
        )

    @mockserver.json_handler(
        'tags/v1/segments/providers/seagull_shipment_name/create',
    )
    def providers_items_handler(request):
        if fail_provider_creation:
            raise mockserver.TimeoutError()
        return {}

    await stq_runner.segments_shipment.call(
        task_id=_TASK_ID,
        args=[],
        kwargs={'consumer_name': 'tags', 'shipment_name': 'shipment_name'},
        expect_fail=expect_task_failure,
    )

    updated_shipment = shipment_tools.find_shipment(
        pgsql, 'tags', 'shipment_name',
    )
    assert updated_shipment.status == expected_status

    if expected_stq_arguments:
        assert stq.segments_shipment.has_calls
        stq_args = stq.segments_shipment.next_call()
        assert stq_args == expected_stq_arguments
    else:
        assert not stq.segments_shipment.has_calls

    assert providers_items_handler.has_calls
    creation_request = providers_items_handler.next_call()['request']
    assert creation_request.json == {
        'acl': {'tvm_owners': ['segments-provider'], 'authority': 'base'},
        'description': (
            'Tags provider for segments-provider\'s shipment shipment_name'
        ),
        'is_active': True,
    }


_FINISHED_LAUNCH_HOUR_AGO = launch_tools.Launch(
    uuid='258fd368e9754c7cadd9242f533a0a20',
    started_at=_NOW_MINUS_1_HOUR,
    is_failed=False,
    status='finished',
    errors=[],
    snapshot_status='fully_applied',
    record_counts=None,
)

_FINISHED_LAUNCH_MINUTE_AGO = launch_tools.Launch(
    uuid='258fd368e9754c7cadd9242f533a0a20',
    started_at=_NOW_MINUS_1_MINUTE,
    is_failed=False,
    status='finished',
    errors=[],
    snapshot_status='fully_applied',
    record_counts=None,
)

_RUNNING_LAUNCH_NOW = launch_tools.Launch(
    uuid='258fd368e9754c7cadd9242f533a0a20',
    started_at=_NOW,
    is_failed=False,
    status='executing_source',
    errors=[],
    snapshot_status='preparing',
    record_counts=None,
)


@pytest.mark.pgsql('segments_provider', queries=[])
@pytest.mark.parametrize(
    'is_enabled_value, start_at, existing_launches, expected_status,'
    'expected_stq_arguments, expected_launches',
    [
        pytest.param(
            True,
            _NOW_PLUS_10_MIN,
            [],
            shipment_tools.Status.READY,
            {
                'args': None,
                'eta': _NOW_PLUS_5_MIN.astimezone(pytz.UTC).replace(
                    tzinfo=None,
                ),
                'kwargs': None,
                'queue': 'segments_shipment',
                'id': _TASK_ID,
            },
            [],
            id='enabled_too_early',
        ),
        pytest.param(
            True,
            _NOW,
            [],
            shipment_tools.Status.RUNNING,
            {
                'args': None,
                'eta': _NOW.astimezone(pytz.UTC).replace(tzinfo=None),
                'kwargs': None,
                'queue': 'segments_shipment',
                'id': _TASK_ID,
            },
            [_RUNNING_LAUNCH_NOW],
            id='enabled_empty_history',
        ),
        pytest.param(
            True,
            _NOW,
            [_FINISHED_LAUNCH_HOUR_AGO],
            shipment_tools.Status.RUNNING,
            {
                'args': None,
                'eta': _NOW.astimezone(pytz.UTC).replace(tzinfo=None),
                'kwargs': None,
                'queue': 'segments_shipment',
                'id': _TASK_ID,
            },
            [_FINISHED_LAUNCH_HOUR_AGO, _RUNNING_LAUNCH_NOW],
            id='enabled_period_passed',
        ),
        pytest.param(
            True,
            _NOW,
            [_FINISHED_LAUNCH_MINUTE_AGO],
            shipment_tools.Status.READY,
            {
                'args': None,
                'eta': _NOW_PLUS_4_MIN.astimezone(pytz.UTC).replace(
                    tzinfo=None,
                ),
                'kwargs': None,
                'queue': 'segments_shipment',
                'id': _TASK_ID,
            },
            [_FINISHED_LAUNCH_MINUTE_AGO],
            id='enabled_waiting_period',
        ),
        pytest.param(
            False,
            _NOW,
            [],
            shipment_tools.Status.DISABLING,
            {
                'args': None,
                'eta': _NOW.astimezone(pytz.UTC).replace(tzinfo=None),
                'kwargs': None,
                'queue': 'segments_shipment',
                'id': _TASK_ID,
            },
            [],
            id='disabled',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_status_ready(
        taxi_segments_provider,
        pgsql,
        stq,
        stq_runner,
        is_enabled_value: bool,
        start_at: dt.datetime,
        expected_status: shipment_tools.Status,
        expected_stq_arguments: Optional[Dict[str, Any]],
        existing_launches: List[launch_tools.Launch],
        expected_launches: List[launch_tools.Launch],
):
    insert_shipment(
        pgsql,
        is_enabled_value,
        shipment_tools.Status.READY,
        start_at=start_at,
    )

    for launch in existing_launches:
        launch_tools.insert_launch(
            pgsql,
            consumer_name='tags',
            shipment_name='shipment_name',
            launch=launch,
        )

    await stq_runner.segments_shipment.call(
        task_id=_TASK_ID,
        args=[],
        kwargs={'consumer_name': 'tags', 'shipment_name': 'shipment_name'},
    )

    updated_shipment = shipment_tools.find_shipment(
        pgsql, 'tags', 'shipment_name',
    )
    assert updated_shipment.status == expected_status

    # Launch creation must clear relaunch flag
    if expected_status == shipment_tools.Status.RUNNING:
        assert not updated_shipment.is_relaunch_requested

    if expected_stq_arguments:
        assert stq.segments_shipment.has_calls
        stq_args = stq.segments_shipment.next_call()
        assert stq_args == expected_stq_arguments
    else:
        assert not stq.segments_shipment.has_calls

    assert list(
        [
            launch.normalized_for_comparizon()
            for launch in launch_tools.fetch_launches(
                pgsql, 'tags', 'shipment_name',
            )
        ],
    ) == [launch.normalized_for_comparizon() for launch in expected_launches]


_SNAPSHOT_PATH = '//snapshot'

_SNAPSHOT_SCHEMA = {
    'path': _SNAPSHOT_PATH,
    'attributes': {
        'schema': [
            {'name': 'entity_value', 'type': 'string'},
            {'name': 'entity_type', 'type': 'string'},
            {'name': 'tag', 'type': 'string'},
            {'name': 'ttl', 'type': 'string'},
        ],
    },
}


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.yt(
    schemas=[_SNAPSHOT_SCHEMA],
    static_table_data=[
        {
            'path': _SNAPSHOT_PATH,
            'values': [
                {
                    'tag': 'tag1',
                    'entity_type': 'udid',
                    'entity_value': '097ccaddcb06413e8537ee6f228a7b7b',
                    'ttl': 'infinity',
                },
                {
                    'tag': 'tag2',
                    'entity_type': 'udid',
                    'entity_value': '097ccaddcb06413e8537ee6f228a7b7b',
                    'ttl': 'infinity',
                },
                {
                    'tag': 'tag1',
                    'entity_type': 'udid',
                    'entity_value': 'fd5b4e8d6aec42c18aa2942643163348',
                    'ttl': '2022-05-25T12:00:00+0300',
                },
                {
                    'tag': 'tag1',
                    'entity_type': 'udid',
                    'entity_value': None,
                    'ttl': 'infinity',
                },
            ],
        },
    ],
)
@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags',
            shipment_tools.DbShipment(
                name='shipment_name',
                ticket='A-2',
                maintainers=['developer'],
                is_enabled=False,
                labels=['CLICKHOUSE', 'passenger-tags'],
                schedule=shipment_tools.Schedule(
                    start_at=_NOW,
                    unit=shipment_tools.UnitOfTime.MINUTES,
                    count=5,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.CLICKHOUSE, 'SELECT 2',
                ),
                consumer=shipment_tools.TagsConsumerSettings(['tag3']),
                created_at=_CREATED_AT,
                updated_at=_UPDATED_AT,
                status=shipment_tools.Status.DISABLING,
            ),
            tag_provider_name_override='seagull_shipment_name',
        ),
    ],
)
@pytest.mark.parametrize(
    'existing_launch, existing_discard_task, existing_yt_tables, '
    'expected_launch, expected_discard_task, expected_yt_tables, '
    'expected_shipment_status',
    [
        pytest.param(
            None,  # existing_launch
            None,  # existing_discard_task
            [],  # existing_yt_tables
            None,  # expected_launch
            None,  # expected_discard_task
            [],  # expected_yt_tables
            shipment_tools.Status.DISABLED,
            id='no_launches',
        ),
        pytest.param(
            launch_tools.Launch(
                uuid=_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='executing_source',
                errors=[],
                snapshot_status='preparing',
                record_counts=None,
            ),  # existing_launch
            None,  # existing_discard_task
            [],  # existing_yt_tables
            launch_tools.Launch(
                uuid=_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='executing_source',
                errors=[],
                snapshot_status='preparing',
                record_counts=None,
            ),  # expected_launch
            None,  # expected_discard_task
            [],  # expected_yt_tables
            shipment_tools.Status.DISABLING,
            id='wait_running_launch',
        ),
        pytest.param(
            launch_tools.Launch(
                uuid=_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='finished',
                errors=[],
                snapshot_status='outdated',
                record_counts=None,
            ),  # existing_launch
            None,  # existing_discard_task
            [],  # existing_yt_tables
            launch_tools.Launch(
                uuid=_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='finished',
                errors=[],
                snapshot_status='outdated',
                record_counts=None,
            ),  # expected_launch
            None,  # expected_discard_task
            [],  # expected_yt_tables
            shipment_tools.Status.DISABLED,
            id='no_snapshots_to_discard',
        ),
        pytest.param(
            launch_tools.Launch(
                uuid=_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='finished',
                errors=[],
                snapshot_status='fully_applied',
                record_counts=None,
            ),  # existing_launch
            None,  # existing_discard_task
            [
                yt_tools.YtTable(
                    launch_uuid=_LAUNCH_UUID,
                    alias='snapshot',
                    path=_SNAPSHOT_PATH,
                    lifespan='persistent',
                    is_marked_for_deletion=False,
                ),
            ],  # existing_yt_tables
            launch_tools.Launch(
                uuid=_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='finished',
                errors=[],
                snapshot_status='fully_applied',
                record_counts=None,
            ),  # expected_launch
            tags_tools.DiscardTask(
                launch_uuid=_LAUNCH_UUID,
                total_snapshot_records=4,
                processed_snapshot_records=0,
            ),  # expected_discard_task
            [
                yt_tools.YtTable(
                    launch_uuid=_LAUNCH_UUID,
                    alias='snapshot',
                    path=_SNAPSHOT_PATH,
                    lifespan='persistent',
                    is_marked_for_deletion=False,
                ),
            ],  # expected_yt_tables
            shipment_tools.Status.DISABLING,
            id='start_discard_snapshot',
        ),
        pytest.param(
            launch_tools.Launch(
                uuid=_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='finished',
                errors=[],
                snapshot_status='fully_applied',
                record_counts=None,
            ),  # existing_launch
            tags_tools.DiscardTask(
                launch_uuid=_LAUNCH_UUID,
                total_snapshot_records=4,
                processed_snapshot_records=4,
            ),  # existing_discard_task
            [
                yt_tools.YtTable(
                    launch_uuid=_LAUNCH_UUID,
                    alias='snapshot',
                    path=_SNAPSHOT_PATH,
                    lifespan='persistent',
                    is_marked_for_deletion=False,
                ),
            ],  # existing_yt_tables
            launch_tools.Launch(
                uuid=_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='finished',
                errors=[],
                snapshot_status='outdated',
                record_counts=None,
            ),  # expected_launch
            None,  # expected_discard_task
            [
                yt_tools.YtTable(
                    launch_uuid=_LAUNCH_UUID,
                    alias='snapshot',
                    path=_SNAPSHOT_PATH,
                    lifespan='persistent',
                    is_marked_for_deletion=True,
                ),
            ],  # expected_yt_tables
            shipment_tools.Status.DISABLED,
            id='finish_discard_snapshot_and_cleanup',
        ),
    ],
)
async def test_status_disabling(
        taxi_segments_provider,
        pgsql,
        stq,
        stq_runner,
        yt_client,
        yt_apply_force,
        existing_launch: Optional[launch_tools.Launch],
        existing_discard_task: Optional[tags_tools.DiscardTask],
        existing_yt_tables: List[yt_tools.YtTable],
        expected_launch: Optional[launch_tools.Launch],
        expected_discard_task: Optional[tags_tools.DiscardTask],
        expected_yt_tables: List[yt_tools.YtTable],
        expected_shipment_status: shipment_tools.Status,
):
    if existing_launch:
        launch_tools.insert_launch(
            pgsql, 'tags', 'shipment_name', existing_launch,
        )
    if existing_discard_task:
        tags_tools.insert_discard_task(pgsql, existing_discard_task)
    for table in existing_yt_tables:
        yt_tools.insert_yt_table(pgsql, table)

    await stq_runner.segments_shipment.call(
        task_id=_TASK_ID,
        args=[],
        kwargs={'consumer_name': 'tags', 'shipment_name': 'shipment_name'},
    )
    assert stq.segments_shipment.has_calls

    updated_shipment = shipment_tools.find_shipment(
        pgsql, 'tags', 'shipment_name',
    )
    assert updated_shipment.status == expected_shipment_status

    launches = launch_tools.fetch_launches(pgsql, 'tags', 'shipment_name')
    if expected_launch:
        assert launches == [expected_launch]
    else:
        assert not launches

    discard_tasks = tags_tools.find_discard_tasks(pgsql)
    if expected_discard_task:
        assert discard_tasks == [expected_discard_task]
    else:
        assert not discard_tasks

    assert yt_tools.find_all_yt_tables(pgsql) == expected_yt_tables


@pytest.mark.pgsql('segments_provider', queries=[])
@pytest.mark.parametrize(
    'is_enabled_value, expected_status, expected_stq_arguments',
    [
        pytest.param(
            True,
            shipment_tools.Status.READY,
            {
                'args': None,
                'eta': _NOW.astimezone(pytz.UTC).replace(tzinfo=None),
                'kwargs': None,
                'queue': 'segments_shipment',
                'id': _TASK_ID,
            },
            id='enabled',
        ),
        pytest.param(
            False, shipment_tools.Status.DISABLED, None, id='disabled',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_status_disabled(
        taxi_segments_provider,
        pgsql,
        stq,
        stq_runner,
        is_enabled_value: bool,
        expected_status: str,
        expected_stq_arguments: Optional[Dict[str, Any]],
):
    insert_shipment(pgsql, is_enabled_value, shipment_tools.Status.DISABLED)

    await stq_runner.segments_shipment.call(
        task_id=_TASK_ID,
        args=[],
        kwargs={'consumer_name': 'tags', 'shipment_name': 'shipment_name'},
    )

    updated_shipment = shipment_tools.find_shipment(
        pgsql, 'tags', 'shipment_name',
    )
    assert updated_shipment.status == expected_status

    if expected_stq_arguments:
        assert stq.segments_shipment.has_calls
        stq_args = stq.segments_shipment.next_call()
        assert stq_args == expected_stq_arguments
    else:
        assert not stq.segments_shipment.has_calls
