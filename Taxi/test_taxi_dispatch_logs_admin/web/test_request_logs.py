# pylint: disable=C0302,redefined-outer-name

import datetime
import json

import pytest
import yt.wrapper as yt

from taxi.stq import client as stq_client

from taxi_dispatch_logs_admin.api.common import request_logs_logic
from taxi_dispatch_logs_admin.common import helpers
from taxi_dispatch_logs_admin.common import version
from taxi_dispatch_logs_admin.generated.stq3 import stq_settings
from test_taxi_dispatch_logs_admin.common import mock


class RequestLogsSetup:
    def __init__(self):
        self.pg_mock = mock.PgMock()
        self.stq_mock = mock.StqMock()
        self.yt_mock = mock.YtMock()
        self.uuid_mock = mock.UuidMock()
        self.pg_insert_query = """
            INSERT INTO common.yt_tasks(
                version, stq_queue, stq_task_id, log_type,
                from_timestamp, to_timestamp,
                order_id, draw_id, extra_filters
            )
            VALUES(
                $1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb
            )
            ON CONFLICT(
                version, log_type, from_timestamp, to_timestamp,
                COALESCE(order_id, ''), COALESCE(draw_id, ''),
                COALESCE(extra_filters, '{}'::jsonb)
            )
            DO UPDATE
            SET stq_task_id = $10,
                status = DEFAULT,
                yt_results = DEFAULT,
                modified_timestamp = DEFAULT;
        """

    def saturated(self):
        return (
            self.pg_mock.saturated()
            and self.stq_mock.saturated()
            and self.yt_mock.saturated()
        )


@pytest.fixture
def request_logs_setup(monkeypatch):
    setup = RequestLogsSetup()
    monkeypatch.setattr(helpers, 'pg_perform', setup.pg_mock.pg_perform)
    monkeypatch.setattr(stq_client, 'put', setup.stq_mock.stq_client_put)
    monkeypatch.setattr(
        request_logs_logic,
        'generate_task_id',
        setup.uuid_mock.generate_task_id,
    )
    monkeypatch.setattr(helpers, 'yt_configure', setup.yt_mock.yt_configure)
    monkeypatch.setattr(yt, 'read_table', setup.yt_mock.yt_read_table)
    return setup


@pytest.mark.parametrize(
    """
        params,
        pg_fetch_result,
        expected_fetch_query,
        expected_task_params,
        expected_queue,
        expected_response
    """,
    [
        (
            {
                'log_type': 'buffer_dispatch',
                'from_dt': '2019-01-01T12:00:00Z',
                'to_dt': '2019-01-01T12:30:00Z',
                'order_id': 'order_id_0',
            },
            [],
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id = 'order_id_0')
                    AND (draw_id IS NULL);
            """,
            {
                'log_type': 'buffer_dispatch',
                'task_id': '0',
                'from_dt': '2019-01-01T12:00:00+00:00',
                'to_dt': '2019-01-01T12:30:00+00:00',
                'order_id': 'order_id_0',
                'draw_id': None,
                'extra_filters': {},
            },
            stq_settings.STQ_DISPATCH_LOGS_ADMIN_CHYT_IMPORTS_QUEUE,
            {
                'status': 'pending',
                'filters': {
                    'log_type': 'buffer_dispatch',
                    'from_dt': helpers.to_localized_iso(
                        '2019-01-01T12:00:00Z',
                    ),
                    'to_dt': helpers.to_localized_iso('2019-01-01T12:30:00Z'),
                    'order_id': 'order_id_0',
                },
            },
        ),
    ],
)
async def test_scheduling(
        web_app_client,
        stq,
        request_logs_setup,
        params,
        pg_fetch_result,
        expected_fetch_query,
        expected_task_params,
        expected_queue,
        expected_response,
):
    request_logs_setup.pg_mock.expect(
        [
            mock.Expectation(
                mock.PgCallParams(
                    'fetch',
                    expected_fetch_query,
                    version.VERSION,
                    params['log_type'],
                    helpers.to_naive_utc_datetime(params['from_dt']),
                    helpers.to_naive_utc_datetime(params['to_dt']),
                ),
                return_value=pg_fetch_result,
            ),
            mock.Expectation(
                mock.PgCallParams(
                    'execute',
                    request_logs_setup.pg_insert_query,
                    version.VERSION,
                    expected_queue,
                    expected_task_params['task_id'],
                    params['log_type'],
                    helpers.to_naive_utc_datetime(params['from_dt']),
                    helpers.to_naive_utc_datetime(params['to_dt']),
                    expected_task_params['order_id'],
                    expected_task_params['draw_id'],
                    json.dumps(expected_task_params['extra_filters']),
                    expected_task_params['task_id'],
                ),
                return_value='INSERT 0 1',
            ),
        ],
    )

    response = await web_app_client.post('/request_logs/', params=params)

    assert response.status == 202
    assert await response.json() == expected_response
    assert stq[expected_queue].times_called == 1
    task = stq[expected_queue].next_call()
    assert task['id'] == expected_task_params['task_id']
    assert task['kwargs']['task_params'] == expected_task_params
    assert stq.is_empty
    assert request_logs_setup.saturated()


@pytest.mark.parametrize(
    """
        params,
        yt_log_rows,
        expected_fetch_query,
        expected_content
    """,
    [
        (
            {
                'log_type': 'tracks',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'order_id': 'order_id_0',
            },
            [
                {'col0': 'val00', 'col1': 'val01'},
                {'col0': 'val10', 'col1': 'val11'},
            ],
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id = 'order_id_0')
                    AND (draw_id IS NULL);
            """,
            {
                'log_type': 'tracks',
                'fastcgi_logs': [
                    {'col0': 'val00', 'col1': 'val01'},
                    {'col0': 'val10', 'col1': 'val11'},
                ],
            },
        ),
        (
            {
                'log_type': 'driver_dispatcher',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'order_id': 'order_id_0',
                'offset': 1,
                'limit': 2,
            },
            [
                {'col0': 'val00', 'col1': 'val01'},
                {'col0': 'val10', 'col1': 'val11'},
                {'col0': 'val20', 'col1': 'val21'},
                {'col0': 'val30', 'col1': 'val31'},
            ],
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id = 'order_id_0')
                    AND (draw_id IS NULL);
            """,
            {
                'log_type': 'driver_dispatcher',
                'fastcgi_logs': [
                    {'col0': 'val10', 'col1': 'val11'},
                    {'col0': 'val20', 'col1': 'val21'},
                ],
            },
        ),
        (
            {
                'log_type': 'tracks',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'order_id': 'order_id_0',
            },
            [
                {
                    '_yql_column_0': 'bin',
                    'col0': 'val00',
                    'col1': 'val01',
                    '_other': [
                        ['level', 'INFO'],
                        ['_yql_thread', 'bin'],
                        ['uri', '/do/work'],
                    ],
                },
                {
                    '_yql_column_0': 'bin',
                    'col0': 'val10',
                    'col1': 'val11',
                    '_other': [
                        ['level', 'DEBUG'],
                        ['_yql_thread', 'bin'],
                        ['uri', '/do/other/work'],
                    ],
                },
            ],
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id = 'order_id_0')
                    AND (draw_id IS NULL);
            """,
            {
                'log_type': 'tracks',
                'fastcgi_logs': [
                    {
                        'col0': 'val00',
                        'col1': 'val01',
                        'level': 'INFO',
                        'uri': '/do/work',
                    },
                    {
                        'col0': 'val10',
                        'col1': 'val11',
                        'level': 'DEBUG',
                        'uri': '/do/other/work',
                    },
                ],
            },
        ),
        (
            {
                'log_type': 'driver_dispatcher',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'order_id': 'order_id_0',
                'offset': 1,
                'limit': 2,
            },
            None,
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id = 'order_id_0')
                    AND (draw_id IS NULL);
            """,
            {'log_type': 'driver_dispatcher', 'fastcgi_logs': []},
        ),
    ],
)
async def test_flat_logs_fetching(
        web_app_client,
        request_logs_setup,
        params,
        yt_log_rows,
        expected_fetch_query,
        expected_content,
):

    yt_results = ['//path/to/0123_yql'] if yt_log_rows is not None else []
    modified_timestamp = datetime.datetime.utcnow()
    request_logs_setup.pg_mock.expect(
        [
            mock.Expectation(
                mock.PgCallParams(
                    'fetch',
                    expected_fetch_query,
                    version.VERSION,
                    params['log_type'],
                    helpers.to_naive_utc_datetime(params['from_dt']),
                    helpers.to_naive_utc_datetime(params['to_dt']),
                ),
                return_value=[
                    {
                        'status': 'completed',
                        'yt_results': yt_results,
                        'modified_timestamp': modified_timestamp,
                    },
                ],
            ),
        ],
    )
    if yt_results:
        request_logs_setup.yt_mock.expect_configure(
            mock.Expectation(('hahn.yt.yandex.net', 'FAKE_YT_TOKEN')),
        )

        request_logs_setup.yt_mock.expect_read_table(
            [
                mock.Expectation(
                    (yt_results[0], yt.JsonFormat()),
                    return_value=iter(yt_log_rows),
                ),
            ],
        )

    response = await web_app_client.post('/request_logs/', params=params)
    assert response.status == 200
    content = await response.json()
    assert content == expected_content
    assert request_logs_setup.saturated()


@pytest.mark.parametrize(
    """
        params,
        yt_orders_rows,
        yt_draw_rows,
        yt_candidates_rows,
        expected_fetch_query,
        expected_content
    """,
    [
        (
            {
                'log_type': 'buffer_dispatch',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'order_id': 'order_id_0',
            },
            [
                {
                    'order_id': 'order_id_0',
                    'draw_id': 'draw_id_0',
                    'orders_meta': 'orders_meta_0',
                },
                {
                    'order_id': 'order_id_0',
                    'draw_id': 'draw_id_1',
                    'orders_meta': 'orders_meta_1',
                },
            ],
            [
                {'draw_id': 'draw_id_0', 'draw_meta': 'draw_meta_0'},
                {'draw_id': 'draw_id_1', 'draw_meta': 'draw_meta_1'},
            ],
            [
                {
                    'driver_id': 'driver_id_0',
                    'draw_id': 'draw_id_0',
                    'driver_meta': 'driver_meta_0',
                },
                {
                    'driver_id': 'driver_id_1',
                    'draw_id': 'draw_id_0',
                    'driver_meta': 'driver_meta_1',
                },
                {
                    'driver_id': 'driver_id_2',
                    'draw_id': 'draw_id_1',
                    'driver_meta': 'driver_meta_2',
                },
                {
                    'driver_id': 'driver_id_3',
                    'draw_id': 'draw_id_1',
                    'driver_meta': 'driver_meta_3',
                },
            ],
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id = 'order_id_0')
                    AND (draw_id IS NULL);
            """,
            {
                'log_type': 'buffer_dispatch',
                'buffer_dispatch_logs': [
                    {
                        'orders_log_string': {
                            'order_id': 'order_id_0',
                            'draw_id': 'draw_id_0',
                            'orders_meta': 'orders_meta_0',
                        },
                        'draw_log_string': {
                            'draw_id': 'draw_id_0',
                            'draw_meta': 'draw_meta_0',
                        },
                        'candidates_logs': [
                            {
                                'driver_id': 'driver_id_0',
                                'draw_id': 'draw_id_0',
                                'driver_meta': 'driver_meta_0',
                            },
                            {
                                'driver_id': 'driver_id_1',
                                'draw_id': 'draw_id_0',
                                'driver_meta': 'driver_meta_1',
                            },
                        ],
                    },
                    {
                        'orders_log_string': {
                            'order_id': 'order_id_0',
                            'draw_id': 'draw_id_1',
                            'orders_meta': 'orders_meta_1',
                        },
                        'draw_log_string': {
                            'draw_id': 'draw_id_1',
                            'draw_meta': 'draw_meta_1',
                        },
                        'candidates_logs': [
                            {
                                'driver_id': 'driver_id_2',
                                'draw_id': 'draw_id_1',
                                'driver_meta': 'driver_meta_2',
                            },
                            {
                                'driver_id': 'driver_id_3',
                                'draw_id': 'draw_id_1',
                                'driver_meta': 'driver_meta_3',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'order_id': 'order_id_0',
            },
            None,
            None,
            None,
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id = 'order_id_0')
                    AND (draw_id IS NULL);
            """,
            {'log_type': 'buffer_dispatch', 'buffer_dispatch_logs': []},
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'order_id': 'order_id_0',
            },
            None,
            [
                {'draw_id': 'draw_id_0', 'draw_meta': 'draw_meta_0'},
                {'draw_id': 'draw_id_1', 'draw_meta': 'draw_meta_1'},
            ],
            [
                {
                    'driver_id': 'driver_id_0',
                    'draw_id': 'draw_id_0',
                    'driver_meta': 'driver_meta_0',
                },
                {
                    'driver_id': 'driver_id_1',
                    'draw_id': 'draw_id_0',
                    'driver_meta': 'driver_meta_1',
                },
                {
                    'driver_id': 'driver_id_2',
                    'draw_id': 'draw_id_1',
                    'driver_meta': 'driver_meta_2',
                },
                {
                    'driver_id': 'driver_id_3',
                    'draw_id': 'draw_id_1',
                    'driver_meta': 'driver_meta_3',
                },
            ],
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id = 'order_id_0')
                    AND (draw_id IS NULL);
            """,
            {
                'log_type': 'buffer_dispatch',
                'buffer_dispatch_logs': [
                    {
                        'draw_log_string': {
                            'draw_id': 'draw_id_0',
                            'draw_meta': 'draw_meta_0',
                        },
                        'candidates_logs': [
                            {
                                'driver_id': 'driver_id_0',
                                'draw_id': 'draw_id_0',
                                'driver_meta': 'driver_meta_0',
                            },
                            {
                                'driver_id': 'driver_id_1',
                                'draw_id': 'draw_id_0',
                                'driver_meta': 'driver_meta_1',
                            },
                        ],
                    },
                    {
                        'draw_log_string': {
                            'draw_id': 'draw_id_1',
                            'draw_meta': 'draw_meta_1',
                        },
                        'candidates_logs': [
                            {
                                'driver_id': 'driver_id_2',
                                'draw_id': 'draw_id_1',
                                'driver_meta': 'driver_meta_2',
                            },
                            {
                                'driver_id': 'driver_id_3',
                                'draw_id': 'draw_id_1',
                                'driver_meta': 'driver_meta_3',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'order_id': 'order_id_0',
            },
            [
                {
                    'order_id': 'order_id_0',
                    'draw_id': 'draw_id_0',
                    'orders_meta': 'orders_meta_0',
                },
                {
                    'order_id': 'order_id_0',
                    'draw_id': 'draw_id_1',
                    'orders_meta': 'orders_meta_1',
                },
            ],
            None,
            [
                {
                    'driver_id': 'driver_id_0',
                    'draw_id': 'draw_id_0',
                    'driver_meta': 'driver_meta_0',
                },
                {
                    'driver_id': 'driver_id_1',
                    'draw_id': 'draw_id_0',
                    'driver_meta': 'driver_meta_1',
                },
                {
                    'driver_id': 'driver_id_2',
                    'draw_id': 'draw_id_1',
                    'driver_meta': 'driver_meta_2',
                },
                {
                    'driver_id': 'driver_id_3',
                    'draw_id': 'draw_id_1',
                    'driver_meta': 'driver_meta_3',
                },
            ],
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id = 'order_id_0')
                    AND (draw_id IS NULL);
            """,
            {
                'log_type': 'buffer_dispatch',
                'buffer_dispatch_logs': [
                    {
                        'orders_log_string': {
                            'order_id': 'order_id_0',
                            'draw_id': 'draw_id_0',
                            'orders_meta': 'orders_meta_0',
                        },
                        'candidates_logs': [
                            {
                                'driver_id': 'driver_id_0',
                                'draw_id': 'draw_id_0',
                                'driver_meta': 'driver_meta_0',
                            },
                            {
                                'driver_id': 'driver_id_1',
                                'draw_id': 'draw_id_0',
                                'driver_meta': 'driver_meta_1',
                            },
                        ],
                    },
                    {
                        'orders_log_string': {
                            'order_id': 'order_id_0',
                            'draw_id': 'draw_id_1',
                            'orders_meta': 'orders_meta_1',
                        },
                        'candidates_logs': [
                            {
                                'driver_id': 'driver_id_2',
                                'draw_id': 'draw_id_1',
                                'driver_meta': 'driver_meta_2',
                            },
                            {
                                'driver_id': 'driver_id_3',
                                'draw_id': 'draw_id_1',
                                'driver_meta': 'driver_meta_3',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'draw_id': 'draw_id_0',
            },
            None,
            None,
            [
                {
                    'driver_id': 'driver_id_0',
                    'draw_id': 'draw_id_0',
                    'driver_meta': 'driver_meta_0',
                },
                {
                    'driver_id': 'driver_id_1',
                    'draw_id': 'draw_id_0',
                    'driver_meta': 'driver_meta_1',
                },
            ],
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id IS NULL)
                    AND (draw_id = 'draw_id_0');
            """,
            {
                'log_type': 'buffer_dispatch',
                'buffer_dispatch_logs': [
                    {
                        'candidates_logs': [
                            {
                                'driver_id': 'driver_id_0',
                                'draw_id': 'draw_id_0',
                                'driver_meta': 'driver_meta_0',
                            },
                            {
                                'driver_id': 'driver_id_1',
                                'draw_id': 'draw_id_0',
                                'driver_meta': 'driver_meta_1',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'draw_id': 'draw_id_0',
                'offset': 1,
                'limit': 2,
            },
            None,
            None,
            [
                {
                    'driver_id': 'driver_id_0',
                    'draw_id': 'draw_id_0',
                    'driver_meta': 'driver_meta_0',
                },
                {
                    'driver_id': 'driver_id_1',
                    'draw_id': 'draw_id_0',
                    'driver_meta': 'driver_meta_1',
                },
                {
                    'driver_id': 'driver_id_2',
                    'draw_id': 'draw_id_0',
                    'driver_meta': 'driver_meta_2',
                },
                {
                    'driver_id': 'driver_id_3',
                    'draw_id': 'draw_id_0',
                    'driver_meta': 'driver_meta_3',
                },
            ],
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id IS NULL)
                    AND (draw_id = 'draw_id_0');
            """,
            {
                'log_type': 'buffer_dispatch',
                'buffer_dispatch_logs': [
                    {
                        'candidates_logs': [
                            {
                                'driver_id': 'driver_id_1',
                                'draw_id': 'draw_id_0',
                                'driver_meta': 'driver_meta_1',
                            },
                            {
                                'driver_id': 'driver_id_2',
                                'draw_id': 'draw_id_0',
                                'driver_meta': 'driver_meta_2',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'draw_id': 'draw_id_0',
                'offset': 1,
                'limit': 2,
            },
            [
                {
                    'order_id': 'order_id_0',
                    'draw_id': 'draw_id_0',
                    'orders_meta': 'orders_meta_0',
                },
                {
                    'order_id': 'order_id_1',
                    'draw_id': 'draw_id_0',
                    'orders_meta': 'orders_meta_1',
                },
                {
                    'order_id': 'order_id_2',
                    'draw_id': 'draw_id_0',
                    'orders_meta': 'orders_meta_2',
                },
                {
                    'order_id': 'order_id_3',
                    'draw_id': 'draw_id_0',
                    'orders_meta': 'orders_meta_3',
                },
            ],
            None,
            None,
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id IS NULL)
                    AND (draw_id = 'draw_id_0');
            """,
            {
                'log_type': 'buffer_dispatch',
                'buffer_dispatch_logs': [
                    {
                        'orders_log_string': {
                            'order_id': 'order_id_1',
                            'draw_id': 'draw_id_0',
                            'orders_meta': 'orders_meta_1',
                        },
                        'candidates_logs': [],
                    },
                    {
                        'orders_log_string': {
                            'order_id': 'order_id_2',
                            'draw_id': 'draw_id_0',
                            'orders_meta': 'orders_meta_2',
                        },
                        'candidates_logs': [],
                    },
                ],
            },
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'order_id': 'order_id_0',
            },
            [
                {
                    'order_id': 'order_id_0',
                    'draw_id': 'draw_id_0',
                    'orders_meta': '{\n    \"lookup\" = #;\n}',
                    'geo_point': yt.yson.YsonEntity(),
                },
            ],
            None,
            None,
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id = 'order_id_0')
                    AND (draw_id IS NULL);
            """,
            {
                'log_type': 'buffer_dispatch',
                'buffer_dispatch_logs': [
                    {
                        'orders_log_string': {
                            'order_id': 'order_id_0',
                            'draw_id': 'draw_id_0',
                            'orders_meta': {'lookup': None},
                            'geo_point': None,
                        },
                        'candidates_logs': [],
                    },
                ],
            },
        ),
    ],
)
async def test_buffer_dispatch_logs_fetching(
        web_app_client,
        request_logs_setup,
        params,
        yt_orders_rows,
        yt_draw_rows,
        yt_candidates_rows,
        expected_fetch_query,
        expected_content,
):
    yt_results = {}
    if yt_orders_rows is not None:
        yt_results['//0123_buffer_dispatch_orders'] = yt_orders_rows
    if yt_draw_rows is not None:
        yt_results['//0123_buffer_dispatch_draw'] = yt_draw_rows
    if yt_candidates_rows is not None:
        yt_results['//0123_buffer_dispatch_candidates'] = yt_candidates_rows

    modified_timestamp = datetime.datetime.utcnow()
    request_logs_setup.pg_mock.expect(
        [
            mock.Expectation(
                mock.PgCallParams(
                    'fetch',
                    expected_fetch_query,
                    version.VERSION,
                    params['log_type'],
                    helpers.to_naive_utc_datetime(params['from_dt']),
                    helpers.to_naive_utc_datetime(params['to_dt']),
                ),
                return_value=[
                    {
                        'status': 'completed',
                        'yt_results': list(yt_results.keys()),
                        'modified_timestamp': modified_timestamp,
                    },
                ],
            ),
        ],
    )

    if yt_results:
        request_logs_setup.yt_mock.expect_configure(
            mock.Expectation(('hahn.yt.yandex.net', 'FAKE_YT_TOKEN')),
        )
        request_logs_setup.yt_mock.expect_read_table(
            [
                mock.Expectation(
                    (yt_path, yt.YsonFormat(encoding=None)),
                    return_value=iter(yt_rows),
                )
                for yt_path, yt_rows in yt_results.items()
            ],
        )

    response = await web_app_client.post('/request_logs/', params=params)
    assert response.status == 200
    content = await response.json()
    assert content == expected_content
    assert request_logs_setup.saturated()


@pytest.mark.config(
    DISPATCH_LOGS_ADMIN={
        'yt_cluster': 'hahn',
        'chyt_clique_id': '*ch_public',
        'yt_destination': {'path_prefix': '//home', 'path': 'path'},
        'log_sources': {
            'dispatch_buffer': {'path': '//home/path', 'tz_offset': '+0300'},
        },
    },
)
@pytest.mark.parametrize(
    """
        params,
        yt_orders_rows,
        yt_draw_rows,
        expected_fetch_query,
        expected_content
    """,
    [
        (
            {
                'log_type': 'dispatch_buffer',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'order_id': 'order_id_0',
            },
            [
                {
                    'order_id': 'order_id_0',
                    'draw_id': 'draw_id_0',
                    'order_meta': 'order_meta_0',
                },
                {
                    'order_id': 'order_id_0',
                    'draw_id': 'draw_id_1',
                    'order_meta': 'order_meta_0',
                },
            ],
            [
                {'draw_id': 'draw_id_0', 'draw_meta': 'draw_meta_0'},
                {'draw_id': 'draw_id_1', 'draw_meta': 'draw_meta_1'},
            ],
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id = 'order_id_0')
                    AND (draw_id IS NULL);
            """,
            {
                'log_type': 'dispatch_buffer',
                'dispatch_buffer_logs': [
                    {
                        'order_log': {
                            'order_id': 'order_id_0',
                            'draw_id': 'draw_id_0',
                            'order_meta': 'order_meta_0',
                        },
                        'draw_log': {
                            'draw_id': 'draw_id_0',
                            'draw_meta': 'draw_meta_0',
                        },
                    },
                    {
                        'order_log': {
                            'order_id': 'order_id_0',
                            'draw_id': 'draw_id_1',
                            'order_meta': 'order_meta_0',
                        },
                        'draw_log': {
                            'draw_id': 'draw_id_1',
                            'draw_meta': 'draw_meta_1',
                        },
                    },
                ],
            },
        ),
        (
            {
                'log_type': 'dispatch_buffer',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'draw_id': 'draw_id_0',
            },
            [
                {
                    'order_id': 'order_id_0',
                    'draw_id': 'draw_id_0',
                    'order_meta': 'order_meta_0',
                },
                {
                    'order_id': 'order_id_1',
                    'draw_id': 'draw_id_0',
                    'order_meta': 'order_meta_1',
                },
            ],
            [{'draw_id': 'draw_id_0', 'draw_meta': 'draw_meta_0'}],
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id IS NULL)
                    AND (draw_id = 'draw_id_0');
            """,
            {
                'log_type': 'dispatch_buffer',
                'dispatch_buffer_logs': [
                    {
                        'order_log': {
                            'order_id': 'order_id_0',
                            'draw_id': 'draw_id_0',
                            'order_meta': 'order_meta_0',
                        },
                        'draw_log': {
                            'draw_id': 'draw_id_0',
                            'draw_meta': 'draw_meta_0',
                        },
                    },
                    {
                        'order_log': {
                            'order_id': 'order_id_1',
                            'draw_id': 'draw_id_0',
                            'order_meta': 'order_meta_1',
                        },
                        'draw_log': {
                            'draw_id': 'draw_id_0',
                            'draw_meta': 'draw_meta_0',
                        },
                    },
                ],
            },
        ),
        (
            {
                'log_type': 'dispatch_buffer',
                'from_dt': '2019-01-01T12:00:00+03:00',
                'to_dt': '2019-01-01T12:30:00+03:00',
                'draw_id': 'draw_id_0',
                'offset': 1,
                'limit': 2,
            },
            [
                {
                    'order_id': 'order_id_0',
                    'draw_id': 'draw_id_0',
                    'order_meta': 'order_meta_0',
                },
                {
                    'order_id': 'order_id_1',
                    'draw_id': 'draw_id_0',
                    'order_meta': 'order_meta_1',
                },
                {
                    'order_id': 'order_id_2',
                    'draw_id': 'draw_id_0',
                    'order_meta': 'order_meta_2',
                },
                {
                    'order_id': 'order_id_3',
                    'draw_id': 'draw_id_0',
                    'order_meta': 'order_meta_3',
                },
            ],
            None,
            """
                SELECT status, yt_results, modified_timestamp
                FROM common.yt_tasks
                WHERE version = $1
                    AND log_type = $2
                    AND from_timestamp = $3
                    AND to_timestamp = $4
                    AND (order_id IS NULL)
                    AND (draw_id = 'draw_id_0');
            """,
            {
                'log_type': 'dispatch_buffer',
                'dispatch_buffer_logs': [
                    {
                        'order_log': {
                            'order_id': 'order_id_1',
                            'draw_id': 'draw_id_0',
                            'order_meta': 'order_meta_1',
                        },
                    },
                    {
                        'order_log': {
                            'order_id': 'order_id_2',
                            'draw_id': 'draw_id_0',
                            'order_meta': 'order_meta_2',
                        },
                    },
                ],
            },
        ),
    ],
)
async def test_dispatch_buffer_logs_fetching(
        web_app_client,
        request_logs_setup,
        params,
        yt_orders_rows,
        yt_draw_rows,
        expected_fetch_query,
        expected_content,
):
    yt_results = {}
    if yt_orders_rows is not None:
        yt_results['//0123_dispatch_buffer_orders'] = yt_orders_rows
    if yt_draw_rows is not None:
        yt_results['//0123_dispatch_buffer_draw'] = yt_draw_rows

    modified_timestamp = datetime.datetime.utcnow()
    request_logs_setup.pg_mock.expect(
        [
            mock.Expectation(
                mock.PgCallParams(
                    'fetch',
                    expected_fetch_query,
                    version.VERSION,
                    params['log_type'],
                    helpers.to_naive_utc_datetime(params['from_dt']),
                    helpers.to_naive_utc_datetime(params['to_dt']),
                ),
                return_value=[
                    {
                        'status': 'completed',
                        'yt_results': list(yt_results.keys()),
                        'modified_timestamp': modified_timestamp,
                    },
                ],
            ),
        ],
    )

    if yt_results:
        request_logs_setup.yt_mock.expect_configure(
            mock.Expectation(('hahn.yt.yandex.net', 'FAKE_YT_TOKEN')),
        )
        request_logs_setup.yt_mock.expect_read_table(
            [
                mock.Expectation(
                    (yt_path, yt.YsonFormat(encoding=None)),
                    return_value=iter(yt_rows),
                )
                for yt_path, yt_rows in yt_results.items()
            ],
        )

    response = await web_app_client.post('/request_logs/', params=params)
    assert response.status == 200
    content = await response.json()
    assert content == expected_content
    assert request_logs_setup.saturated()
