# pylint: disable=unused-variable
import datetime

import pytest

from scripts.stuff import scripts_by_organizations


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.now(datetime.datetime(2019, 5, 30, 20).isoformat())
async def test_do_stuff(loop, patch, scripts_tasks_app):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def mock(*args, **kwargs):
        pass

    class StuffContext:
        data = scripts_tasks_app

    await scripts_by_organizations.do_stuff(StuffContext(), loop)

    expected = [
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_organization.taxi.count',
                'value': 3,
                'timestamp': 1559246400.0,
            },
        },
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_organization.taximeter.count',
                'value': 1,
                'timestamp': 1559246400.0,
            },
        },
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_organization.total.count',
                'value': 4,
                'timestamp': 1559246400.0,
            },
        },
    ]
    assert sorted(mock.calls, key=lambda x: x['kwargs']['metric']) == sorted(
        expected, key=lambda x: x['kwargs']['metric'],
    )
