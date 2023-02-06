# pylint: disable=import-only-modules
import pytest

from tests_reposition_watcher.utils import get_task_name


@pytest.mark.now('2010-01-01T02:00:00+0000')
@pytest.mark.pgsql('reposition_watcher', files=['test.sql'])
async def test_monitor(
        taxi_reposition_watcher, mockserver, pgsql, testpoint, statistics,
):
    @testpoint('reposition-watcher-monitor::finish')
    def _on_watcher_monitor_finish(data):
        pass

    response = await taxi_reposition_watcher.post(
        'service/cron',
        json={'task_name': get_task_name('reposition-watcher-monitor')},
    )

    assert response.status_code == 200
    await _on_watcher_monitor_finish.wait_call()
