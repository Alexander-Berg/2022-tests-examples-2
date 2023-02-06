# pylint: disable=import-only-modules
import datetime

import pytest


MOCK_NOW = '2020-09-14T14:15:16+0000'
MOCK_NOW_DT = datetime.datetime(2020, 9, 14, 14, 15, 16)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(
        taxi_shuttle_control, taxi_shuttle_control_monitor, testpoint,
):
    @testpoint('speed_info')
    def _speed_info(data):
        assert data['speed_info'] == [60.0, 40.0]

    response = await taxi_shuttle_control.post(
        'service/cron', json={'task_name': 'shuttle-speed-monitor-cron'},
    )
    assert response.status_code == 200

    metrics = await taxi_shuttle_control_monitor.get_metric(
        'shuttle-speed-monitor',
    )
    assert metrics == {
        '$meta': {'solomon_children_labels': 'route-name'},
        'route1': {
            '$meta': {'solomon_children_labels': 'driver-uuid'},
            'uuid0': 60.0,
        },
        'route3': {
            '$meta': {'solomon_children_labels': 'driver-uuid'},
            'uuid4': 40.0,
        },
    }
