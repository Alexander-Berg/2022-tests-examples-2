# pylint: disable=C5521, W0621
import datetime

import pytest

from tests_tags.tags import tags_tools
from tests_tags.tags import yql_services_fixture
from tests_tags.tags.yql_services_fixture import (  # noqa: F401
    local_yql_services,
)

_FORMAT = '%Y-%m-%d'
_NOW = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)
_TTL = _NOW + datetime.timedelta(days=10)
_TABLE = 'home/taxi/testsuite/features/tags/history_search/table_name'
_TAGS_AUTH = 'OAuth tags-robot-token'
_YT_DATA = [
    {
        'active': 1,
        'entity': f'entity{i}',
        'entity_type': 'dbid_uud',
        'provider': f'provider{i}',
        'tag': f'tag{i}',
        'timestamp': _NOW.isoformat(
            timespec='microseconds' if i % 2 else 'seconds',
        ),
        'ttl': (
            'infinity' if i % 2 else _TTL.isoformat(timespec='microseconds')
        ),
    }
    for i in range(10)
]


@pytest.mark.yt(
    schemas=[
        {
            'path': '//' + _TABLE,
            'attributes': {
                'schema': [
                    {'name': 'active', 'type': 'uint64'},
                    {'name': 'entity', 'type': 'string'},
                    {'name': 'entity_type', 'type': 'string'},
                    {'name': 'provider', 'type': 'string'},
                    {'name': 'tag', 'type': 'string'},
                    {'name': 'timestamp', 'type': 'string'},
                    {'name': 'ttl', 'type': 'string'},
                ],
            },
        },
    ],
    static_table_data=[{'path': '//' + _TABLE, 'values': _YT_DATA}],
)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_history_operations(
            [[yql_services_fixture.DEFAULT_OPERATION_ID, _TABLE, _NOW]],
        ),
    ],
)
@pytest.mark.parametrize(
    'offset, limit',
    [(None, None), (1, None), (None, 4), (3, 4), (10, 10000), (None, 30)],
)
async def test_admin_history_poll(
        taxi_tags,
        yt_client,
        local_yql_services,  # noqa: F811
        offset,
        limit,
        yt_apply_force,
):
    yt_offset = offset or 0
    yt_limit = limit or 1000
    result = _YT_DATA[yt_offset : yt_offset + yt_limit]

    local_yql_services.add_results_response(
        {
            'id': yql_services_fixture.DEFAULT_OPERATION_ID,
            'status': 'COMPLETED',
            'data': [{'Write': [{}]}],
            'updatedAt': '2019-06-18T07:04:50.528Z',
        },
    )

    body = {'operation_id': yql_services_fixture.DEFAULT_OPERATION_ID}
    if offset is not None:
        body['offset'] = offset
    if limit is not None:
        body['limit'] = limit
    response = await taxi_tags.post('v1/admin/tags/history/poll', body)

    assert local_yql_services.times_called['results'] == 1
    assert local_yql_services.times_called['results_data'] == 0

    assert response.status_code == 200

    response = response.json()
    status = response['status']
    assert status == 'completed'
    assert _TABLE == response['path']
    assert len(response['events']) == len(result)

    for data, expected in zip(response['events'], result):
        assert data['action'] == (
            'assign' if expected['active'] == 1 else 'remove'
        )
        assert data['entity_name'] == expected['entity']
        for key in ['entity_type', 'provider', 'tag']:
            assert data[key] == expected[key]
        for key in ['timestamp', 'ttl']:
            if data[key] == 'infinity':
                assert expected[key] == 'infinity'
            else:
                if expected[key][-3:] == ':00':
                    # original data in YT does not contain ms and tz parts
                    timezone_suffix = '.000000+0000'
                else:
                    # original data in YT does not contain tz part
                    timezone_suffix = '+0000'
                assert data[key] == expected[key] + timezone_suffix


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_history_operations(
            [[yql_services_fixture.DEFAULT_OPERATION_ID, _TABLE, _NOW]],
        ),
    ],
)
@pytest.mark.parametrize(
    'offset, limit',
    [(-1, None), (None, 0), (None, 10001), (None, 'str'), ('str', None)],
)
async def test_bad_history_poll(
        taxi_tags, local_yql_services, offset, limit,  # noqa: F811
):
    body = {'operation_id': yql_services_fixture.DEFAULT_OPERATION_ID}
    if offset is not None:
        body['offset'] = offset
    if limit is not None:
        body['limit'] = limit
    response = await taxi_tags.post('v1/admin/tags/history/poll', body)

    assert local_yql_services.times_called['results'] == 0
    assert response.status_code == 400
