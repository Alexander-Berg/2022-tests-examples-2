# pylint: disable=redefined-outer-name

import pytest

from taxi_dispatch_logs_admin.common import helpers
from taxi_dispatch_logs_admin.generated.stq3 import stq_settings
from taxi_dispatch_logs_admin.stq import base_task
from taxi_dispatch_logs_admin.stq import flat_logs_yql_task
from taxi_dispatch_logs_admin.stq import helpers as stq_helpers
from test_taxi_dispatch_logs_admin.common import mock
from test_taxi_dispatch_logs_admin.stq import setup


class FlatLogsYQLTaskSetup(setup.TaskSetupBase):
    def __init__(self, interface):
        super().__init__(
            stq_settings.STQ_DISPATCH_LOGS_ADMIN_YQL_IMPORTS_QUEUE, interface,
        )
        self.yql_mock = mock.YqlMock()

    def saturated(self):
        return super().saturated() and self.yql_mock.saturated()


@pytest.fixture
def flat_logs_yql_task_setup(simple_secdist, monkeypatch):
    task_setup = FlatLogsYQLTaskSetup('yql')
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
    monkeypatch.setattr(
        flat_logs_yql_task,
        'sync_run_yql_query',
        task_setup.yql_mock.sync_run_yql_query,
    )
    monkeypatch.setattr(helpers, 'pg_perform', task_setup.pg_mock.pg_perform)
    monkeypatch.setattr(
        base_task.BaseTask, 'expiration_time', task_setup.expiration_time,
    )
    return task_setup


@pytest.mark.parametrize(
    """
        task_params,
        expected_yt_result,
        expected_yql_query
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
            '//dispatch-logs-admin/0123_yql_driver_dispatcher',
            """
                PRAGMA yt.ExpirationDeadline = "2019-12-25T12:58:08+00:00";
                INSERT INTO
                    `//dispatch-logs-admin/0123_yql_driver_dispatcher`
                WITH TRUNCATE
                SELECT *
                FROM CONCAT(
                    `//driver-dispatcher/2019-01-01`,
                    `//driver-dispatcher/2019-01-02`)
                WHERE `timestamp` BETWEEN '2019-01-01T23:00:00'
                        AND '2019-01-02T02:00:00'
                    AND (WeakField(`dbid`, 'String', NULL) = '888' OR
                    WeakField(`dbid_uuid`, 'String', NULL) = '888')
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
            '//dispatch-logs-admin/0123_yql_driver_dispatcher',
            """
                PRAGMA yt.ExpirationDeadline = "2019-12-25T12:58:08+00:00";
                INSERT INTO
                    `//dispatch-logs-admin/0123_yql_driver_dispatcher`
                WITH TRUNCATE
                SELECT *
                FROM CONCAT(
                    `//driver-dispatcher/2019-01-01`,
                    `//driver-dispatcher/2019-01-02`)
                WHERE `timestamp` BETWEEN '2019-01-01T23:00:00'
                        AND '2019-01-02T02:00:00'
                    AND (WeakField(`order_id`, 'String', NULL) = 'order_id_0'
                        OR WeakField(`meta_order_id`, 'String', NULL) =
                            'order_id_0')
                    AND (WeakField(`dbid`, 'String', NULL) = '888' OR
                    WeakField(`dbid_uuid`, 'String', NULL) = '888')
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
            '//dispatch-logs-admin/0123_yql_tracks',
            """
                PRAGMA yt.ExpirationDeadline = "2019-12-25T12:58:08+00:00";
                INSERT INTO `//dispatch-logs-admin/0123_yql_tracks`
                WITH TRUNCATE
                SELECT *
                FROM CONCAT(
                    `//tracks/2019-01-03`)
                WHERE `timestamp_changed` BETWEEN '2019-01-03 13:00:00'
                        AND '2019-01-03 13:30:00'
                    AND (WeakField(`order_id`, 'String', NULL) =
                            'order_id_0'
                        OR WeakField(`meta_order_id`, 'String', NULL) =
                            'order_id_0')
                    AND (WeakField(`draw_id`, 'String', NULL) = 'draw_id_0'
                        OR WeakField(`link`, 'String', NULL) = 'draw_id_0')
                ORDER BY `timestamp_changed` DESC;
            """,
        ),
    ],
)
async def test_flat_logs_yql_task(
        flat_logs_yql_task_setup,
        task_params,
        expected_yt_result,
        expected_yql_query,
):
    flat_logs_yql_task_setup.yt_mock.expect_configure(
        mock.Expectation(('hahn.yt.yandex.net', 'FAKE_YT_TOKEN')),
    )
    flat_logs_yql_task_setup.expect_successful_pg_update(
        task_params['task_id'], [expected_yt_result],
    )
    flat_logs_yql_task_setup.yql_mock.expect(
        [
            mock.Expectation(
                mock.YqlCallParams(
                    'hahn',
                    'hahn.yt.yandex.net',
                    'FAKE_YQL_TOKEN',
                    expected_yql_query,
                ),
            ),
        ],
    )
    await flat_logs_yql_task.task(
        flat_logs_yql_task_setup.context, task_params, {},
    )
    assert flat_logs_yql_task_setup.saturated()


async def test_not_found(flat_logs_yql_task_setup):
    flat_logs_yql_task_setup.yt_mock.set_cypress_tree(
        {
            '/': {
                'type': 'map_node',
                '/': {'driver-dispatcher': {'type': 'map_node', '/': {}}},
            },
        },
    )
    task_params = {
        'log_type': 'driver_dispatcher',
        'task_id': '0123',
        'from_dt': '2019-01-01T20:00:00Z',
        'to_dt': '2019-01-01T23:00:00Z',
        'order_id': 'order_id_0',
        'draw_id': None,
    }
    flat_logs_yql_task_setup.yt_mock.expect_configure(
        mock.Expectation(('hahn.yt.yandex.net', 'FAKE_YT_TOKEN')),
    )
    flat_logs_yql_task_setup.expect_successful_pg_update(
        task_params['task_id'], [],
    )
    await flat_logs_yql_task.task(
        flat_logs_yql_task_setup.context, task_params, {},
    )
    assert flat_logs_yql_task_setup.saturated()
