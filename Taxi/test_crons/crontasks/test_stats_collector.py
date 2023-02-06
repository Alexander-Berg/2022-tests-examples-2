# pylint: disable=protected-access, redefined-outer-name
import asyncio

import pytest

from taxi import stats

from crons.generated.cron import run_cron


class _AnyNumber:
    def __eq__(self, other):
        return isinstance(other, (int, float))

    def __repr__(self):
        return self.__class__.__name__


ANY_NUMBER = _AnyNumber()


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


async def test_do_stuff(patch, mock_stats):
    await run_cron.main(['crons.crontasks.stats_collector', '-t', '0'])
    assert len(mock_stats) == 43
    assert sum(len(x) for x in mock_stats) == 44
    serialized_sensors = [
        sensor_to_dict(x) for senors in mock_stats for x in senors
    ][:11]
    assert serialized_sensors == [
        {
            'labels': {
                'collection': 'crons.cron_commands',
                'operation': 'unknown.count',
                'sensor': 'mongo.operation.timing',
            },
            'value': ANY_NUMBER,
        },
        {
            'labels': {
                'collection': 'crons.cron_commands',
                'operation': 'unknown.count',
                'sensor': 'mongo.operation.timing',
            },
            'value': ANY_NUMBER,
        },
        {
            'labels': {
                'sensor': 'cron_commands.count_by_status',
                'status': 'queued',
            },
            'value': 1.0,
        },
        {
            'labels': {
                'sensor': 'cron_commands.count_by_status',
                'status': 'accepted',
            },
            'value': 1.0,
        },
        {'labels': {'sensor': 'cron_commands.max_accept_time'}, 'value': 10.0},
        {
            'labels': {
                'collection': 'crons.cron_commands',
                'operation': 'unknown.to_list',
                'sensor': 'mongo.operation.timing',
            },
            'value': ANY_NUMBER,
        },
        {
            'labels': {
                'collection': 'crons.cron_monitor',
                'sensor': 'mongo.collection.stats.sizeMb',
            },
            'value': 0.0,
        },
        {
            'labels': {
                'collection': 'crons.cron_monitor',
                'sensor': 'mongo.collection.stats.docsCount',
            },
            'value': 0.0,
        },
        {
            'labels': {
                'collection': 'crons.cron_monitor',
                'sensor': 'mongo.collection.stats.avgDocSizeB',
            },
            'value': 0.0,
        },
        {
            'labels': {
                'collection': 'crons.cron_monitor',
                'sensor': 'mongo.collection.stats.indicesCount',
            },
            'value': 6.0,
        },
        {
            'labels': {
                'collection': 'crons.cron_monitor',
                'indexName': '_id_',
                'sensor': 'mongo.collection.stats.indexSizeMb',
            },
            'value': ANY_NUMBER,
        },
    ]
