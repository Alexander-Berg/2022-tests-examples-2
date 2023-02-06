# pylint: disable=unused-variable
import datetime

import pytest

from scripts.stuff import scripts_by_state


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.now(datetime.datetime(2019, 5, 30, 14).isoformat())
async def test_do_stuff(loop, patch, scripts_tasks_app):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def mock(*args, **kwargs):
        pass

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def get_drafts_mock(data, log_extra):
        return [
            {
                'status': 'applying',
                'change_doc_id': 'scripts_test-send-stats-1',
            },
            {'status': 'failed', 'change_doc_id': 'scripts_test-send-stats-2'},
            {
                'status': 'need_approval',
                'change_doc_id': 'scripts_test-send-stats-3',
            },
            {
                'status': 'succeeded',
                'change_doc_id': 'scripts_test-send-stats-4',
            },
        ]

    class StuffContext:
        data = scripts_tasks_app

    await scripts_by_state.do_stuff(StuffContext(), loop)
    expected = [
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_state.need_approval.count',
                'value': 1,
                'timestamp': 1559224800.0,
            },
        },
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_state.succeeded.count',
                'value': 1,
                'timestamp': 1559224800.0,
            },
        },
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_state.running.count',
                'value': 1,
                'timestamp': 1559224800.0,
            },
        },
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_state.failed.count',
                'value': 1,
                'timestamp': 1559224800.0,
            },
        },
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_state.applying.count',
                'value': 1,
                'timestamp': 1559224800.0,
            },
        },
        {
            'args': (),
            'kwargs': {
                'metric': 'scripts.by_state.total.count',
                'value': 4,
                'timestamp': 1559224800.0,
            },
        },
    ]
    assert sorted(mock.calls, key=lambda x: x['kwargs']['metric']) == sorted(
        expected, key=lambda x: x['kwargs']['metric'],
    )
