import dataclasses
import datetime as dt
from typing import List
import uuid

import pytest
import pytz

from tests_segments_provider import common_tools
from tests_segments_provider import launch_tools
from tests_segments_provider import shipment_tools

_TZ_MOSCOW = pytz.timezone('Europe/Moscow')

_NOW = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 17))

_CONSUMER_NAME = 'tags'


def make_uuid():
    return str(uuid.uuid4()).replace('-', '')


@dataclasses.dataclass
class LaunchInsertParams:
    started_at: dt.datetime
    status: str
    is_failed: bool


def insert_launches(
        pgsql, shipment_name: str, launches: List[LaunchInsertParams],
):
    if not launches:
        return

    last_launch = launches[-1]
    for launch in launches:
        launch_tools.insert_launch(
            pgsql,
            consumer_name=_CONSUMER_NAME,
            shipment_name=shipment_name,
            launch=launch_tools.Launch(
                uuid=make_uuid(),
                started_at=launch.started_at,
                is_failed=launch.is_failed,
                status=launch.status,
                errors=[],
                snapshot_status='fully_applied'
                if not launch.is_failed and launch == last_launch
                else 'outdated',
                record_counts=None,
            ),
        )


def insert_shipment(pgsql, name: str, is_shipment_enabled: bool):
    shipment_tools.insert_shipment(
        pgsql,
        consumer_name=_CONSUMER_NAME,
        shipment=shipment_tools.DbShipment(
            name=name,
            ticket='A-1',
            maintainers=[],
            is_enabled=is_shipment_enabled,
            labels=[],
            schedule=shipment_tools.Schedule(
                start_at=_NOW, unit=shipment_tools.UnitOfTime.HOURS, count=1,
            ),
            source=shipment_tools.YqlQuery(
                syntax=shipment_tools.YqlSyntax.SQLv1, query='SELECT 1',
            ),
            consumer=shipment_tools.TagsConsumerSettings(
                allowed_tag_names=['tag1'],
            ),
            created_at=_NOW,
            updated_at=_NOW,
            status=shipment_tools.Status.READY,
        ),
    )


@pytest.mark.now(_NOW.isoformat())
async def test_launches_monitor(
        taxi_segments_provider,
        taxi_segments_provider_monitor,
        pgsql,
        testpoint,
):
    insert_shipment(pgsql, name='disabled_shipment', is_shipment_enabled=False)
    insert_launches(
        pgsql,
        shipment_name='disabled_shipment',
        launches=[
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(hours=10),
                status='finished',
                is_failed=False,
            ),
        ],
    )

    insert_shipment(pgsql, name='shipment_1', is_shipment_enabled=True)
    insert_launches(
        pgsql,
        'shipment_1',
        launches=[
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(hours=10),
                status='finished',
                is_failed=False,
            ),
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(hours=9),
                status='finished',
                is_failed=True,
            ),
        ],
    )

    insert_shipment(pgsql, name='shipment_2', is_shipment_enabled=True)
    insert_launches(
        pgsql,
        'shipment_2',
        launches=[
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(hours=10),
                status='executing_source',
                is_failed=False,
            ),
        ],
    )

    insert_shipment(pgsql, name='shipment_3', is_shipment_enabled=True)
    insert_launches(
        pgsql,
        'shipment_3',
        launches=[
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(hours=10),
                status='finished',
                is_failed=False,
            ),
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(minutes=50),
                status='finished',
                is_failed=False,
            ),
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(minutes=40),
                status='finished',
                is_failed=False,
            ),
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(minutes=30),
                status='finished',
                is_failed=True,
            ),
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(minutes=20),
                status='finished',
                is_failed=True,
            ),
            LaunchInsertParams(
                started_at=_NOW, status='executing_consumer', is_failed=True,
            ),
        ],
    )

    insert_shipment(pgsql, name='shipment_4', is_shipment_enabled=True)
    insert_launches(
        pgsql,
        'shipment_4',
        launches=[
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(hours=10),
                status='finished',
                is_failed=False,
            ),
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(hours=9),
                status='finished',
                is_failed=False,
            ),
        ],
    )

    insert_shipment(pgsql, name='shipment_5', is_shipment_enabled=True)
    insert_launches(
        pgsql,
        'shipment_5',
        launches=[
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(hours=10),
                status='finished',
                is_failed=False,
            ),
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(hours=9),
                status='finished',
                is_failed=False,
            ),
        ],
    )

    insert_shipment(pgsql, name='shipment_6', is_shipment_enabled=True)
    insert_launches(
        pgsql,
        'shipment_6',
        launches=[
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(hours=10),
                status='finished',
                is_failed=False,
            ),
            LaunchInsertParams(
                started_at=_NOW - dt.timedelta(hours=9),
                status='finished',
                is_failed=False,
            ),
        ],
    )

    testpoint_handler = common_tools.WorkerTestpointWithMetrics(
        testpoint, taxi_segments_provider_monitor, 'launches-monitor',
    )

    async with taxi_segments_provider.spawn_task('launches-monitor'):
        await testpoint_handler.worker_finished.wait_call()

    assert testpoint_handler.metrics == {
        'launches-by-last-status': {
            '$meta': {'solomon_children_labels': 'status'},
            'failed': {'count': 1},
            'running': {'count': 2},
            'succeeded': {'count': 3},
        },
        'launches-statuses-last-hour': {
            '$meta': {'solomon_children_labels': 'status'},
            'failed': {'count': 2},
            'running': {'count': 1},
            'succeeded': {'count': 2},
        },
    }
