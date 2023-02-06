import socket

import pytest


HOST = socket.gethostname()


def get_task_name():
    return f'active-offers-monitor@{HOST}'


@pytest.mark.now('2018-11-20T13:00:00.000000')
@pytest.mark.pgsql(
    'reposition',
    files=[
        'mode_home.sql',
        'mode_poi.sql',
        'drivers.sql',
        'active_session.sql',
    ],
)
async def test_run(taxi_reposition_api, taxi_reposition_api_monitor):
    assert (
        await taxi_reposition_api.post(
            '/service/cron', json={'task_name': get_task_name()},
        )
    ).status_code == 200

    metrics = await taxi_reposition_api_monitor.get_metric(
        'active-offers-monitor',
    )

    assert metrics == {
        '$meta': {'solomon_children_labels': 'geozone'},
        'unknown': {
            '$meta': {'solomon_children_labels': 'reposition-offer-stats'},
            'active-offers': 6,
            'accepted-offers': 50,
        },
    }
