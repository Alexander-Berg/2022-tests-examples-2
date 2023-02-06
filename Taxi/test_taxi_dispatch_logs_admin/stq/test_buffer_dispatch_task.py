# pylint: disable=redefined-outer-name

import pytest
import requests
import yt.wrapper as yt

from taxi_dispatch_logs_admin.common import helpers
from taxi_dispatch_logs_admin.generated.stq3 import stq_settings
from taxi_dispatch_logs_admin.stq import base_task
from taxi_dispatch_logs_admin.stq import helpers as stq_helpers
from taxi_dispatch_logs_admin.stq.chyt_tasks import chyt_base
from taxi_dispatch_logs_admin.stq.chyt_tasks import task_creator
from test_taxi_dispatch_logs_admin.common import common as test_common
from test_taxi_dispatch_logs_admin.common import mock
from test_taxi_dispatch_logs_admin.stq import setup


EMPTY_MAP_NODE = {'type': 'map_node', '/': {}}

TABLE_MAP_NODE = {'type': 'map_node', '/': {'2019-01-01': {'type': 'table'}}}

STREAM_MAP_NODE = {
    'type': 'map_node',
    '/': {'stream': {'type': 'map_node', '/': {'1d': TABLE_MAP_NODE}}},
}


class BufferDispatchTaskSetup(setup.TaskSetupBase):
    def __init__(self):
        super().__init__(
            stq_settings.STQ_DISPATCH_LOGS_ADMIN_CHYT_IMPORTS_QUEUE, 'chyt',
        )
        self.post_mock = mock.PostMock()

    def saturated(self):
        return (
            super().saturated()
            and self.post_mock.saturated()
            and self.yt_mock.saturated()
        )


@pytest.fixture
def buffer_dispatch_task_setup(simple_secdist, monkeypatch):
    task_setup = BufferDispatchTaskSetup()
    monkeypatch.setattr(
        stq_helpers,
        'yt_list_with_types',
        task_setup.yt_mock.yt_list_with_types,
    )
    monkeypatch.setattr(
        stq_helpers, 'yt_node_exists', task_setup.yt_mock.yt_node_exists,
    )
    monkeypatch.setattr(chyt_base, 'post', task_setup.post_mock.post)
    monkeypatch.setattr(
        helpers, 'yt_configure', task_setup.yt_mock.yt_configure,
    )
    monkeypatch.setattr(yt, 'read_table', task_setup.yt_mock.yt_read_table)
    monkeypatch.setattr(yt, 'remove', task_setup.yt_mock.yt_remove)
    monkeypatch.setattr(helpers, 'pg_perform', task_setup.pg_mock.pg_perform)
    monkeypatch.setattr(
        stq_helpers,
        'remove_duplicates',
        test_common.remove_duplicates_ordered,
    )
    monkeypatch.setattr(
        base_task.BaseTask, 'expiration_time', task_setup.expiration_time,
    )
    monkeypatch.setattr(yt, 'get', task_setup.yt_mock.yt_get_table)
    return task_setup


@pytest.mark.parametrize(
    """
        task_params,
        non_default_cypress_tree,
        draw_ids,
        expected_yt_schema_tables,
        yt_get_result,
        expected_yt_results,
        expected_queries
    """,
    [
        (
            {
                'log_type': 'buffer_dispatch',
                'task_id': '0123',
                'from_dt': '2019-01-01T23:00:00Z',
                'to_dt': '2019-01-02T01:00:00Z',
                'order_id': 'order_id_0',
                'draw_id': None,
                'extra_filters': {'driver_id': '999'},
            },
            None,
            ['draw_id_0', 'draw_id_1', 'draw_id_2', 'draw_id_0'],
            [
                '//home/unittests/buffer_dispatch/orders/2019-01-01',
                '//home/unittests/buffer_dispatch/orders/2019-01-02',
                '//home/unittests/buffer_dispatch/draw/2019-01-01',
                '//home/unittests/buffer_dispatch/draw/2019-01-02',
                '//home/unittests/buffer_dispatch/candidates/2019-01-01',
                '//home/unittests/buffer_dispatch/candidates/2019-01-02',
            ],
            """
            {
                "$attributes": {"unique_keys": false, "strict": true},
                "$value": [
                   {
                        "name": "field0",
                        "type_v3": "string",
                        "type_v2": "string",
                        "required": true,
                        "type": "string"
                    },
                    {
                        "name": "field1",
                        "type_v3": "double",
                        "type_v2": "double",
                        "required": true,
                        "type": "double"
                    }
                ]
            }
            """,
            [
                '//dispatch-logs-admin/0123_buffer_dispatch_orders',
                '//dispatch-logs-admin/0123_buffer_dispatch_draw',
                '//dispatch-logs-admin/0123_buffer_dispatch_candidates',
            ],
            [
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_orders"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                        `//home/unittests/buffer_dispatch/orders/2019-01-01`,
                        `//home/unittests/buffer_dispatch/orders/2019-01-02`)
                    WHERE `timestamp` BETWEEN 1546383600 AND 1546390800
                        AND (`order_id` = 'order_id_0')
                        AND (`dbid` = '999' OR `clid` = '999')
                    ORDER BY `timestamp` DESC;
                """,
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_draw"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                        `//home/unittests/buffer_dispatch/draw/2019-01-01`,
                        `//home/unittests/buffer_dispatch/draw/2019-01-02`)
                    WHERE `timestamp` BETWEEN 1546383600 AND 1546390800
                        AND `draw_id` IN ('draw_id_0','draw_id_1','draw_id_2')
                    ORDER BY `timestamp` DESC;
                """,
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_candidates"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                    `//home/unittests/buffer_dispatch/candidates/2019-01-01`,
                    `//home/unittests/buffer_dispatch/candidates/2019-01-02`)
                    WHERE `timestamp` BETWEEN 1546383600 AND 1546390800
                        AND `draw_id` IN ('draw_id_0','draw_id_1','draw_id_2')
                    ORDER BY `timestamp` DESC;
                """,
            ],
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'task_id': '0123',
                'from_dt': '2019-01-01T10:00:00Z',
                'to_dt': '2019-01-01T10:30:00Z',
                'order_id': 'order_id_0',
                'draw_id': 'draw_id_0',
                'extra_filters': {},
            },
            None,
            ['draw_id_0'],
            [
                '//home/unittests/buffer_dispatch/orders/2019-01-01',
                '//home/unittests/buffer_dispatch/draw/2019-01-01',
                '//home/unittests/buffer_dispatch/candidates/2019-01-01',
            ],
            """
            {
                "$attributes": {"unique_keys": false, "strict": true},
                "$value": [
                   {
                        "name": "field0",
                        "type_v3": "string",
                        "type_v2": "string",
                        "required": true,
                        "type": "string"
                    },
                    {
                        "name": "field1",
                        "type_v3": "double",
                        "type_v2": "double",
                        "required": true,
                        "type": "double"
                    }
                ]
            }
            """,
            [
                '//dispatch-logs-admin/0123_buffer_dispatch_orders',
                '//dispatch-logs-admin/0123_buffer_dispatch_draw',
                '//dispatch-logs-admin/0123_buffer_dispatch_candidates',
            ],
            [
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_orders"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                        `//home/unittests/buffer_dispatch/orders/2019-01-01`)
                    WHERE `timestamp` BETWEEN 1546336800 AND 1546338600
                        AND (`order_id` = 'order_id_0')
                        AND (`draw_id` = 'draw_id_0')
                    ORDER BY `timestamp` DESC;
                """,
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_draw"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                        `//home/unittests/buffer_dispatch/draw/2019-01-01`)
                    WHERE `timestamp` BETWEEN 1546336800 AND 1546338600
                        AND `draw_id` IN ('draw_id_0')
                    ORDER BY `timestamp` DESC;
                """,
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_candidates"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                    `//home/unittests/buffer_dispatch/candidates/2019-01-01`)
                    WHERE `timestamp` BETWEEN 1546336800 AND 1546338600
                        AND `draw_id` IN ('draw_id_0')
                    ORDER BY `timestamp` DESC;
                """,
            ],
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'task_id': '0123',
                'from_dt': '2019-01-01T10:00:00Z',
                'to_dt': '2019-01-01T10:30:00Z',
                'order_id': 'nonexist',
                'draw_id': None,
                'extra_filters': {},
            },
            None,
            [],
            [
                '//home/unittests/buffer_dispatch/orders/2019-01-01',
                '//home/unittests/buffer_dispatch/draw/2019-01-01',
                '//home/unittests/buffer_dispatch/candidates/2019-01-01',
            ],
            """
            {
                "$attributes": {"unique_keys": false, "strict": true},
                "$value": [
                   {
                        "name": "field0",
                        "type_v3": "string",
                        "type_v2": "string",
                        "required": true,
                        "type": "string"
                    },
                    {
                        "name": "field1",
                        "type_v3": "double",
                        "type_v2": "double",
                        "required": true,
                        "type": "double"
                    }
                ]
            }
            """,
            [
                '//dispatch-logs-admin/0123_buffer_dispatch_orders',
                '//dispatch-logs-admin/0123_buffer_dispatch_draw',
                '//dispatch-logs-admin/0123_buffer_dispatch_candidates',
            ],
            [
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_orders"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                        `//home/unittests/buffer_dispatch/orders/2019-01-01`)
                    WHERE `timestamp` BETWEEN 1546336800 AND 1546338600
                        AND (`order_id` = 'nonexist')
                    ORDER BY `timestamp` DESC;
                """,
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_draw"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                        `//home/unittests/buffer_dispatch/draw/2019-01-01`)
                    WHERE `timestamp` BETWEEN 1546336800 AND 1546338600
                        AND 0 = 1
                    ORDER BY `timestamp` DESC;
                """,
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_candidates"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                    `//home/unittests/buffer_dispatch/candidates/2019-01-01`)
                    WHERE `timestamp` BETWEEN 1546336800 AND 1546338600
                        AND 0 = 1
                    ORDER BY `timestamp` DESC;
                """,
            ],
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'task_id': '0123',
                'from_dt': '2019-01-01T01:00:00Z',
                'to_dt': '2019-01-01T02:00:00Z',
                'order_id': 'order_id_0',
                'draw_id': None,
                'extra_filters': {},
            },
            {
                '/': {
                    'type': 'map_node',
                    '/': {
                        'home': {
                            'type': 'map_node',
                            '/': {
                                'unittests': {
                                    'type': 'map_node',
                                    '/': {
                                        'buffer_dispatch': {
                                            'type': 'map_node',
                                            '/': {
                                                'orders': EMPTY_MAP_NODE,
                                                'draw': EMPTY_MAP_NODE,
                                                'candidates': EMPTY_MAP_NODE,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            [],
            [],
            {},
            [],
            [],
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'task_id': '0123',
                'from_dt': '2019-01-01T01:00:00Z',
                'to_dt': '2019-01-01T02:00:00Z',
                'order_id': 'order_id_0',
                'draw_id': None,
                'extra_filters': {},
            },
            {
                '/': {
                    'type': 'map_node',
                    '/': {
                        'home': {
                            'type': 'map_node',
                            '/': {
                                'unittests': {
                                    'type': 'map_node',
                                    '/': {
                                        'buffer_dispatch': {
                                            'type': 'map_node',
                                            '/': {
                                                'orders': TABLE_MAP_NODE,
                                                'draw': EMPTY_MAP_NODE,
                                                'candidates': EMPTY_MAP_NODE,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            ['draw_id_0'],
            ['//home/unittests/buffer_dispatch/orders/2019-01-01'],
            """
            {
                "$attributes": {"unique_keys": false, "strict": true},
                "$value": [
                   {
                        "name": "field0",
                        "type_v3": "string",
                        "type_v2": "string",
                        "required": true,
                        "type": "string"
                    },
                    {
                        "name": "field1",
                        "type_v3": "double",
                        "type_v2": "double",
                        "required": true,
                        "type": "double"
                    }
                ]
            }
            """,
            ['//dispatch-logs-admin/0123_buffer_dispatch_orders'],
            [
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_orders"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                        `//home/unittests/buffer_dispatch/orders/2019-01-01`)
                    WHERE `timestamp` BETWEEN 1546304400 AND 1546308000
                        AND (`order_id` = 'order_id_0')
                    ORDER BY `timestamp` DESC;
                """,
            ],
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'task_id': '0123',
                'from_dt': '2019-01-01T01:00:00Z',
                'to_dt': '2019-01-01T02:00:00Z',
                'order_id': None,
                'draw_id': 'draw_id_0',
                'extra_filters': {},
            },
            {
                '/': {
                    'type': 'map_node',
                    '/': {
                        'home': {
                            'type': 'map_node',
                            '/': {
                                'unittests': {
                                    'type': 'map_node',
                                    '/': {
                                        'buffer_dispatch': {
                                            'type': 'map_node',
                                            '/': {
                                                'orders': EMPTY_MAP_NODE,
                                                'draw': TABLE_MAP_NODE,
                                                'candidates': EMPTY_MAP_NODE,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            [],
            ['//home/unittests/buffer_dispatch/draw/2019-01-01'],
            """
            {
                "$attributes": {"unique_keys": false, "strict": true},
                "$value": [
                   {
                        "name": "field0",
                        "type_v3": "string",
                        "type_v2": "string",
                        "required": true,
                        "type": "string"
                    },
                    {
                        "name": "field1",
                        "type_v3": "double",
                        "type_v2": "double",
                        "required": true,
                        "type": "double"
                    }
                ]
            }
            """,
            ['//dispatch-logs-admin/0123_buffer_dispatch_draw'],
            [
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_draw"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                        `//home/unittests/buffer_dispatch/draw/2019-01-01`)
                    WHERE `timestamp` BETWEEN 1546304400 AND 1546308000
                        AND `draw_id` IN ('draw_id_0')
                    ORDER BY `timestamp` DESC;
                """,
            ],
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'task_id': '0123',
                'from_dt': '2019-01-01T01:00:00Z',
                'to_dt': '2019-01-01T02:00:00Z',
                'order_id': None,
                'draw_id': 'draw_id_0',
                'extra_filters': {},
            },
            {
                '/': {
                    'type': 'map_node',
                    '/': {
                        'home': {
                            'type': 'map_node',
                            '/': {
                                'unittests': {
                                    'type': 'map_node',
                                    '/': {
                                        'buffer_dispatch': {
                                            'type': 'map_node',
                                            '/': {
                                                'orders': EMPTY_MAP_NODE,
                                                'draw': EMPTY_MAP_NODE,
                                                'candidates': TABLE_MAP_NODE,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            [],
            ['//home/unittests/buffer_dispatch/candidates/2019-01-01'],
            """
            {
                "$attributes": {"unique_keys": false, "strict": true},
                "$value": [
                   {
                        "name": "field0",
                        "type_v3": "string",
                        "type_v2": "string",
                        "required": true,
                        "type": "string"
                    },
                    {
                        "name": "field1",
                        "type_v3": "double",
                        "type_v2": "double",
                        "required": true,
                        "type": "double"
                    }
                ]
            }
            """,
            ['//dispatch-logs-admin/0123_buffer_dispatch_candidates'],
            [
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_candidates"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                    `//home/unittests/buffer_dispatch/candidates/2019-01-01`)
                    WHERE `timestamp` BETWEEN 1546304400 AND 1546308000
                        AND `draw_id` IN ('draw_id_0')
                    ORDER BY `timestamp` DESC;
                """,
            ],
        ),
        (
            {
                'log_type': 'buffer_dispatch',
                'task_id': '0123',
                'from_dt': '2019-01-01T01:00:00Z',
                'to_dt': '2019-01-01T02:00:00Z',
                'order_id': None,
                'draw_id': 'draw_id_0',
                'extra_filters': {},
            },
            {
                '/': {
                    'type': 'map_node',
                    '/': {
                        'home': {
                            'type': 'map_node',
                            '/': {
                                'unittests': {
                                    'type': 'map_node',
                                    '/': {
                                        'buffer_dispatch': {
                                            'type': 'map_node',
                                            '/': {
                                                'orders': EMPTY_MAP_NODE,
                                                'draw': STREAM_MAP_NODE,
                                                'candidates': EMPTY_MAP_NODE,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            [],
            ['//home/unittests/buffer_dispatch/draw/stream/1d/2019-01-01'],
            """
            {
                "$attributes": {"unique_keys": false, "strict": true},
                "$value": [
                   {
                        "name": "field0",
                        "type_v3": "string",
                        "type_v2": "string",
                        "required": true,
                        "type": "string"
                    },
                    {
                        "name": "field1",
                        "type_v3": "double",
                        "type_v2": "double",
                        "required": true,
                        "type": "double"
                    }
                ]
            }
            """,
            ['//dispatch-logs-admin/0123_buffer_dispatch_draw'],
            [
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_draw"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                    `//home/unittests/buffer_dispatch/draw/stream/1d/2019-01-01`)
                    WHERE `timestamp` BETWEEN 1546304400 AND 1546308000
                        AND `draw_id` IN ('draw_id_0')
                    ORDER BY `timestamp` DESC;
                """,
            ],
        ),
    ],
)
async def test_buffer_dispatch_task(
        buffer_dispatch_task_setup,
        task_params,
        non_default_cypress_tree,
        draw_ids,
        expected_yt_results,
        expected_queries,
        yt_get_result,
        expected_yt_schema_tables,
):
    if non_default_cypress_tree is not None:
        buffer_dispatch_task_setup.yt_mock.set_cypress_tree(
            non_default_cypress_tree,
        )

    buffer_dispatch_task_setup.expect_successful_pg_update(
        task_params['task_id'], expected_yt_results,
    )

    buffer_dispatch_task_setup.yt_mock.expect_get_table(
        [
            mock.Expectation(
                (yt_schema_table + '/@schema', yt.JsonFormat()),
                return_value=yt_get_result,
            )
            for yt_schema_table in expected_yt_schema_tables
        ],
    )

    ok_response = requests.Response()
    ok_response.status_code = 200
    buffer_dispatch_task_setup.post_mock.expect(
        [
            mock.Expectation(
                mock.PostCallParams(
                    'http://hahn.yt.yandex.net/query?database=*ch_public',
                    headers={'Authorization': 'OAuth FAKE_YT_TOKEN'},
                    data=expected_query,
                ),
                return_value=ok_response,
            )
            for expected_query in expected_queries
        ],
    )
    buffer_dispatch_task_setup.yt_mock.expect_configure(
        mock.Expectation(('hahn.yt.yandex.net', 'FAKE_YT_TOKEN')),
    )
    buffer_dispatch_task_setup.yt_mock.expect_remove(
        [
            mock.Expectation((table_path, True))
            for table_path in expected_yt_results
        ],
    )
    orders_table_path = (
        f"""//dispatch-logs-admin/{task_params['task_id']}_"""
        f"""{task_params['log_type']}_orders"""
    )
    if orders_table_path in expected_yt_results:
        buffer_dispatch_task_setup.yt_mock.expect_read_table(
            [
                mock.Expectation(
                    (
                        yt.TablePath(orders_table_path, columns=['draw_id']),
                        None,
                    ),
                    return_value=[{'draw_id': id} for id in draw_ids],
                ),
            ],
        )
    await task_creator.task(
        buffer_dispatch_task_setup.context, task_params, {},
    )
    assert buffer_dispatch_task_setup.saturated()


@pytest.mark.parametrize(
    """
        task_params,
        non_default_cypress_tree,
        draw_ids,
        yt_get_result,
        expected_yt_results,
        expected_queries
    """,
    [
        (
            {
                'log_type': 'buffer_dispatch',
                'task_id': '0123',
                'from_dt': '2019-01-01T01:00:00Z',
                'to_dt': '2019-01-01T02:00:00Z',
                'order_id': None,
                'draw_id': 'draw_id_0',
                'extra_filters': {},
            },
            {
                '/': {
                    'type': 'map_node',
                    '/': {
                        'home': {
                            'type': 'map_node',
                            '/': {
                                'unittests': {
                                    'type': 'map_node',
                                    '/': {
                                        'buffer_dispatch': {
                                            'type': 'map_node',
                                            '/': {
                                                'orders': EMPTY_MAP_NODE,
                                                'draw': STREAM_MAP_NODE,
                                                'candidates': EMPTY_MAP_NODE,
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            [],
            """
            {
                "$attributes": {"unique_keys": false, "strict": true},
                "$value": [
                   {
                        "name": "field0",
                        "type_v3": "string",
                        "type_v2": "string",
                        "required": true,
                        "type": "string"
                    },
                    {
                        "name": "field1",
                        "type_v3": "double",
                        "type_v2": "double",
                        "required": true,
                        "type": "double"
                    }
                ]
            }
            """,
            ['//dispatch-logs-admin/0123_buffer_dispatch_draw'],
            [
                """
                    CREATE TABLE
                        "//dispatch-logs-admin/0123_buffer_dispatch_draw"
                    ENGINE =
                    YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                    SELECT `field0`, `field1`
                    FROM concatYtTables(
                    `//home/unittests/buffer_dispatch/draw/stream/1d/2019-01-01`)
                    WHERE `timestamp` BETWEEN 1546304400 AND 1546308000
                        AND `draw_id` IN ('draw_id_0')
                    ORDER BY `timestamp` DESC;
                """,
            ],
        ),
    ],
)
@pytest.mark.now('2019-01-01T02:00:00')
async def test_buffer_dispatch_outdated_task(
        buffer_dispatch_task_setup,
        task_params,
        non_default_cypress_tree,
        draw_ids,
        expected_yt_results,
        expected_queries,
        yt_get_result,
):
    buffer_dispatch_task_setup.yt_mock.set_cypress_tree(
        non_default_cypress_tree,
    )

    buffer_dispatch_task_setup.expect_successful_pg_update(
        task_params['task_id'], expected_yt_results, True,
    )

    buffer_dispatch_task_setup.yt_mock.expect_get_table(
        [
            mock.Expectation(
                (
                    '//home/unittests/buffer_dispatch/draw/stream/'
                    '1d/2019-01-01/@schema',
                    yt.JsonFormat(),
                ),
                return_value=yt_get_result,
            ),
        ],
    )

    ok_response = requests.Response()
    ok_response.status_code = 200

    buffer_dispatch_task_setup.post_mock.expect(
        [
            mock.Expectation(
                mock.PostCallParams(
                    'http://hahn.yt.yandex.net/query?database=*ch_public',
                    headers={'Authorization': 'OAuth FAKE_YT_TOKEN'},
                    data=expected_query,
                ),
                return_value=ok_response,
            )
            for expected_query in expected_queries
        ],
    )
    buffer_dispatch_task_setup.yt_mock.expect_configure(
        mock.Expectation(('hahn.yt.yandex.net', 'FAKE_YT_TOKEN')),
    )
    buffer_dispatch_task_setup.yt_mock.expect_remove(
        [
            mock.Expectation((table_path, True))
            for table_path in expected_yt_results
        ],
    )
    orders_table_path = (
        f"""//dispatch-logs-admin/{task_params['task_id']}_"""
        f"""{task_params['log_type']}_orders"""
    )
    if orders_table_path in expected_yt_results:
        buffer_dispatch_task_setup.yt_mock.expect_read_table(
            [
                mock.Expectation(
                    (
                        yt.TablePath(orders_table_path, columns=['draw_id']),
                        None,
                    ),
                    return_value=[{'draw_id': id} for id in draw_ids],
                ),
            ],
        )
    await task_creator.task(
        buffer_dispatch_task_setup.context, task_params, {},
    )
    assert buffer_dispatch_task_setup.saturated()
