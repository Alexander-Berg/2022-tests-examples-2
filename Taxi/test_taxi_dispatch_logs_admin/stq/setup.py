import typing as tp

from taxi_dispatch_logs_admin.generated.stq3 import stq_context
from test_taxi_dispatch_logs_admin.common import mock


class TaskSetupBase:
    UPDATE_STATUS_TPL = """
        UPDATE common.yt_tasks
        SET status = $1,
            modified_timestamp = DEFAULT
        WHERE stq_queue = $2
            AND stq_task_id = $3;
    """

    ADD_YT_RESULT_TPL = """
        UPDATE common.yt_tasks
        SET yt_results = array_append(yt_results, $1),
            modified_timestamp = DEFAULT
        WHERE stq_queue = $2
            AND stq_task_id = $3;
    """

    YT_DESTINATION = {'path': '//dispatch-logs-admin'}

    LOG_SOURCES = {
        'buffer_dispatch': {
            'path': 'buffer_dispatch',
            'path_prefix': '//home',
            'tz_offset': '+0000',
        },
        'dispatch_buffer': {
            'path': '//dispatch_buffer/taxi',
            'tz_offset': '+0000',
        },
        'driver_dispatcher': {
            'path': '//driver-dispatcher',
            'tz_offset': '+0300',
        },
        'tracks': {'path': '//tracks', 'tz_offset': '+0300'},
    }

    QUERY_SETTINGS = {
        '__default__': {
            'order_id_fields': ['order_id'],
            'draw_id_fields': ['draw_id'],
            'driver_id_fields': ['dbid', 'clid'],
            'timestamp': {'field_type': 'integer', 'field_name': 'timestamp'},
        },
        'driver_dispatcher': {
            'order_id_fields': ['order_id', 'meta_order_id'],
            'draw_id_fields': ['draw_id', 'link'],
            'driver_id_fields': ['dbid', 'dbid_uuid'],
            'timestamp': {
                'field_type': 'string',
                'field_name': 'timestamp',
                'field_format': '%Y-%m-%dT%H:%M:%S',
            },
        },
        'tracks': {
            'order_id_fields': ['order_id', 'meta_order_id'],
            'draw_id_fields': ['draw_id', 'link'],
            'timestamp': {
                'field_type': 'string',
                'field_name': 'timestamp_changed',
            },
        },
    }

    DEFAULT_LOG_SUBTREE = {
        'type': 'map_node',
        '/': {
            '2019-01-01': {'type': 'table'},
            '2019-01-02': {'type': 'table'},
            '2019-01-03': {'type': 'table'},
        },
    }
    BUFFER_DISPATCH_SUBTREE = {
        'type': 'map_node',
        '/': {
            'orders': DEFAULT_LOG_SUBTREE,
            'draw': DEFAULT_LOG_SUBTREE,
            'candidates': DEFAULT_LOG_SUBTREE,
        },
    }
    DISPATCH_BUFFER_SUBTREE = {
        'type': 'map_node',
        '/': {
            'taxi-orders-log': DEFAULT_LOG_SUBTREE,
            'taxi-draw-log': DEFAULT_LOG_SUBTREE,
        },
    }
    CYPRESS_TREE = {
        '/': {
            'type': 'map_node',
            '/': {
                'dispatch_buffer': DISPATCH_BUFFER_SUBTREE,
                'driver-dispatcher': DEFAULT_LOG_SUBTREE,
                'tracks': DEFAULT_LOG_SUBTREE,
                'home': {
                    'type': 'map_node',
                    '/': {
                        'unittests': {
                            'type': 'map_node',
                            '/': {'buffer_dispatch': BUFFER_DISPATCH_SUBTREE},
                        },
                    },
                },
            },
        },
    }

    def __init__(self, queue, interface):
        self.queue = queue
        self.pg_mock = mock.PgMock()
        self.yt_mock = mock.YtMock()
        self.yt_mock.set_cypress_tree(TaskSetupBase.CYPRESS_TREE)
        self.context = stq_context.Context()

        cfg = self.context.config
        logs_admin_cfg = cfg.DISPATCH_LOGS_ADMIN

        logs_admin_cfg['yt_destination'] = TaskSetupBase.YT_DESTINATION
        logs_admin_cfg['log_sources'] = TaskSetupBase.LOG_SOURCES

        cfg.DISPATCH_LOGS_QUERY_SETTINGS = TaskSetupBase.QUERY_SETTINGS
        for log_source in logs_admin_cfg['log_sources'].values():
            log_source['interface'] = interface

    def saturated(self):
        return self.pg_mock.saturated()

    def expect_successful_pg_update(
            self, task_id: str, yt_results: tp.List[str], is_outdated=False,
    ):
        expectations = []
        expectations.append(
            mock.Expectation(
                mock.PgCallParams(
                    'execute',
                    TaskSetupBase.UPDATE_STATUS_TPL,
                    'running',
                    self.queue,
                    task_id,
                ),
                return_value='UPDATE 1',
            ),
        )

        for yt_result in yt_results:
            expectations.append(
                mock.Expectation(
                    mock.PgCallParams(
                        'execute',
                        TaskSetupBase.ADD_YT_RESULT_TPL,
                        yt_result,
                        self.queue,
                        task_id,
                    ),
                    return_value='UPDATE 1',
                ),
            )

        result_status = 'outdated' if is_outdated else 'completed'
        expectations.append(
            mock.Expectation(
                mock.PgCallParams(
                    'execute',
                    TaskSetupBase.UPDATE_STATUS_TPL,
                    result_status,
                    self.queue,
                    task_id,
                ),
                return_value='UPDATE 1',
            ),
        )

        self.pg_mock.expect(expectations)

    @property
    def expiration_time(self):
        return '2019-12-25T12:58:08+00:00'
