# pylint: disable=import-only-modules
import datetime
import socket

import pytest


MOCK_NOW = '2020-09-14T14:15:16+0000'
MOCK_NOW_DT = datetime.datetime(2020, 9, 14, 14, 15, 16)
_HOST = socket.gethostname()


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(taxi_shuttle_control, taxi_shuttle_control_monitor):
    response = await taxi_shuttle_control.post(
        'service/cron',
        json={'task_name': 'shuttle-route-load-monitor-cron@' + _HOST},
    )
    assert response.status_code == 200

    metrics = await taxi_shuttle_control_monitor.get_metric(
        'shuttle-route-load-monitor',
    )
    assert metrics == {
        '$meta': {'solomon_children_labels': 'route-name'},
        'route1': {
            '$meta': {'solomon_children_labels': 'driver-uuid'},
            'uuid0': {
                '$meta': {'solomon_children_labels': 'route-metric'},
                'capacity': 4,
                'created': 0,
                'driving': 1,
                'transporting': 2,
            },
            'uuid1': {
                '$meta': {'solomon_children_labels': 'route-metric'},
                'capacity': 5,
                'created': 0,
                'driving': 0,
                'transporting': 2,
            },
        },
        'route2': {
            '$meta': {'solomon_children_labels': 'driver-uuid'},
            'uuid2': {
                '$meta': {'solomon_children_labels': 'route-metric'},
                'capacity': 6,
                'created': 1,
                'driving': 1,
                'transporting': 1,
            },
        },
        'route3': {
            '$meta': {'solomon_children_labels': 'driver-uuid'},
            'uuid3': {
                '$meta': {'solomon_children_labels': 'route-metric'},
                'capacity': 6,
                'created': 0,
                'driving': 0,
                'transporting': 0,
            },
        },
    }
