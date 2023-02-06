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
from test_taxi_dispatch_logs_admin.common import mock
from test_taxi_dispatch_logs_admin.stq import setup


class FlatLogsChytTaskSetup(setup.TaskSetupBase):
    def __init__(self, interface):
        super().__init__(
            stq_settings.STQ_DISPATCH_LOGS_ADMIN_CHYT_IMPORTS_QUEUE, interface,
        )
        self.post_mock = mock.PostMock()

    def saturated(self):
        return super().saturated() and self.post_mock.saturated()


@pytest.fixture
def flat_logs_chyt_task_setup(simple_secdist, monkeypatch):
    task_setup = FlatLogsChytTaskSetup('chyt')
    monkeypatch.setattr(
        helpers, 'yt_configure', task_setup.yt_mock.yt_configure,
    )
    monkeypatch.setattr(
        stq_helpers,
        'yt_list_with_types',
        task_setup.yt_mock.yt_list_with_types,
    )
    monkeypatch.setattr(
        stq_helpers, 'yt_node_exists', task_setup.yt_mock.yt_node_exists,
    )
    monkeypatch.setattr(chyt_base, 'post', task_setup.post_mock.post)
    monkeypatch.setattr(yt, 'remove', task_setup.yt_mock.yt_remove)
    monkeypatch.setattr(helpers, 'pg_perform', task_setup.pg_mock.pg_perform)
    monkeypatch.setattr(
        base_task.BaseTask, 'expiration_time', task_setup.expiration_time,
    )
    monkeypatch.setattr(yt, 'get', task_setup.yt_mock.yt_get_table)
    return task_setup


@pytest.mark.parametrize(
    """
        task_params,
        expected_yt_schema_tables,
        yt_get_results,
        expected_yt_result,
        expected_chyt_query
    """,
    [
        (
            {
                'log_type': 'driver_dispatcher',
                'task_id': '0123',
                'from_dt': '2019-01-01T20:00:00Z',
                'to_dt': '2019-01-01T23:00:00Z',
                'extra_filters': {'driver_id': '888'},
            },
            [
                '//driver-dispatcher/2019-01-01',
                '//driver-dispatcher/2019-01-02',
            ],
            [
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
                            "type_v3": {
                                "type_name": "optional",
                                "item": "yson"
                            },
                            "type_v2": {
                                "element": "any",
                                "metatype": "optional"
                            },
                            "required": false,
                            "type": "any"
                        },
                        {
                            "name": "field2",
                            "type_v3": "double",
                            "type_v2": "double",
                            "required": true,
                            "type": "double"
                        },
                        {
                            "name": "field3",
                            "type_v3": {
                                "type_name": "optional",
                                "item": "yson"
                            },
                            "type_v2": {
                                "element": "any",
                                "metatype": "optional"
                            },
                            "required": false,
                            "type": "any"
                        }
                    ]
                }
                """,
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
                            "type_v3": {
                                "type_name": "optional",
                                "item": "yson"
                            },
                            "type_v2": {
                                "element": "any",
                                "metatype": "optional"
                            },
                            "required": false,
                            "type": "any"
                        },
                        {
                            "name": "field2",
                            "type_v3": "double",
                            "type_v2": "double",
                            "required": true,
                            "type": "double"
                        },
                        {
                            "name": "field3",
                            "type_v3": "string",
                            "type_v2": {
                                "element": "any",
                                "metatype": "optional"
                            },
                            "required": false,
                            "type": "any"
                        },
                        {
                            "name": "field4",
                            "type_v3": "string",
                            "type_v2": {
                                "element": "any",
                                "metatype": "optional"
                            },
                            "required": false,
                            "type": "any"
                        }
                    ]
                }
                """,
            ],
            '//dispatch-logs-admin/0123_chyt_driver_dispatcher',
            """
                CREATE TABLE
                "//dispatch-logs-admin/0123_chyt_driver_dispatcher"
                ENGINE =
                YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                SELECT `field0`, ConvertYson(`field1`, 'pretty')
                    AS `field1`, `field2`
                FROM concatYtTables(
                    `//driver-dispatcher/2019-01-01`,
                    `//driver-dispatcher/2019-01-02`)
                WHERE `timestamp` BETWEEN
                    '2019-01-01T23:00:00' AND '2019-01-02T02:00:00'
                    AND (`dbid` = '888' OR `dbid_uuid` = '888')
                ORDER BY `timestamp` DESC;
            """,
        ),
        (
            {
                'log_type': 'driver_dispatcher',
                'task_id': '0123',
                'from_dt': '2019-01-01T20:00:00Z',
                'to_dt': '2019-01-01T23:00:00Z',
                'order_id': 'order_id_0',
                'draw_id': None,
                'extra_filters': {'driver_id': '888'},
            },
            [
                '//driver-dispatcher/2019-01-01',
                '//driver-dispatcher/2019-01-02',
            ],
            [
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
                            "type_v3": {
                                "type_name": "optional",
                                "item": "yson"
                            },
                            "type_v2": {
                                "element": "any",
                                "metatype": "optional"
                            },
                            "required": false,
                            "type": "any"
                        },
                        {
                            "name": "field2",
                            "type_v3": "double",
                            "type_v2": "double",
                            "required": true,
                            "type": "double"
                        }
                    ]
                }
                """,
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
                                "type_v3": {
                                    "type_name": "optional",
                                    "item": "yson"
                                },
                                "type_v2": {
                                    "element": "any",
                                    "metatype": "optional"
                                },
                                "required": false,
                                "type": "any"
                            },
                            {
                                "name": "field2",
                                "type_v3": "double",
                                "type_v2": "double",
                                "required": true,
                                "type": "double"
                            }
                        ]
                    }
                    """,
            ],
            '//dispatch-logs-admin/0123_chyt_driver_dispatcher',
            """
                CREATE TABLE
                "//dispatch-logs-admin/0123_chyt_driver_dispatcher"
                ENGINE =
                YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                SELECT `field0`, ConvertYson(`field1`, 'pretty')
                    AS `field1`, `field2`
                FROM concatYtTables(
                    `//driver-dispatcher/2019-01-01`,
                    `//driver-dispatcher/2019-01-02`)
                WHERE `timestamp` BETWEEN '2019-01-01T23:00:00' AND
                    '2019-01-02T02:00:00' AND (`order_id` = 'order_id_0' OR
                    `meta_order_id` = 'order_id_0') AND
                    (`dbid` = '888' OR `dbid_uuid` = '888')
                ORDER BY `timestamp` DESC;
            """,
        ),
        (
            {
                'log_type': 'tracks',
                'task_id': '0123',
                'from_dt': '2019-01-03T10:00:00Z',
                'to_dt': '2019-01-03T10:30:00Z',
                'order_id': 'order_id_0',
                'draw_id': 'draw_id_0',
                'extra_filters': {},
            },
            ['//tracks/2019-01-03'],
            [
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
                            "type_v3": {
                                "type_name": "optional",
                                "item": "yson"
                            },
                            "type_v2": {
                                "element": "any",
                                "metatype": "optional"
                            },
                            "required": false,
                            "type": "any"
                        },
                        {
                            "name": "field2",
                            "type_v3": "double",
                            "type_v2": "double",
                            "required": true,
                            "type": "double"
                        }
                    ]
                }
                """,
            ],
            '//dispatch-logs-admin/0123_chyt_tracks',
            """
                CREATE TABLE "//dispatch-logs-admin/0123_chyt_tracks"
                ENGINE =
                YtTable('{expiration_time="2019-12-25T12:58:08+00:00"}') AS
                SELECT `field0`, ConvertYson(`field1`, 'pretty')
                    AS `field1`, `field2`
                FROM concatYtTables(
                    `//tracks/2019-01-03`)
                WHERE `timestamp_changed` BETWEEN '2019-01-03 13:00:00'
                AND '2019-01-03 13:30:00'
                AND (`order_id` = 'order_id_0' OR
                `meta_order_id` = 'order_id_0')
                AND (`draw_id` = 'draw_id_0' OR `link` = 'draw_id_0')
                ORDER BY `timestamp_changed` DESC;

            """,
        ),
    ],
)
async def test_flat_logs_chyt_task(
        flat_logs_chyt_task_setup,
        task_params,
        expected_yt_schema_tables,
        yt_get_results,
        expected_yt_result,
        expected_chyt_query,
):
    flat_logs_chyt_task_setup.yt_mock.expect_configure(
        mock.Expectation(('hahn.yt.yandex.net', 'FAKE_YT_TOKEN')),
    )

    flat_logs_chyt_task_setup.expect_successful_pg_update(
        task_params['task_id'], [expected_yt_result],
    )
    flat_logs_chyt_task_setup.yt_mock.expect_remove(
        [mock.Expectation((expected_yt_result, True))],
    )

    flat_logs_chyt_task_setup.yt_mock.expect_get_table(
        [
            mock.Expectation(
                (expected_yt_schema_tables[i] + '/@schema', yt.JsonFormat()),
                return_value=yt_get_results[i],
            )
            for i in range(len(expected_yt_schema_tables))
        ],
    )

    ok_response = requests.Response()
    ok_response.status_code = 200
    flat_logs_chyt_task_setup.post_mock.expect(
        [
            mock.Expectation(
                mock.PostCallParams(
                    'http://hahn.yt.yandex.net/query?database=*ch_public',
                    headers={'Authorization': 'OAuth FAKE_YT_TOKEN'},
                    data=expected_chyt_query,
                ),
                return_value=ok_response,
            ),
        ],
    )
    await task_creator.task(flat_logs_chyt_task_setup.context, task_params, {})
    assert flat_logs_chyt_task_setup.saturated()
