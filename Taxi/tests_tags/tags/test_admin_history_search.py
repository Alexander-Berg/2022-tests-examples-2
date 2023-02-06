import datetime
import json
from typing import Optional
from typing import Tuple

import pytest
import pytz

from tests_tags.tags import constants
from tests_tags.tags import tags_tools


_DATE_FORMAT = '%Y-%m-%d'
_NOW = datetime.datetime(2020, 4, 20, 12, 0, 0, tzinfo=pytz.timezone('UTC'))
_FROM = _NOW - datetime.timedelta(days=20)
_DAY_LOGS_START = _NOW - datetime.timedelta(days=10)
_HOUR_LOGS_START = datetime.datetime(
    2020, 4, 19, 10, 0, 0, tzinfo=pytz.timezone('UTC'),
)
_HOUR_LOGS_NEW_DAY = datetime.datetime(
    2020, 4, 20, 0, 0, 0, tzinfo=pytz.timezone('UTC'),
)
_OLD_LOGS_END = _NOW - datetime.timedelta(days=11)
_TTL = (_NOW + datetime.timedelta(days=1)).strftime('%FT%T')
_HISTORY_PATH_PREFIX = '//home/taxi/testsuite/features/tags/history_search'
_NEW_LOGS_PATH_PREFIX = '//home/logfeller/logs/taxi-tags-tag-event-log'


def _check_tables_usage(
        query: str,
        start_from: int,
        path: str,
        from_date: Optional[str],
        to_date: Optional[str],
        should_be_used: bool,
        is_new_tables: bool,
):
    timestamp = (
        'timestamp_field as timestamp' if is_new_tables else 'timestamp'
    )
    subquery = (
        f'select CAST(active as UInt64) as active, entity, entity_type, '
        f'provider, tag, {timestamp}, ttl\nfrom concatYtTablesRange(\'{path}\''
        f', \'{from_date}\', \'{to_date}'
    )
    position = query.find(subquery, start_from)
    if should_be_used:
        assert position > 0
    else:
        assert position == -1


@pytest.mark.yt(
    schemas=[
        {
            'path': f'{_NEW_LOGS_PATH_PREFIX}/1d/2020-04-{day}',
            'attributes': {'schema': [{'name': 'id', 'type': 'string'}]},
        }
        for day in range(10, 20)
    ]
    + [
        {
            'path': f'{_NEW_LOGS_PATH_PREFIX}/1h/2020-04-20T0{hour}:00:00',
            'attributes': {},
        }
        for hour in range(9)
    ]
    + [
        {
            'path': f'{_NEW_LOGS_PATH_PREFIX}/1h/2020-04-19T{hour}:00:00',
            'attributes': {},
        }
        for hour in range(10, 23)
    ],
)
@pytest.mark.nofilldb()
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'entities, entity_types, tags, providers, from_datetime, to_datetime',
    [
        (None, None, None, None, _FROM, None),
        (['some_entity'], None, None, None, _FROM, None),
        (None, ['dbid_uuid'], None, None, _FROM, None),
        (None, None, ['', 'empty_tag_ok'], None, _FROM, None),
        (None, None, None, ['provider'], _FROM, None),
        pytest.param(
            None,
            None,
            None,
            None,
            _NOW - datetime.timedelta(days=25),
            _NOW - datetime.timedelta(days=24),
            id='too old time range without new tables',
        ),
        pytest.param(
            None,
            None,
            None,
            None,
            _NOW - datetime.timedelta(days=1),
            None,
            id='recent time range without old tables',
        ),
        pytest.param(
            None,
            None,
            None,
            None,
            _FROM,
            _NOW + datetime.timedelta(days=10),
            id='time range in future is ok',
        ),
        pytest.param(
            ['entity1', 'entity2'],
            ['dbid_uuid', 'park', 'car_number'],
            ['tag_name', ''],
            ['provider'],
            _FROM,
            _NOW - datetime.timedelta(days=3),
            id='time range in past',
        ),
    ],
)
async def test_admin_history_search(
        taxi_tags,
        entities,
        entity_types,
        tags,
        providers,
        from_datetime: datetime.datetime,
        to_datetime: Optional[datetime.datetime],
        mockserver,
        pgsql,
        yt_client,
):
    use_old_logs = from_datetime <= _OLD_LOGS_END
    use_new_logs = to_datetime is None or to_datetime >= _DAY_LOGS_START

    @mockserver.json_handler('/yql/api/v2/operations')
    def handler(request):
        assert request.args == {}
        assert request.headers['User-Agent'] == constants.USER_AGENT
        assert request.headers['Authorization'] == constants.TAGS_AUTH

        requested_data = json.loads(request.get_data())
        query = requested_data['content']
        prefix = (
            'use chyt.hahn/robot-tags-alias;\ncreate table `'
            + _HISTORY_PATH_PREFIX
            + '/'
        )
        pos = query.find(prefix)
        assert pos == 0

        engine = f'`\nengine = YtTable(\'{{expiration_time="{_TTL}"}}\')'
        pos = query.find(engine, len(prefix))
        assert pos > 0
        pos += len(engine)

        to_date = (
            _NOW.strftime(_DATE_FORMAT)
            if to_datetime is None
            else to_datetime.strftime(_DATE_FORMAT)
        )
        _check_tables_usage(
            query,
            pos,
            '//home/taxi/production/features/tags/events/raw_entries',
            from_datetime.strftime(_DATE_FORMAT),
            to_date,
            use_old_logs,
            False,
        )

        from_date = from_datetime.strftime(_DATE_FORMAT)
        _check_tables_usage(
            query,
            pos,
            _NEW_LOGS_PATH_PREFIX + '/1d',
            max('2020-04-10', from_date),
            min('2020-04-19', to_date),
            use_new_logs,
            True,
        )
        if use_old_logs and use_new_logs:
            assert query.find('\nunion all\n', pos) > 0

        if to_datetime is not None:
            pos = query.find(to_datetime.strftime(_DATE_FORMAT), pos)
            assert pos > 0
            pos += len(to_datetime.strftime(_DATE_FORMAT))
        else:
            pos = len(prefix)
        pos = query.find('\')\nwhere', pos)
        assert pos > 0

        for column, values in zip(
                ['entity', 'entity_type', 'tag', 'provider'],
                [entities, entity_types, tags, providers],
        ):
            if values is not None:
                filter_pos = query.find(
                    column + ' in (\'' + '\', \''.join(values) + '\')', pos,
                )
                assert filter_pos > 0

        mock_response = (
            '{{"id": "operation_id_{}", "status": "RUNNING"}}'.format(
                handler.times_called,
            )
        )
        return mockserver.make_response(mock_response, 200)

    data = {'from': from_datetime.isoformat()}
    for name, filter_values in zip(
            ['entities', 'entity_types', 'tags', 'providers'],
            [entities, entity_types, tags, providers],
    ):
        if filter_values is not None:
            data[name] = filter_values
    if to_datetime is not None:
        data['to'] = to_datetime.isoformat()
    response = await taxi_tags.post('v1/admin/tags/history/search', data)

    assert response.status_code == 200
    response = response.json()
    assert response['operation_id'] == 'operation_id_0'
    path = response['path']
    assert path.find(_HISTORY_PATH_PREFIX[2:]) == 0

    tags_tools.verify_inserted_operations(
        [
            {
                'operation_id': 'operation_id_0',
                'created': _NOW.replace(tzinfo=None),
            },
        ],
        pgsql['tags'],
    )


@pytest.mark.yt(
    schemas=[
        {
            'path': f'{_NEW_LOGS_PATH_PREFIX}/1d/2020-04-{day}',
            'attributes': {'schema': [{'name': 'id', 'type': 'string'}]},
        }
        for day in range(10, 19)
    ]
    + [
        {
            'path': f'{_NEW_LOGS_PATH_PREFIX}/1h/2020-04-20T0{hour}:00:00',
            'attributes': {},
        }
        for hour in range(10)
    ]
    + [
        {
            'path': f'{_NEW_LOGS_PATH_PREFIX}/1h/2020-04-19T{hour}:00:00',
            'attributes': {},
        }
        for hour in range(10, 24)
    ],
)
@pytest.mark.nofilldb()
@pytest.mark.now(_NOW.isoformat())
# day tables exist from 2020-04-10 to 2020-04-18, and 2020-04-19 parametrized
# hour tables exist from 2020-04-19T10:00:00 to 2020-04-20T09:00:00
@pytest.mark.parametrize(
    'from_, to_, create_last_day_table, use_old_logs, days_interval, '
    'hours_interval',
    [
        (
            _FROM,
            None,
            False,
            True,
            ('2020-04-10', '2020-04-18'),
            ('2020-04-19T10:00:00', '2020-04-20T09:00:00'),
        ),
        (_FROM, None, True, True, None, None),
        pytest.param(
            _NOW - datetime.timedelta(days=15),
            _NOW - datetime.timedelta(days=14),
            False,
            True,
            None,
            None,
            id='too old time range with only old tables',
        ),
        pytest.param(
            _NOW - datetime.timedelta(days=1),
            None,
            False,
            False,
            None,
            ('2020-04-19T10:00:00', '2020-04-20T09:00:00'),
            id='only hour tables usage, without day tables',
        ),
        pytest.param(
            _NOW - datetime.timedelta(days=1),
            None,
            True,
            False,
            ('2020-04-19', '2020-04-19'),
            ('2020-04-20T00:00:00', '2020-04-20T09:00:00'),
            id='new day tables and part of hour tables usage',
        ),
        pytest.param(
            _FROM,
            _NOW + datetime.timedelta(days=10),
            True,
            True,
            ('2020-04-10', '2020-04-19'),
            ('2020-04-20T00:00:00', '2020-04-20T09:00:00'),
            id='all day tables and partial hour tables',
        ),
        pytest.param(
            _FROM,
            _NOW + datetime.timedelta(days=1),
            False,
            True,
            ('2020-04-10', '2020-04-18'),
            ('2020-04-19T10:00:00', '2020-04-20T09:00:00'),
            id='almost all day tables and all hour tables',
        ),
        pytest.param(
            _NOW - datetime.timedelta(hours=3),
            _NOW + datetime.timedelta(days=1),
            True,
            False,
            None,
            ('2020-04-20T00:00:00', '2020-04-20T09:00:00'),
            id='only current day hour tables',
        ),
        pytest.param(
            _NOW - datetime.timedelta(hours=8),
            _NOW - datetime.timedelta(hours=6),
            True,
            False,
            None,
            ('2020-04-20T00:00:00', '2020-04-20T09:00:00'),
            id='take current day hour tables, but do not filter them',
        ),
        pytest.param(
            _NOW - datetime.timedelta(days=1),
            _NOW - datetime.timedelta(hours=6),
            False,
            False,
            None,
            ('2020-04-19T10:00:00', '2020-04-20T09:00:00'),
            id='take all hour tables, but do not filter them',
        ),
        pytest.param(
            _NOW - datetime.timedelta(days=3),
            _NOW - datetime.timedelta(hours=9),
            True,
            False,
            ('2020-04-17', '2020-04-19'),
            None,
            id='take only previous days logs without hours',
        ),
    ],
)
async def test_tables_ranges_usage(
        taxi_tags,
        from_: datetime.datetime,
        to_: Optional[datetime.datetime],
        create_last_day_table: bool,
        use_old_logs: bool,
        days_interval: Optional[Tuple[str, str]],
        hours_interval: Optional[Tuple[str, str]],
        mockserver,
        yt_client,
        yt_apply_force,
):
    if create_last_day_table:
        yt_client.create_table(
            f'{_NEW_LOGS_PATH_PREFIX}/1d/2020-04-19',
            attributes={'schema': [{'name': 'id', 'type': 'string'}]},
        )

    assert use_old_logs == (from_ <= _OLD_LOGS_END)
    use_new_day_logs = days_interval is not None
    use_hour_logs = hours_interval is not None

    @mockserver.json_handler('/yql/api/v2/operations')
    def handler(request):
        mock_response = (
            '{{"id": "operation_id_{}", "status": "RUNNING"}}'.format(
                handler.times_called,
            )
        )
        return mockserver.make_response(mock_response, 200)

    data = {'from': from_.isoformat()}
    if to_ is not None:
        data['to'] = to_.isoformat()
    response = await taxi_tags.post('v1/admin/tags/history/search', data)
    assert response.status_code == 200

    yql_request = handler.next_call()['request']
    query = json.loads(yql_request.get_data())['content']

    to_date = (
        _NOW.strftime(_DATE_FORMAT)
        if to_ is None
        else to_.strftime(_DATE_FORMAT)
    )
    _check_tables_usage(
        query,
        0,
        '//home/taxi/production/features/tags/events/raw_entries',
        from_.strftime(_DATE_FORMAT),
        to_date,
        use_old_logs,
        False,
    )
    _check_tables_usage(
        query,
        0,
        _NEW_LOGS_PATH_PREFIX + '/1d',
        None if days_interval is None else days_interval[0],
        None if days_interval is None else days_interval[1],
        use_new_day_logs,
        True,
    )
    _check_tables_usage(
        query,
        0,
        _NEW_LOGS_PATH_PREFIX + '/1h',
        None if hours_interval is None else hours_interval[0],
        None if hours_interval is None else hours_interval[1],
        use_hour_logs,
        True,
    )

    tables_usage = sum([use_old_logs, use_new_day_logs, use_hour_logs])
    pos = 0
    for _ in range(1, tables_usage):
        pos = query.find('\nunion all\n', pos)
        assert pos > 0
        pos += 11

    if not tables_usage:
        assert query.find('\nunion all\n') == -1


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'data',
    [
        ({'entity_types': ['invalid_type'], 'from': _NOW.isoformat()}),
        ({'from': 'not timestamp'}),
        ({'from': _NOW.isoformat(), 'to': '2019-02-04T23:59:59+0000'}),
        ({'from': _NOW.isoformat(), 'to': '2019-02-05T02:59:59+0300'}),
        ({'from': _NOW.isoformat(), 'to': _NOW.isoformat()}),
        ({}),
    ],
)
async def test_admin_bad_history_search_bad_requests(taxi_tags, data, pgsql):
    response = await taxi_tags.post('v1/admin/tags/history/search', data)
    assert response.status_code == 400
    tags_tools.verify_inserted_operations([], pgsql['tags'])
