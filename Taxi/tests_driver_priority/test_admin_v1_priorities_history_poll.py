import datetime
from typing import Any
from typing import Dict
from typing import Optional

import pytest


_NOW = datetime.datetime(2021, 9, 9, 12, 0, 0)
_NOW_LOCAL = _NOW + datetime.timedelta(hours=3)
_DAY = datetime.timedelta(days=1)

_AUTH = 'OAuth driver-priority-robot-token'
_USER_AGENT = 'Taxi-Driver-Priority-Service'
_OPERATION_ID = 'some_operation_id'
_OPERATION_RUNNING = 'in_progress'
_OPERATION_FAILED = 'something_went_wrong'
_TABLE_PATH = (
    'home/taxi/testsuite/features/driver-priority/history_search/table_name'
)
_YT_DATA = [
    {
        'change_type': 2,  # TODO: convert to string
        'dbid_uuid': f'dbid_uuid{i}',
        'deleted': 1 if i % 4 else 0,
        'is_temporary': 0,
        'lcl_dttm': _NOW_LOCAL.isoformat(sep=' ', timespec='seconds'),
        'priority_key': 'priority_name',
        'priority_value_change': i * (-1 if i % 2 else 1),
        'tariff_zone': 'spb',
        'utc_dttm': _NOW.isoformat(timespec='seconds'),
        'value': i,
    }
    for i in range(10)
]


@pytest.mark.yt(
    schemas=[
        {
            'path': f'//{_TABLE_PATH}',
            'attributes': {
                'schema': [
                    {'name': 'change_type', 'type': 'int64'},
                    {'name': 'dbid_uuid', 'type': 'string'},
                    {'name': 'deleted', 'type': 'int64'},
                    {'name': 'is_temporary', 'type': 'int64'},
                    {'name': 'lcl_dttm', 'type': 'string'},
                    {'name': 'priority_key', 'type': 'string'},
                    {'name': 'priority_value_change', 'type': 'int64'},
                    {'name': 'tariff_zone', 'type': 'string'},
                    {'name': 'utc_dttm', 'type': 'string'},
                    {'name': 'value', 'type': 'int64'},
                ],
            },
        },
    ],
    static_table_data=[{'path': '//' + _TABLE_PATH, 'values': _YT_DATA}],
)
@pytest.mark.pgsql(
    'driver_priority',
    queries=[
        f'INSERT INTO service.yql_history_operations VALUES '
        f'(\'{_OPERATION_ID}\', \'{_TABLE_PATH}\', \'{_NOW + _DAY}\'), '
        f'(\'{_OPERATION_RUNNING}\', \'{_TABLE_PATH}\', \'{_NOW + _DAY}\'), '
        f'(\'{_OPERATION_FAILED}\', \'{_TABLE_PATH}\', \'{_NOW + _DAY}\');',
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'operation_id, offset, limit, expected_code, expected_operation_status',
    [
        pytest.param(
            'missing', None, None, 404, '', id='missing operation id',
        ),
        pytest.param(
            _OPERATION_ID,
            None,
            None,
            200,
            'completed',
            id='read with default parameters',
        ),
        pytest.param(
            _OPERATION_ID,
            4,
            2,
            200,
            'completed',
            id='read with offset and limit',
        ),
        pytest.param(
            _OPERATION_ID, 50, None, 200, 'completed', id='empty result',
        ),
        pytest.param(
            _OPERATION_RUNNING, None, None, 200, 'running', id='no result',
        ),
        pytest.param(
            _OPERATION_FAILED, None, None, 200, 'failed', id='no result',
        ),
    ],
)
async def test_handler(
        taxi_driver_priority,
        operation_id: str,
        offset: Optional[int],
        limit: Optional[int],
        expected_code: int,
        expected_operation_status: str,
        mockserver,
        yt_client,
):
    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<req_operation_id>\w+)', regex=True,
    )
    def status_handler(request, req_operation_id):
        assert request.args == {}
        assert request.headers['User-Agent'] == _USER_AGENT
        assert request.headers['Authorization'] == _AUTH
        assert operation_id == req_operation_id

        status = 'RUNNING'
        if expected_operation_status == 'completed':
            status = 'COMPLETED'
        elif expected_operation_status == 'failed':
            status = 'ERROR'
        mock_response = f'{{"id": "operation_id_0", "status": "{status}"}}'
        return mockserver.make_response(
            mock_response, 200, content_type='application/json',
        )

    data: Dict[str, Any] = {'operation_id': operation_id}
    if offset is not None:
        data['offset'] = offset
    if limit is not None:
        data['limit'] = limit
    headers = {'X-Yandex-Login': 'login'}

    response = await taxi_driver_priority.post(
        'admin/v1/priorities/history/poll', data, headers=headers,
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        assert status_handler.has_calls

        response_json = response.json()
        assert response_json['status'] == expected_operation_status
        assert response_json['result_table_path'] == _TABLE_PATH
        if expected_operation_status == 'completed':
            assert len(response_json['priority_changes']) == len(
                _YT_DATA[(offset or 0) : (offset or 0) + (limit or 50)],
            )
        else:
            assert 'priority_changes' not in response_json
