import datetime as dt
from typing import Any
from typing import Dict
from typing import List

import pytest
import pytz

from tests_segments_provider import launch_tools
from tests_segments_provider import shipment_tools

_TZ_MOSCOW = pytz.timezone('Europe/Moscow')

_NOW = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 17))
_LAUNCH_1_START = _TZ_MOSCOW.localize(dt.datetime(2021, 10, 14, 17))
_LAUNCH_2_START = _TZ_MOSCOW.localize(dt.datetime(2021, 11, 14, 17))
_LAUNCH_3_START = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 17))

_LAUNCH_1_UUID = 'c2e1b42f73f44ecdaca108a0f61a1970'
_LAUNCH_2_UUID = '153d344067084a1d9a52f9ff53352ede'
_LAUNCH_3_UUID = 'b2a97e655a554583ba2642f1e1503884'

_DB_LAUNCH_1 = launch_tools.Launch(
    uuid=_LAUNCH_1_UUID,
    started_at=_LAUNCH_1_START,
    is_failed=False,
    status='finished',
    errors=[],
    snapshot_status='fully_applied',
    record_counts=launch_tools.RecordCounts(
        snapshot=10, appended=5, removed=3, malformed=1,
    ),
)

_DB_LAUNCH_2 = launch_tools.Launch(
    uuid=_LAUNCH_2_UUID,
    started_at=_LAUNCH_2_START,
    is_failed=True,
    status='finished',
    errors=['operation failed', 'ERROR'],
    snapshot_status='outdated',
    record_counts=None,
)

_DB_LAUNCH_3 = launch_tools.Launch(
    uuid=_LAUNCH_3_UUID,
    started_at=_LAUNCH_3_START,
    is_failed=False,
    status='executing_source',
    errors=[],
    snapshot_status='preparing',
    record_counts=None,
)

_LIST_LAUNCH_1 = {
    'id': _LAUNCH_1_UUID,
    'started_at': _LAUNCH_1_START,
    'status': 'completed',
    'hints': [],
    'record_counts': {
        'total': 10,
        'appended': 5,
        'removed': 3,
        'malformed': 1,
    },
}

_LIST_LAUNCH_2 = {
    'id': _LAUNCH_2_UUID,
    'started_at': _LAUNCH_2_START,
    'status': 'failed',
    'hints': [
        {'text': 'operation failed', 'severity': 'error'},
        {'text': 'ERROR', 'severity': 'error'},
    ],
}

_LIST_LAUNCH_3 = {
    'id': _LAUNCH_3_UUID,
    'started_at': _LAUNCH_3_START,
    'status': 'running',
    'hints': [],
}


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags',
            shipment_tools.DbShipment(
                name='shipment_name',
                ticket='A-1',
                maintainers=[],
                is_enabled=True,
                labels=[],
                schedule=shipment_tools.Schedule(
                    _NOW, shipment_tools.UnitOfTime.HOURS, 2,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1, 'SELECT 1',
                ),
                consumer=shipment_tools.TagsConsumerSettings(['tag1']),
                created_at=_NOW,
                updated_at=_NOW,
                status=shipment_tools.Status.READY,
            ),
        ),
        shipment_tools.get_shipment_insert_query(
            'passenger-tags',
            shipment_tools.DbShipment(
                name='shipment_name_1',
                ticket='A-1',
                maintainers=[],
                is_enabled=True,
                labels=[],
                schedule=shipment_tools.Schedule(
                    _NOW, shipment_tools.UnitOfTime.HOURS, 2,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1, 'SELECT 1',
                ),
                consumer=shipment_tools.TagsConsumerSettings(['tag1']),
                created_at=_NOW,
                updated_at=_NOW,
                status=shipment_tools.Status.READY,
            ),
        ),
        launch_tools.get_launch_insert_query(
            'passenger-tags',
            'shipment_name',
            launch_tools.Launch(
                uuid='9aec477f71074874b4e255f9fa31203e',
                started_at=_LAUNCH_1_START,
                is_failed=False,
                status='finished',
                errors=[],
                snapshot_status='fully_applied',
                record_counts=None,
            ),
        ),
        launch_tools.get_launch_insert_query(
            'tags', 'shipment_name', _DB_LAUNCH_1,
        ),
        launch_tools.get_launch_insert_query(
            'tags', 'shipment_name', _DB_LAUNCH_2,
        ),
        launch_tools.get_launch_insert_query(
            'tags', 'shipment_name', _DB_LAUNCH_3,
        ),
    ],
)
@pytest.mark.parametrize(
    'consumer_name, shipment_name, start_time_filter_begin, '
    'start_time_filter_end, limit, expected_list_items',
    [
        pytest.param(
            'tags',
            'shipment_name',
            _LAUNCH_1_START - dt.timedelta(hours=1),
            _LAUNCH_1_START,
            50,
            [],
            id='too_early',
        ),
        pytest.param(
            'tags',
            'shipment_name',
            _LAUNCH_3_START + dt.timedelta(hours=1),
            _LAUNCH_3_START + dt.timedelta(hours=2),
            50,
            [],
            id='too_lately',
        ),
        pytest.param(
            'tags',
            'shipment_name',
            _LAUNCH_1_START,
            _LAUNCH_2_START,
            50,
            [_LIST_LAUNCH_1],
            id='include_first_exclude_second',
        ),
        pytest.param(
            'tags',
            'shipment_name',
            _LAUNCH_1_START,
            _LAUNCH_3_START,
            50,
            [_LIST_LAUNCH_1, _LIST_LAUNCH_2],
            id='exclude_third',
        ),
        pytest.param(
            'tags',
            'shipment_name',
            _LAUNCH_1_START,
            _LAUNCH_3_START + dt.timedelta(hours=1),
            50,
            [_LIST_LAUNCH_1, _LIST_LAUNCH_2, _LIST_LAUNCH_3],
            id='all_launches',
        ),
        pytest.param(
            'tags',
            'shipment_name',
            _LAUNCH_1_START,
            _LAUNCH_3_START + dt.timedelta(hours=1),
            1,
            [_LIST_LAUNCH_1],
            id='limit',
        ),
        pytest.param(
            'tags',
            'shipment_name_1',
            _LAUNCH_1_START,
            _LAUNCH_3_START + dt.timedelta(hours=1),
            1,
            [],
            id='different_shipment_name',
        ),
        pytest.param(
            'passenger-tags',
            'shipment_name',
            _LAUNCH_1_START,
            _LAUNCH_3_START + dt.timedelta(hours=1),
            1,
            [],
            id='different_consumer_name',
        ),
    ],
)
async def test_launch_history(
        taxi_segments_provider,
        consumer_name: str,
        shipment_name: str,
        start_time_filter_begin: dt.datetime,
        start_time_filter_end: dt.datetime,
        limit: int,
        expected_list_items: List[Dict[str, Any]],
):
    response = await taxi_segments_provider.post(
        f'/admin/v1/shipment/launch-history/search?consumer={consumer_name}'
        f'&shipment={shipment_name}',
        json={
            'filters': {
                'start_time_range': {
                    'begin': start_time_filter_begin.isoformat(),
                    'end': start_time_filter_end.isoformat(),
                },
            },
            'limit': limit,
        },
    )
    assert response.status_code == 200

    response_data = response.json()
    for launch in response_data['launches']:
        launch['started_at'] = dt.datetime.fromisoformat(launch['started_at'])
    assert response_data == {'launches': expected_list_items}
