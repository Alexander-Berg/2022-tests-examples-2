import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest
import pytz

from tests_driver_priority import db_tools


_NOW = datetime.datetime(2021, 9, 9, 12, 0, 0, tzinfo=pytz.timezone('UTC'))

_AUTH = 'OAuth driver-priority-robot-token'
_USER_AGENT = 'Taxi-Driver-Priority-Service'
_LOGIN = 'login'

_LOGS_PATH_PREFIX = (
    '//home/taxi/production/features/driver-priority/priority_changes'
)

DAY_TABLES = [f'2021-09-0{day}' for day in range(7, 9)]


@pytest.mark.yt(
    schemas=[
        {
            'path': f'{_LOGS_PATH_PREFIX}/days/{day_table}',
            'attributes': {'schema': [{'name': 'id', 'type': 'string'}]},
        }
        for day_table in DAY_TABLES
    ],
)
@pytest.mark.nofilldb()
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'from_datetime, to_datetime, priorities_filter, yt_nodes, expected_code',
    [
        pytest.param(_NOW, None, None, None, 400, id='time range is zero'),
        pytest.param(
            _NOW - datetime.timedelta(hours=24),
            _NOW - datetime.timedelta(hours=25),
            None,
            None,
            400,
            id='time range is invalid',
        ),
        pytest.param(
            _NOW - datetime.timedelta(days=2),
            None,
            None,
            DAY_TABLES,
            200,
            id='time range is valid',
        ),
        pytest.param(
            _NOW - datetime.timedelta(hours=7),
            None,
            None,
            [],
            200,
            id='time range is today',
        ),
        pytest.param(
            _NOW - datetime.timedelta(days=1),
            _NOW - datetime.timedelta(hours=7),
            None,
            DAY_TABLES[1:],
            200,
            id='time range is yesterday & today',
        ),
        pytest.param(
            _NOW - datetime.timedelta(days=2),
            _NOW + datetime.timedelta(days=1),
            None,
            DAY_TABLES,
            200,
            id='time range in future is ok',
        ),
        pytest.param(
            _NOW - datetime.timedelta(days=2),
            _NOW - datetime.timedelta(days=1),
            None,
            DAY_TABLES,
            200,
            id='time range in past',
        ),
        pytest.param(
            _NOW - datetime.timedelta(days=2),
            _NOW - datetime.timedelta(days=1),
            [],
            DAY_TABLES,
            400,
            id='empty priorities filter',
        ),
        pytest.param(
            _NOW - datetime.timedelta(days=2),
            _NOW - datetime.timedelta(days=1),
            ['sticker', 'lightbox'],
            DAY_TABLES,
            200,
            id='priorities filter not empty',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        from_datetime: datetime.datetime,
        to_datetime: Optional[datetime.datetime],
        priorities_filter: Optional[List[str]],
        yt_nodes: Optional[List[str]],
        expected_code: int,
        mockserver,
        testpoint,
        pgsql,
        yt_client,
):
    path = None

    @testpoint('generated_path')
    def _generated_path(data):
        nonlocal path
        path = data['path']

    @testpoint('yt_nodes')
    def _yt_nodes(data):
        nonlocal yt_nodes
        assert yt_nodes is not None
        assert data['nodes'] == yt_nodes

    @mockserver.json_handler('/yql/api/v2/operations')
    def _v2_operation(request):
        assert request.args == {}
        assert request.headers['User-Agent'] == _USER_AGENT
        assert request.headers['Authorization'] == _AUTH

        mock_response = '{"id": "operation_id_0", "status": "RUNNING"}'
        return mockserver.make_response(
            mock_response, 200, content_type='application/json',
        )

    data: Dict[str, Any] = {
        'dbid': 'dbid',
        'uuid': 'uuid',
        'from': from_datetime.isoformat(),
    }
    if to_datetime is not None:
        data['to'] = to_datetime.isoformat()
    if priorities_filter is not None:
        data['priorities'] = priorities_filter
    headers = {'X-Yandex-Login': _LOGIN}

    response = await taxi_driver_priority.post(
        'admin/v1/priorities/history/search', data, headers=headers,
    )
    assert response.status_code == expected_code

    data = db_tools.select_named(
        'SELECT * FROM service.yql_history_operations',
        pgsql['driver_priority'],
    )

    if expected_code == 200:
        assert _generated_path.has_calls is True
        assert _yt_nodes.has_calls is True
        response_json = response.json()
        assert response_json['operation_id'] == 'operation_id_0'
        assert data == [
            {
                'operation_id': 'operation_id_0',
                'path': path,
                'valid_until': datetime.datetime(
                    2021, 9, 9, 12, 0, 0,
                ) + datetime.timedelta(hours=12),
            },
        ]
    else:
        assert data == []
