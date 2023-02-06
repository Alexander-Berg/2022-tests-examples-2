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
        'service/cron', json={'task_name': 'shuttle-bookings-monitor-cron'},
    )
    assert response.status_code == 200

    metrics = await taxi_shuttle_control_monitor.get_metric(
        'shuttle-bookings-monitor',
    )
    assert metrics == {
        '$meta': {'solomon_children_labels': 'route-name'},
        'route1': {
            '$meta': {'solomon_children_labels': 'origin'},
            'application': {
                '$meta': {'solomon_children_labels': 'booking-status'},
                'cancelled': 0,
                'created': 4,
                'finished': 0,
            },
            'street_hail': {
                '$meta': {'solomon_children_labels': 'booking-status'},
                'cancelled': 1,
                'created': 3,
                'finished': 1,
            },
        },
        'route2': {
            '$meta': {'solomon_children_labels': 'origin'},
            'application': {
                '$meta': {'solomon_children_labels': 'booking-status'},
                'cancelled': 0,
                'created': 1,
                'finished': 0,
            },
            'street_hail': {
                '$meta': {'solomon_children_labels': 'booking-status'},
                'cancelled': 0,
                'created': 2,
                'finished': 1,
            },
        },
    }
