import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi_maintenance.monrun import main
from taxi_maintenance.monrun.checks.yt import pool_resources
from taxi_maintenance.monrun.checks.yt import resources


class TableObj(object):
    def __init__(self, path, attributes):
        self.path = path
        self.attributes = attributes

    def __str__(self):
        return self.path


class MockYtClient(object):
    config = {'proxy': {'retries': {}}, 'prefix': '//prefix/'}
    resources_info = {
        '//sys/accounts/taxi/@resource_limits': {
            'disk_space_per_medium': {
                'default': 100,
                'ssd_blobs': 100,
                'cloud': 1,
                'ssd_journals': 100,
            },
            'tablet_count': 10,
            'tablet_static_memory': 5,
            'disk_space': 100,
            'chunk_count': 100,
            'node_count': 10,
        },
        '//sys/accounts/taxi/@committed_resource_usage': {
            'disk_space_per_medium': {
                'default': 81,
                'ssd_blobs': 90,
                'cloud': 1,
                'ssd_journals': 90,
            },
            'tablet_count': 8,
            'tablet_static_memory': 3,
            'disk_space': 35,
            'chunk_count': 70,
            'node_count': 7,
        },
    }

    flush_data = {
        'hahn': [
            TableObj('private/mongo/bson/orders',
                     attributes={'flush_lag_time': 10000000}),
        ],
        'arnold': [
            TableObj('private/mongo/bson/orders',
                     attributes={'flush_lag_time': 11000000}),
        ],
        'seneca-sas': [
            TableObj('private/mongo/bson/orders',
                     attributes={'flush_lag_time': 20000000}),
        ],
    }

    def __init__(self, client_name):
        self.client_name = client_name

    def get(self, path, *args, **kwargs):
        return self.resources_info[path]

    def search(self, *args, **kwargs):
        return self.flush_data[self.client_name]


@pytest.mark.config(YT_RESOURCES_MONITOR={'__default__': {}})
@pytest.inline_callbacks
def test_check_resources_dummy(patch, monkeypatch):
    yield _check_resources(patch, monkeypatch, '0; OK', None)


@pytest.mark.config(YT_RESOURCES_MONITOR={
        '__default__': {
            '__default__': {
                'chunk_count': {
                    'warning': 80,
                    'critical': 90,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
                'disk_space_per_medium_default': {
                    'warning': 80,
                    'critical': 90,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
                'disk_space_per_medium_ssd_blobs': {
                    'warning': 80,
                    'critical': 90,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
                'disk_space_per_medium_ssd_journals': {
                    'warning': 80,
                    'critical': 90,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
                'node_count': {
                    'warning': 80,
                    'critical': 90,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
                'tablet_count': {
                    'warning': 80,
                    'critical': 90,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
            },
        }
    }
)
@pytest.inline_callbacks
def test_check_resources(patch, monkeypatch):
    yield _check_resources(
        patch,
        monkeypatch,
        '2; CRIT (2 problems): hahn: disk_space_per_medium.ssd_blobs = 90.0%, '
        'disk_space_per_medium.ssd_journals = 90.0%, WARN (2 problems): hahn: '
        'disk_space_per_medium.default = 81.0%, tablet_count = 80.0%',
        2,
    )


@pytest.mark.config(YT_RESOURCES_MONITOR={
        '__default__': {
            '__default__': {
                'chunk_count': {
                    'warning': 80,
                    'critical': 90,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
                'disk_space_per_medium_default': {
                    'warning': 82,
                    'critical': 90,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
                'disk_space_per_medium_ssd_blobs': {
                    'warning': 91,
                    'critical': 99,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
                'disk_space_per_medium_ssd_journals': {
                    'warning': 91,
                    'critical': 99,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
                'node_count': {
                    'warning': 90,
                    'critical': 99,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
                'tablet_count': {
                    'warning': 90,
                    'critical': 99,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
            },
        }
    }
)
@pytest.inline_callbacks
def test_check_resources_ok(patch, monkeypatch):
    yield _check_resources(patch, monkeypatch, '0; OK', None)


@pytest.mark.config(YT_RESOURCES_MONITOR={
        '__default__': {
            '__default__': {
                'chunk_count': {
                    'warning': 0,
                    'critical': 0,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
                'disk_space_per_medium_default': {
                    'warning': 84,
                    'critical': 90,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
                'disk_space_per_medium_ssd_blobs': {
                    'warning': 91,
                    'critical': 99,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
            },
        },
        'taxi': {
            'hahn': {
                'chunk_count': {
                    'warning': 70,
                    'critical': 90,
                },
            },
        },
    }
)
@pytest.inline_callbacks
def test_check_resources_warn(patch, monkeypatch):
    yield _check_resources(
        patch,
        monkeypatch,
        '1; WARN (2 problems): '
        'hahn: disk_space_per_medium.ssd_blobs = 90.0%, chunk_count = 70.0%',
        1,
    )


@pytest.mark.config(YT_RESOURCES_MONITOR={
        '__default__': {},
        'taxi': {
            'hahn': {
                'chunk_count': {
                    'warning': 70,
                    'critical': 90,
                    'gap_at_decrease_warning': 2,
                    'gap_at_decrease_critical': 2,
                },
            },
        },
    }
)
@pytest.inline_callbacks
def test_check_resources_warn_no_default(patch, monkeypatch):
    yield _check_resources(
        patch,
        monkeypatch,
        '1; WARN (1 problem): hahn: chunk_count = 70.0%',
        1,
    )


@pytest.mark.config(YT_RESOURCES_MONITOR={
        '__default__': {
            '__default__': {
                'chunk_count': {
                    'warning': 80,
                    'critical': 90,
                },
                'tablet_count': {
                    'warning': 90,
                    'critical': 99,
                },
            },
        },
        'taxi': {
            'hahn': {
                'chunk_count': {
                    'warning': 70,
                    'critical': 90,
                },
            },
        },
    }
)
@pytest.inline_callbacks
def test_check_resources_by_cluster(patch, monkeypatch):
    yield _check_resources(
        patch,
        monkeypatch,
        '1; WARN (1 problem): hahn: chunk_count = 70.0%',
        1,
        client_name='hahn',
    )


@pytest.inline_callbacks
def _check_resources(patch, monkeypatch, expected_msg, expected_status,
                     client_name=None):
    monkeypatch.setattr(settings, 'YT_ACCOUNTS_CLIENTS_MAP', {'taxi': ['hahn']})
    _patch_clients(monkeypatch, patch)
    args = ['yt_resources', 'taxi']
    if client_name:
        args.extend(('--client-name', client_name))

    msg = yield main.run(args)
    assert msg == expected_msg

    result_status = yield resources._get_event(
        'taxi', client_name
    ).get_recent()
    if expected_status is None:
        assert result_status is None
    else:
        assert result_status['status'] == expected_status
        assert '%s; %s' % (
            result_status['status'], result_status['msg']
        ) == expected_msg


def _patch_clients(monkeypatch, patch, client_names=('hahn',)):
    clients = {
        client_name: MockYtClient(client_name) for client_name in client_names
    }
    monkeypatch.setattr(
        'taxi.external.yt_wrapper._environments', clients
    )

    @patch('taxi.external.yt_wrapper.get_all_replication_clusters')
    def get_all_replication_clusters():
        return client_names

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(client_name, *args, **kwargs):
        assert not (
            kwargs['extra_config_overrides'][('proxy', 'retries', 'enable')]
        )
        return clients[client_name]


@pytest.mark.filldb(_fill=False)
@pytest.mark.now('2016-07-01T00:00:00')
@pytest.mark.config(YT_POOL_QUEUE_THRESHOLDS={
    'arnold': {
        'test-pool': {
            'critical': 30,
            'gap_at_decrease_critical': 10,
            'gap_at_decrease_warning': 10,
            'warning': 20
        },
        'test-pool-2': {
            'critical': 30,
            'gap_at_decrease_critical': 10,
            'gap_at_decrease_warning': 10,
            'warning': 20
        }
    },
    'hahn': {
        'test-pool': {
            'critical': 30,
            'gap_at_decrease_critical': 10,
            'gap_at_decrease_warning': 10,
            'warning': 15,
        }
    }
})
@pytest.mark.parametrize('sensor_values,expected_msg,expected_status', [
    ({
        'hahn': [
            {
                'labels': {'pool': pool, 'sensor': sensor},
                'values': [{'value': 1}, {'value': 5}],
            } for pool, sensor in [
                ('test-pool', 'yt.scheduler.running_operation_count'),
                ('test-pool', 'yt.scheduler.total_operation_count'),
            ]
        ],
        'arnold': [
            {
                'labels': {'pool': pool, 'sensor': sensor},
                'values': [{'value': 1}, {'value': 5}],
            } for pool, sensor in [
                ('test-pool', 'yt.scheduler.running_operation_count'),
                ('test-pool', 'yt.scheduler.total_operation_count'),
                ('test-pool-2', 'yt.scheduler.running_operation_count'),
                ('test-pool-2', 'yt.scheduler.total_operation_count'),
            ]
        ],
    }, '0; OK', None),
    ({
        'hahn': [
            {
                'labels': {'pool': pool, 'sensor': sensor},
                'values': [{'value': value}],
            } for pool, sensor, value in [
                ('test-pool', 'yt.scheduler.running_operation_count', 2),
                ('test-pool', 'yt.scheduler.total_operation_count', 23),
            ]
        ],
        'arnold': [
            {
                'labels': {'pool': pool, 'sensor': sensor},
                'values': [{'value': value}],
            } for pool, sensor, value in [
                ('test-pool', 'yt.scheduler.running_operation_count', 1),
                ('test-pool', 'yt.scheduler.total_operation_count', 1),
                ('test-pool-2', 'yt.scheduler.running_operation_count', 1),
                ('test-pool-2', 'yt.scheduler.total_operation_count', 1),
            ]
        ],
    }, '1; WARN (1 problem): hahn: operations_queue_size.test-pool = 21.0', 1),
    ({
         'hahn': [
             {
                 'labels': {'pool': pool, 'sensor': sensor},
                 'values': [{'value': value}],
             } for pool, sensor, value in [
                 ('test-pool', 'yt.scheduler.running_operation_count', 2),
                 ('test-pool', 'yt.scheduler.total_operation_count', 18),
             ]
         ],
         'arnold': [
             {
                 'labels': {'pool': pool, 'sensor': sensor},
                 'values': [{'value': value}],
             } for pool, sensor, value in [
                 ('test-pool', 'yt.scheduler.running_operation_count', 1),
                 ('test-pool', 'yt.scheduler.total_operation_count', 35),
                 ('test-pool-2', 'yt.scheduler.running_operation_count', 1),
                 ('test-pool-2', 'yt.scheduler.total_operation_count', 1),
             ]
         ],
     }, '2; CRIT (1 problem): arnold: operations_queue_size.test-pool = 34.0, '
        'WARN (1 problem): hahn: operations_queue_size.test-pool = 16.0', 2),
])
@pytest.inline_callbacks
def test_check_pool_resources(monkeypatch, patch, sensor_values, expected_msg,
                              expected_status):
    yield db.event_monitor.remove({'name': 'yt_operations_queue_size_monrun'})
    call_args = []
    clusters_sensors_values = {
        'arnold': {
            ('yt.scheduler.running_operation_count|'
             'yt.scheduler.total_operation_count',
             ('test-pool|test-pool-2', 'test-pool-2|test-pool')):
                 sensor_values['arnold'],
        },
        'hahn': {
            ('yt.scheduler.running_operation_count|'
             'yt.scheduler.total_operation_count',
             ('test-pool',)): sensor_values['hahn'],
        }
    }

    @patch('taxi.external.solomon.get_sensors_values')
    @async.inline_callbacks
    def get_sensors_values(project, cluster, service, query_labels, date_from,
                           date_to=None, points=None, log_extra=None):
        call_args.append((date_from, date_to))
        yield
        if cluster in clusters_sensors_values:
            pool_labels = query_labels['pool']
            sensor_labels = query_labels['sensor']
            for args, result in clusters_sensors_values[cluster].iteritems():
                if pool_labels in args[1] and sensor_labels == args[0]:
                    async.return_value({'sensors': result})
        async.return_value()

    msg = yield main.run(['yt_pool_resources'])
    assert msg == expected_msg

    result_status = yield pool_resources.EVENT.get_recent()
    if expected_status is None:
        assert result_status is None
    else:
        assert result_status['status'] == expected_status
