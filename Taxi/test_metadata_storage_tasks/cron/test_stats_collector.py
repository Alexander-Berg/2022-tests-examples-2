# pylint: disable=protected-access, redefined-outer-name
import asyncio
import datetime

import pytest

from taxi import stats

from metadata_storage_tasks.generated.cron import run_cron


NOW = datetime.datetime(2010, 1, 1, 12, 0)


def sensor_to_dict(sensor):
    return {'value': sensor.value, 'labels': sensor.labels}


@pytest.fixture()
def mock_stats(monkeypatch):
    measurer_data = []

    async def _data_sender(self):
        await self._sleep()
        while not self._stop_sender:
            self._sender_task = asyncio.create_task(
                self._gather_and_send_data(),
            )
            await self._wrap_and_wait_for_sender(self._sender_task)
            await self._sleep()

    async def on_shutdown(self):
        push_data = self._new_push_data()
        for aggregation in self._aggregations.values():
            if isinstance(aggregation, stats.MeasuresAggregation):
                measurer_data.append(aggregation._values)
            self._update_push_data(push_data, aggregation.dump())

        if self._sender_task is not None and not self._sender_task.done():
            await self._sender_task

        if self._cycle_task is not None:
            self._cycle_task.cancel()
            try:
                await self._cycle_task
            except asyncio.CancelledError:
                pass

    monkeypatch.setattr('taxi.stats.Stats._data_sender', _data_sender)
    monkeypatch.setattr('taxi.stats.Stats.on_shutdown', on_shutdown)
    return measurer_data


@pytest.mark.mongodb_collections('metadata_storage')
@pytest.mark.filldb(metadata_storage='empty')
async def test_collect_no_data(mock_stats):
    await run_cron.main(
        ['metadata_storage_tasks.crontasks.stats_collector', '-t', '0'],
    )
    assert not mock_stats


@pytest.mark.now(NOW.isoformat())
@pytest.mark.mongodb_collections('metadata_storage')
async def test_collect_with_data(mock_stats):
    await run_cron.main(
        ['metadata_storage_tasks.crontasks.stats_collector', '-t', '0'],
    )
    assert len(mock_stats) == 1
    assert sum(len(x) for x in mock_stats) == 1
    assert [sensor_to_dict(x) for senors in mock_stats for x in senors] == [
        {
            'value': 180,
            'labels': {'sensor': 'metadata_storage.oldest_doc_age_min'},
        },
    ]
