# pylint: disable=redefined-outer-name

import pytest

from taxi_dispatch_logs_admin.generated.stq3 import stq_context
from taxi_dispatch_logs_admin.stq import base_task
from taxi_dispatch_logs_admin.stq import helpers as stq_helpers
from test_taxi_dispatch_logs_admin.common import mock


class DummyTask(base_task.BaseTask):
    async def process(self):
        pass


class CommonTaskSetup:
    def __init__(self):
        self.queue = 'any'
        self.context = stq_context.Context()
        self.yt_mock = mock.YtMock()

    def task(self, from_dt: str, to_dt: str):
        task_params: dict = {
            'log_type': 'tracks',
            'task_id': 'any',
            'from_dt': from_dt,
            'to_dt': to_dt,
            'order_id': 'any',
            'draw_id': None,
            'extra_filters': {},
        }
        return DummyTask(self.context, 'any', task_params)


@pytest.fixture
def common_task_setup(simple_secdist, monkeypatch):
    task_setup = CommonTaskSetup()
    monkeypatch.setattr(
        stq_helpers,
        'yt_list_with_types',
        task_setup.yt_mock.yt_list_with_types,
    )
    monkeypatch.setattr(
        stq_helpers, 'yt_node_exists', task_setup.yt_mock.yt_node_exists,
    )
    return task_setup


@pytest.mark.parametrize(
    'from_dt, to_dt, tz_offset, cypress_tree, src_path, expected_tables',
    [
        (
            '2019-01-05T12:00:00Z',
            '2019-01-05T13:00:00Z',
            '+0000',
            {
                '/': {
                    'type': 'map_node',
                    '/': {
                        'logs': {
                            'type': 'map_node',
                            '/': {
                                '2019-01-01': {'type': 'table'},
                                '2019-01-02': {'type': 'table'},
                                '2019-01-03': {'type': 'table'},
                                '2019-01-04': {'type': 'table'},
                                '2019-01-05': {'type': 'table'},
                                '2019-01-06': {'type': 'table'},
                                '2019-01-07': {'type': 'table'},
                            },
                        },
                    },
                },
            },
            '//logs',
            ['//logs/2019-01-05'],
        ),
        (
            '2019-01-05T20:00:00Z',
            '2019-01-05T22:00:00Z',
            '+0300',
            {
                '/': {
                    'type': 'map_node',
                    '/': {
                        'logs': {
                            'type': 'map_node',
                            '/': {
                                '2019-01-01': {'type': 'table'},
                                '2019-01-02': {'type': 'table'},
                                '2019-01-03': {'type': 'table'},
                                '2019-01-04': {'type': 'table'},
                                '2019-01-05': {'type': 'table'},
                                '2019-01-06': {'type': 'table'},
                                '2019-01-07': {'type': 'table'},
                            },
                        },
                    },
                },
            },
            '//logs',
            ['//logs/2019-01-05', '//logs/2019-01-06'],
        ),
        (
            '2019-01-31T20:00:00Z',
            '2019-02-01T01:00:00Z',
            '+0000',
            {
                '/': {
                    'type': 'map_node',
                    '/': {
                        'logs': {
                            'type': 'map_node',
                            '/': {
                                '2019-01': {'type': 'table'},
                                '2019-02-01': {'type': 'table'},
                                '2019-02-02': {'type': 'table'},
                                '2019-02-03': {'type': 'table'},
                            },
                        },
                    },
                },
            },
            '//logs',
            ['//logs/2019-01', '//logs/2019-02-01'],
        ),
        (
            '2019-01-03T23:00:00Z',
            '2019-01-04T01:30:00Z',
            '+0000',
            {
                '/': {
                    'type': 'map_node',
                    '/': {
                        '1d': {
                            'type': 'map_node',
                            '/': {
                                '2019-01-01': {'type': 'table'},
                                '2019-01-02': {'type': 'table'},
                                '2019-01-03': {'type': 'table'},
                            },
                        },
                        '1h': {
                            'type': 'map_node',
                            '/': {
                                '2019-01-04T00:00:00': {'type': 'table'},
                                '2019-01-04T01:00:00': {'type': 'table'},
                                '2019-01-04T02:00:00': {'type': 'table'},
                            },
                        },
                        'stream': {
                            'type': 'map_node',
                            '/': {
                                '5min': {
                                    'type': 'map_node',
                                    '/': {
                                        '2019-01-04T00:30:00': {
                                            'type': 'table',
                                        },
                                        '2019-01-04T00:35:00': {
                                            'type': 'table',
                                        },
                                        '2019-01-04T02:00:00': {
                                            'type': 'table',
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            '/',
            [
                '//1d/2019-01-03',
                '//1h/2019-01-04T00:00:00',
                '//1h/2019-01-04T01:00:00',
                '//stream/5min/2019-01-04T00:30:00',
                '//stream/5min/2019-01-04T00:35:00',
            ],
        ),
        (
            '2019-01-01T00:00:00Z',
            '2019-01-19T03:07:00Z',
            '+0000',
            {
                '/': {
                    'type': 'map_node',
                    '/': {
                        '5min': {
                            'type': 'map_node',
                            '/': {
                                '2019-01-19T02:50:00': {'type': 'table'},
                                '2019-01-19T02:55:00': {'type': 'table'},
                                '2019-01-19T03:00:00': {'type': 'table'},
                                '2019-01-19T03:00:00-bad': {'type': 'table'},
                                '2019-01-19T03:05:00': {'type': 'table'},
                                '2019-01-19T03:10:00': {'type': 'table'},
                            },
                        },
                        '1d': {
                            'type': 'map_node',
                            '/': {
                                '2019-01-15': {'type': 'table'},
                                '2019-01-16': {'type': 'table'},
                                '2019-01-17': {'type': 'table'},
                                '2019-01-18': {'type': 'table'},
                            },
                        },
                        '1h': {
                            'type': 'map_node',
                            '/': {
                                '2019-01-18T22:00:00': {'type': 'table'},
                                '2019-01-18T23:00:00': {'type': 'table'},
                                '2019-01-19T00:00:00': {'type': 'table'},
                                '2019-01-19T01:00:00': {'type': 'table'},
                                '2019-01-19T02:00:00': {'type': 'table'},
                            },
                        },
                        '1w': {
                            'type': 'map_node',
                            '/': {
                                '2019-01-01': {'type': 'table'},
                                '2019-01-08': {'type': 'table'},
                            },
                        },
                    },
                },
            },
            '/',
            [
                '//1w/2019-01-01',
                '//1w/2019-01-08',
                '//1d/2019-01-15',
                '//1d/2019-01-16',
                '//1d/2019-01-17',
                '//1d/2019-01-18',
                '//1h/2019-01-19T00:00:00',
                '//1h/2019-01-19T01:00:00',
                '//1h/2019-01-19T02:00:00',
                '//5min/2019-01-19T03:00:00',
                '//5min/2019-01-19T03:05:00',
            ],
        ),
    ],
)
async def test_tables_filtration(
        common_task_setup,
        from_dt,
        to_dt,
        tz_offset,
        cypress_tree,
        src_path,
        expected_tables,
):
    common_task_setup.yt_mock.set_cypress_tree(cypress_tree)
    task = common_task_setup.task(from_dt, to_dt)
    task.tz_offset = tz_offset

    assert task.filter_tables(src_path) == expected_tables
