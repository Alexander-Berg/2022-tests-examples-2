# pylint: disable=C5521
import pytest

from .utils import get_task_name

MOCK_NOW = '2021-11-02T14:15:16+0000'


@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql(
    'reposition',
    files=[
        'drivers.sql',
        'mode_home.sql',
        'mode_poi.sql',
        'submodes_poi.sql',
        'active_session.sql',
        'bonus_drivers.sql',
    ],
)
async def test_run(taxi_reposition_api, taxi_reposition_api_monitor):
    assert (
        await taxi_reposition_api.post(
            '/service/cron',
            {'task_name': get_task_name('active-sessions-monitor-cron')},
        )
    ).status_code == 200

    metrics = await taxi_reposition_api_monitor.get_metric(
        'active-sessions-monitor',
    )

    assert metrics == {
        '$meta': {'solomon_children_labels': 'session-type'},
        'active': {
            '$meta': {'solomon_children_labels': 'mode'},
            'poi': {
                '$meta': {'solomon_children_labels': 'submode'},
                'None': 3,
                'fast': 1,
            },
        },
        'bonus': {
            '$meta': {'solomon_children_labels': 'mode'},
            'home': {
                '$meta': {'solomon_children_labels': 'submode'},
                'None': 1,
            },
        },
    }
