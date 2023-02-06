# pylint: disable=unused-variable
import datetime

import pytest

from scripts.stuff import scripts_by_environ


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.now(datetime.datetime(2019, 5, 30, 15).isoformat())
async def test_do_stuff(loop, patch, scripts_tasks_app):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def mock(*args, **kwargs):
        pass

    class StuffContext:
        data = scripts_tasks_app

    await scripts_by_environ.do_stuff(StuffContext(), loop)

    expected = [
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_environ.taxi.count',
                'value': 1,
                'timestamp': 1559228400.0,
            },
        },
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_environ.taximeter.count',
                'value': 1,
                'timestamp': 1559228400.0,
            },
        },
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_environ.by_cgroup.count',
                'value': 1,
                'timestamp': 1559228400.0,
            },
        },
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_environ.old_py3.count',
                'value': 1,
                'timestamp': 1559228400.0,
            },
        },
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_environ.total.count',
                'value': 4,
                'timestamp': 1559228400.0,
            },
        },
    ]
    assert sorted(mock.calls, key=lambda x: x['kwargs']['metric']) == sorted(
        expected, key=lambda x: x['kwargs']['metric'],
    )
