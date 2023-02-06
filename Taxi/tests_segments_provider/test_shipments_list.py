import dataclasses
import datetime as dt
from typing import List
from typing import Optional

import pytest
import pytz

from tests_segments_provider import launch_tools
from tests_segments_provider import shipment_tools

_NOW = dt.datetime.now()


@dataclasses.dataclass
class TimeRange:
    begin: str
    end: str


@dataclasses.dataclass
class Filters:
    name_part: Optional[str] = None
    is_enabled: Optional[bool] = None
    labels: Optional[List[str]] = None
    last_launch_statuses: Optional[str] = None
    maintainer: Optional[List[str]] = None
    last_modifier: Optional[List[str]] = None
    created_at: Optional[TimeRange] = None
    updated_at: Optional[TimeRange] = None
    disable_at: Optional[TimeRange] = None
    last_launch_at: Optional[TimeRange] = None
    yql_syntax: Optional[shipment_tools.YqlSyntax] = None
    tag_names: Optional[List[str]] = None
    tag_topics: Optional[List[str]] = None


@dataclasses.dataclass
class Request:
    consumer: str
    filters: Filters = Filters()
    order_by: Optional[str] = None
    order_direction: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None

    async def execute(
            self, taxi_segments_provider, expected_code: Optional[int],
    ):
        filters_dict = dataclasses.asdict(self)
        if self.filters.yql_syntax:
            filters_dict['filters'][
                'yql_syntax'
            ] = self.filters.yql_syntax.value

        response = await taxi_segments_provider.post(
            '/admin/v1/shipments-list', filters_dict,
        )

        if expected_code:
            assert response.status_code == expected_code

        return response.json()


@dataclasses.dataclass
class ShipmentsListItem:
    name: str
    labels: List[str]
    maintainers: List[str]
    is_enabled: bool
    created_at: str
    updated_at: str
    last_modifier: str
    disable_at: Optional[str]
    last_launch_at: Optional[str]
    last_launch_status: Optional[str]
    segments_count: Optional[int]
    schedule_to_display: str

    def as_dict(self):
        result = dataclasses.asdict(self)
        for k in list(result.keys()):
            if result[k] is None:
                del result[k]
        return result


async def test_404(taxi_segments_provider):
    request = Request(consumer='unknown-consumer')
    response = await request.execute(taxi_segments_provider, expected_code=404)
    assert response == {
        'code': 'CONSUMER_NOT_FOUND',
        'message': """Consumer "unknown-consumer" doesn't exist""",
    }


@pytest.mark.pgsql('segments_provider', files=['fill_consumers.sql'])
async def test_empty(taxi_segments_provider):
    request = Request(consumer='tags', filters=Filters())
    response = await request.execute(taxi_segments_provider, expected_code=200)
    assert response == {'shipments': []}


_START_AT = dt.datetime(2022, 3, 11, tzinfo=pytz.UTC)

_DATE_1 = dt.datetime(2022, 3, 11, tzinfo=pytz.UTC)
_DATE_2 = dt.datetime(2022, 3, 12, tzinfo=pytz.UTC)
_DATE_3 = dt.datetime(2022, 3, 13, tzinfo=pytz.UTC)
_DATE_4 = dt.datetime(2022, 3, 14, tzinfo=pytz.UTC)

_DATE_1_STR = _DATE_1.isoformat()
_DATE_2_STR = _DATE_2.isoformat()
_DATE_3_STR = _DATE_3.isoformat()
_DATE_4_STR = _DATE_4.isoformat()

_SHIPMENT_1 = ShipmentsListItem(
    name='shipment_name_1',
    labels=['yql'],
    maintainers=['analyst', 'developer'],
    is_enabled=True,
    created_at=_DATE_1.isoformat(),
    updated_at=_DATE_2.isoformat(),
    last_modifier='analyst',
    disable_at=_DATE_3.isoformat(),
    last_launch_at=_DATE_3_STR,
    last_launch_status='error',
    segments_count=None,
    schedule_to_display='Every 30 minutes',
)

_SHIPMENT_2 = ShipmentsListItem(
    name='shipment_name_2',
    labels=[],
    maintainers=['analyst', 'loginef'],
    is_enabled=False,
    created_at=_DATE_2.isoformat(),
    updated_at=_DATE_3.isoformat(),
    last_modifier='developer',
    disable_at=_DATE_4.isoformat(),
    last_launch_at=_DATE_2_STR,
    last_launch_status='success',
    segments_count=None,
    schedule_to_display='Every 1 hours',
)

_SHIPMENT_3 = ShipmentsListItem(
    name='shipment_name_3',
    labels=[],
    maintainers=['developer', 'loginef'],
    is_enabled=True,
    created_at=_DATE_2.isoformat(),
    updated_at=_DATE_2.isoformat(),
    last_modifier='loginef',
    disable_at=_DATE_4.isoformat(),
    last_launch_at=_DATE_1_STR,
    last_launch_status='execution',
    segments_count=None,
    schedule_to_display='Every 90 minutes',
)

_SHIPMENT_4 = ShipmentsListItem(
    name='shipment_name_4',
    labels=[],
    maintainers=[],
    is_enabled=True,
    created_at=_DATE_3.isoformat(),
    updated_at=_DATE_4.isoformat(),
    last_modifier='unknown',
    disable_at=None,
    last_launch_at=None,
    last_launch_status=None,
    segments_count=None,
    schedule_to_display='Every 30 seconds',
)

_LAUNCH_1_RUNNING = launch_tools.Launch(
    uuid='ebf4cb0412014281b5ee54ef389f7be6',
    started_at=_DATE_1,
    is_failed=False,
    status='executing_source',
    errors=[],
    snapshot_status='preparing',
    record_counts=None,
)
_LAUNCH_2_COMPLETED = launch_tools.Launch(
    uuid='5dd4b90b00b6459186b96f162bfa5cba',
    started_at=_DATE_2,
    is_failed=False,
    status='finished',
    errors=['operation failed', 'ERROR'],
    snapshot_status='outdated',
    record_counts=None,
)
_LAUNCH_3_FAILED = launch_tools.Launch(
    uuid='dea02467fdb044b7b50c57f0c723aacd',
    started_at=_DATE_3,
    is_failed=True,
    status='finished',
    errors=['operation failed', 'ERROR'],
    snapshot_status='outdated',
    record_counts=None,
)


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags',
            shipment_tools.DbShipment(
                name='shipment_name_1',
                ticket='A-1',
                maintainers=['developer', 'analyst'],
                is_enabled=True,
                labels=['yql'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
                    unit=shipment_tools.UnitOfTime.MINUTES,
                    count=30,
                ),
                source=shipment_tools.YqlQuery(
                    syntax=shipment_tools.YqlSyntax.SQLv1, query='SELECT 1',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    allowed_tag_names=['tag1'],
                ),
                created_at=_DATE_1,
                updated_at=_DATE_2,
                status=shipment_tools.Status.READY,
                last_modifier='analyst',
                disable_at=_DATE_3,
                launch_period=dt.timedelta(minutes=30),
            ),
        ),
        shipment_tools.get_shipment_insert_query(
            'tags',
            shipment_tools.DbShipment(
                name='shipment_name_2',
                ticket='A-1',
                maintainers=['analyst', 'loginef'],
                is_enabled=False,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
                    unit=shipment_tools.UnitOfTime.HOURS,
                    count=1,
                ),
                source=shipment_tools.YqlQuery(
                    syntax=shipment_tools.YqlSyntax.CLICKHOUSE,
                    query='SELECT 1',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    allowed_tag_names=['tag2'],
                ),
                created_at=_DATE_2,
                updated_at=_DATE_3,
                status=shipment_tools.Status.READY,
                last_modifier='developer',
                disable_at=_DATE_4,
                launch_period=dt.timedelta(hours=1),
            ),
        ),
        shipment_tools.get_shipment_insert_query(
            'tags',
            shipment_tools.DbShipment(
                name='shipment_name_3',
                ticket='A-1',
                maintainers=['loginef', 'developer'],
                is_enabled=True,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
                    unit=shipment_tools.UnitOfTime.MINUTES,
                    count=90,
                ),
                source=shipment_tools.YqlQuery(
                    syntax=shipment_tools.YqlSyntax.SQLv1, query='SELECT 1',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    allowed_tag_names=['tag3'],
                ),
                created_at=_DATE_2,
                updated_at=_DATE_2,
                status=shipment_tools.Status.READY,
                last_modifier='loginef',
                disable_at=_DATE_4,
                launch_period=dt.timedelta(minutes=90),
            ),
        ),
        shipment_tools.get_shipment_insert_query(
            'tags',
            shipment_tools.DbShipment(
                name='shipment_name_4',
                ticket='A-1',
                maintainers=[],
                is_enabled=True,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=30,
                ),
                source=shipment_tools.YqlQuery(
                    syntax=shipment_tools.YqlSyntax.SQLv1, query='SELECT 1',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    allowed_tag_names=[],
                ),
                created_at=_DATE_3,
                updated_at=_DATE_4,
                status=shipment_tools.Status.READY,
                last_modifier=None,
                disable_at=None,
                launch_period=dt.timedelta(seconds=30),
            ),
        ),
        shipment_tools.get_consumer_insert_query('discounts'),
        launch_tools.get_launch_insert_query(
            consumer_name='tags',
            shipment_name=_SHIPMENT_1.name,
            launch=_LAUNCH_1_RUNNING,
        ),
        launch_tools.get_launch_insert_query(
            consumer_name='tags',
            shipment_name=_SHIPMENT_1.name,
            launch=_LAUNCH_2_COMPLETED,
        ),
        launch_tools.get_launch_insert_query(
            consumer_name='tags',
            shipment_name=_SHIPMENT_1.name,
            launch=_LAUNCH_3_FAILED,
        ),
        launch_tools.get_launch_insert_query(
            consumer_name='tags',
            shipment_name=_SHIPMENT_2.name,
            launch=_LAUNCH_1_RUNNING,
        ),
        launch_tools.get_launch_insert_query(
            consumer_name='tags',
            shipment_name=_SHIPMENT_2.name,
            launch=_LAUNCH_2_COMPLETED,
        ),
        launch_tools.get_launch_insert_query(
            consumer_name='tags',
            shipment_name=_SHIPMENT_3.name,
            launch=_LAUNCH_1_RUNNING,
        ),
    ],
)
@pytest.mark.parametrize(
    'req, shipments',
    [
        pytest.param(
            Request(consumer='discounts', filters=Filters()), [], id='empty',
        ),
        pytest.param(
            Request(consumer='tags', filters=Filters()),
            [_SHIPMENT_1, _SHIPMENT_2, _SHIPMENT_3, _SHIPMENT_4],
            id='no_filters',
        ),
        pytest.param(
            Request(consumer='tags', filters=Filters(maintainer=['loginef'])),
            [_SHIPMENT_2, _SHIPMENT_3],
            id='filter_by_maintainer',
        ),
        pytest.param(
            Request(
                consumer='tags',
                filters=Filters(maintainer=['loginef', 'analyst']),
            ),
            [_SHIPMENT_1, _SHIPMENT_2, _SHIPMENT_3],
            id='filter_by_two_maintainers',
        ),
        pytest.param(
            Request(consumer='tags', filters=Filters(is_enabled=True)),
            [_SHIPMENT_1, _SHIPMENT_3, _SHIPMENT_4],
            id='filter_enabled',
        ),
        pytest.param(
            Request(consumer='tags', filters=Filters(is_enabled=False)),
            [_SHIPMENT_2],
            id='filter_disabled',
        ),
        pytest.param(
            Request(consumer='tags', filters=Filters(labels=['yql'])),
            [_SHIPMENT_1],
            id='filter_by_label',
        ),
        pytest.param(
            Request(
                consumer='tags',
                filters=Filters(last_modifier=['analyst', 'developer']),
            ),
            [_SHIPMENT_1, _SHIPMENT_2],
            id='filter_last_modifier',
        ),
        pytest.param(
            Request(
                consumer='tags',
                filters=Filters(
                    created_at=TimeRange(_DATE_2_STR, _DATE_4_STR),
                ),
            ),
            [_SHIPMENT_2, _SHIPMENT_3, _SHIPMENT_4],
            id='filter_created_at',
        ),
        pytest.param(
            Request(
                consumer='tags',
                filters=Filters(
                    updated_at=TimeRange(_DATE_2_STR, _DATE_4_STR),
                ),
            ),
            [_SHIPMENT_1, _SHIPMENT_2, _SHIPMENT_3],
            id='filter_updated_at',
        ),
        pytest.param(
            Request(
                consumer='tags',
                filters=Filters(
                    disable_at=TimeRange(_DATE_2_STR, _DATE_4_STR),
                ),
            ),
            [_SHIPMENT_1],
            id='filter_disable_at',
        ),
        pytest.param(
            Request(
                consumer='tags',
                filters=Filters(
                    yql_syntax=shipment_tools.YqlSyntax.CLICKHOUSE,
                ),
            ),
            [_SHIPMENT_2],
            id='filter_yql_syntax',
        ),
        pytest.param(
            Request(
                consumer='tags', filters=Filters(tag_names=['tag1', 'tag3']),
            ),
            [_SHIPMENT_1, _SHIPMENT_3],
            id='filter_tag_names',
        ),
        pytest.param(
            Request(
                consumer='tags', filters=Filters(name_part='non-existing'),
            ),
            [],
            id='empty-by-name-part',
        ),
        pytest.param(
            Request(consumer='tags', filters=Filters(name_part='MENT')),
            [_SHIPMENT_1, _SHIPMENT_2, _SHIPMENT_3, _SHIPMENT_4],
            id='by_name_part_case_insensitive',
        ),
        pytest.param(
            Request(consumer='tags', filters=Filters(name_part='ame_4')),
            [_SHIPMENT_4],
            id='by-name-part',
        ),
        pytest.param(
            Request(consumer='tags', filters=Filters(), offset=2),
            [_SHIPMENT_3, _SHIPMENT_4],
            id='offset',
        ),
        pytest.param(
            Request(consumer='tags', filters=Filters(), limit=2),
            [_SHIPMENT_1, _SHIPMENT_2],
            id='limit',
        ),
        pytest.param(
            Request(
                consumer='tags',
                filters=Filters(),
                order_by='name',
                order_direction='DESC',
            ),
            [_SHIPMENT_4, _SHIPMENT_3, _SHIPMENT_2, _SHIPMENT_1],
            id='sort_name_desc',
        ),
        pytest.param(
            Request(consumer='tags', filters=Filters(), order_by='is_enabled'),
            [_SHIPMENT_2, _SHIPMENT_1, _SHIPMENT_3, _SHIPMENT_4],
            id='sort_is_enabled',
        ),
        pytest.param(
            Request(consumer='tags', filters=Filters(), order_by='created_at'),
            [_SHIPMENT_1, _SHIPMENT_2, _SHIPMENT_3, _SHIPMENT_4],
            id='sort_created_at',
        ),
        pytest.param(
            Request(consumer='tags', filters=Filters(), order_by='updated_at'),
            [_SHIPMENT_1, _SHIPMENT_3, _SHIPMENT_2, _SHIPMENT_4],
            id='sort_updated_at',
        ),
        pytest.param(
            Request(
                consumer='tags',
                filters=Filters(),
                order_by='launch_frequency',
            ),
            [_SHIPMENT_4, _SHIPMENT_1, _SHIPMENT_2, _SHIPMENT_3],
            id='sort_launch_frequency',
        ),
    ],
)
async def test_list(
        taxi_segments_provider,
        req: Request,
        shipments: List[ShipmentsListItem],
):
    response = await req.execute(taxi_segments_provider, expected_code=200)
    expected_shipments = [s.as_dict() for s in shipments]
    assert response == {'shipments': expected_shipments}
