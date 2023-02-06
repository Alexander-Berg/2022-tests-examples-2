import time
import typing
import asyncio
import logging
from contextlib import contextmanager
import pytest
from _pytest.logging import LogCaptureFixture
from easytap.pytest_plugin import PytestTap

from libstall.log import log, metrics_log
from stall.model.stash import Stash
from stall.model.logbroker.base import TopicMessageBase
from stall.model.event_cache import EventLB, EventLP, EventQueue, EventSTQ
from stall.monitoring import (
    order,
    event_cache,
    order_event,
    detect_store_problems,
)
from stall.scripts.monitoring import (
    MonitoringDaemon,
    MetricLogReporter
)
from stall.shard_schema import eid_for_shard


@contextmanager
def propagate_log(logger: logging.Logger):
    propagate_backup = logger.propagate
    logger.propagate = True
    try:
        yield
    finally:
        logger.propagate = propagate_backup


@contextmanager
def run_daemon_in_background(daemon: typing.Coroutine):
    daemon_task = asyncio.create_task(daemon)
    try:
        yield
    finally:
        daemon_task.cancel()


class ReporterStub:
    # pylint: disable=unused-argument

    def __init__(self):
        self.data = {}

    async def send_value(self, sensor_name, value, agg=None, labels=None):
        if labels:
            keys = sorted(labels.keys())
            sensor_name += (
                ' | '
                + ' | '.join(f'{k}: {labels[k]}' for k in keys)
            )
        self.data[sensor_name] = value


async def test_discover_handles(tap):
    handles = MonitoringDaemon.discover_handles(
        'tests.scripts.package_to_load')
    with tap.plan(2):
        tap.eq_ok(len(handles), 1, 'One handle loaded')
        tap.eq_ok(await handles[0](), 'hello', 'Function works correctly')


async def test_report_event_cache(tap, dataset):
    with tap.plan(24, 'По каждому типу ивентов должны быть метрики'):
        events = [
            EventQueue.create(
                tube='job',
                callback='callback',
            ),
            EventLP(**{
                'key': ['key'],
                'data': {}
            }),
            EventLB.create(TopicMessageBase()),
            EventSTQ(
                queue='grocery_performer_communications_common_message',
                args=['arg1'],
                kwargs={
                    'some_key': 'some_value',
                }
            ),
        ]

        await Stash(stash_id=eid_for_shard(2, 0), value={}).save(events=events)
        await Stash(stash_id=eid_for_shard(2, 1), value={}).save(events=events)

        tablo_metric = await dataset.tablo_metric()
        await tablo_metric.save(events=events)

        reporter = ReporterStub()
        await event_cache.handle(reporter)

        parts = [
            ('main', 'lp', 0),
            ('main', 'lp', 1),
            ('main', 'stq', 0),
            ('main', 'stq', 1),
            ('main', 'queue', 0),
            ('main', 'queue', 1),
            ('main', 'logbroker', 0),
            ('main', 'logbroker', 1),
            ('analytics', 'lp', 0),
            ('analytics', 'stq', 0),
            ('analytics', 'queue', 0),
            ('analytics', 'logbroker', 0),
        ]
        for db, event_type, shard in parts:
            info = f'database: {db} | event_type: {event_type} | shard: {shard}'
            for sensor in ['event_cache.lag', 'event_cache.count']:
                tap.in_ok(
                    f'{sensor} | {info}', reporter.data, f'{sensor} | {info}',
                )


async def test_report_order(tap):
    reporter = ReporterStub()
    await order.handle(reporter)

    with tap.plan(2):
        tap.ok('order_oldest_order_shard_0' in reporter.data,
               'oldest_order for shard 0 is set')
        tap.ok('order_oldest_order_shard_1' in reporter.data,
               'oldest_order for shard 1 is set')


async def test_report_order_event(tap: PytestTap):
    reporter = ReporterStub()
    await order_event.handle(reporter)

    with tap.plan(4):
        tap.ok(reporter.data['order_event.est_table_size.shard_0'] >= 0,
               'est_table_size for shard 0 is set')
        tap.ok(reporter.data['order_event.est_table_size.shard_1'] >= 0,
               'est_table_size for shard 1 is set')
        tap.ok(reporter.data['order_event.oldest_lifetime.shard_0'] >= 0,
               'oldest_lifetime for shard 0 is set')
        tap.ok(reporter.data['order_event.oldest_lifetime.shard_1'] >= 0,
               'oldest_lifetime for shard 1 is set')


async def test_detect_store_problems(tap: PytestTap, dataset, time_mock):
    with tap.plan(6, 'Проверим мониторинг расчета здоровья'):
        sleeping_time = 60
        store = await dataset.store()
        await dataset.store_problem(store_id=store.store_id)
        await dataset.store_health(store_id=store.store_id)
        await dataset.tablo_metric(store_id=store.store_id)
        time_mock.sleep(seconds=sleeping_time)

        reporter = ReporterStub()
        await detect_store_problems.handle(reporter, store_id=store.store_id)

        for table in ['store_problems', 'store_healths', 'tablo_metrics']:
            metric = reporter.data[
                'detect_store_problems.lag | sensor_group: current'
                f' | table: {table}'
            ]
            tap.ok(
                sleeping_time / 2 < metric <= sleeping_time,
                f'{table}: {sleeping_time / 2} < {metric} <= {sleeping_time}'
            )
            metric = reporter.data[
                'detect_store_problems.lag | sensor_group: limit'
                f' | table: {table}'
            ]
            tap.eq(
                metric,
                detect_store_problems.TIME_LIMIT * 2,
                f'{table}: Limit: {metric}'
            )


async def handle1(reporter):
    await reporter.send_value('metrci3', 3)


async def handle2(reporter):
    await reporter.send_value('metric5', 5)
    await reporter.send_value('metric7', 7)


async def handle_with_exception(_):
    raise ValueError('Some exception')


async def handle_delay_100_ms(_):
    await asyncio.sleep(0.1)


async def test_handle_name(tap: PytestTap):
    name = MonitoringDaemon.get_handle_name(order_event.handle)
    with tap.plan(1, 'Провекра имени ручки мониторинга'):
        tap.in_ok('stall.monitoring.order_event.handle', name,
                  'Имя хендлера корреткно')


@pytest.mark.parametrize('handles,required_metrics', (
    ([handle1], ['metrci3']),
    ([handle2], ['metric5', 'metric7']),
    ([handle1, handle2], ['metrci3', 'metric5', 'metric7']),
))
async def test_monitoring_daemon(tap: PytestTap, handles, required_metrics):
    reporter = ReporterStub()
    period = 0.01

    with tap:
        required_metrics = set(required_metrics)
        not_sent = set(required_metrics)
        sent_metrics = set()

        daemon_coro = MonitoringDaemon(reporter, handles, period).run()
        with run_daemon_in_background(daemon_coro):
            start_time = time.time()
            while time.time() - start_time < 5.0 and not_sent:
                sent_metrics = set(reporter.data)
                not_sent = required_metrics - sent_metrics
                await asyncio.sleep(0.01)

        tap.eq_ok(required_metrics - sent_metrics, set(),
                  'Отправлены все метрики')


@pytest.mark.parametrize('handles,log_message,handle_name', (
    (
        [handle_with_exception],
        'Exception in monitoring handle',
        'tests.scripts.test_monitoring.handle_with_exception'
    ),
    (
        [handle_delay_100_ms],
        'Monitoring handle works too long',
        'tests.scripts.test_monitoring.handle_delay_100_ms'
    ),
))
async def test_log_handle_exception(
        tap: PytestTap,
        caplog: LogCaptureFixture,
        handles: typing.List[typing.Callable],
        log_message: str,
        handle_name: str
):
    reporter = ReporterStub()
    period = 0.01
    with tap, caplog.at_level(logging.WARNING, logger=log.name):
        found_record = None
        daemon_coro = MonitoringDaemon(reporter, handles, period).run()

        with run_daemon_in_background(daemon_coro):
            start_time = time.time()
            while time.time() - start_time < 5.0 and found_record is None:
                for rec in caplog.records:
                    if rec.message == log_message:
                        found_record = rec
                        break
                await asyncio.sleep(0.01)

        tap.ok(found_record is not None, 'Сообщение залоггировано')
        if found_record:
            tap.eq_ok(found_record.log_type, 'monitoring', 'Верный тип лога')
            tap.in_ok(handle_name, found_record.ctx.get('handle', ''),
                      'Верный хендлер')


@pytest.mark.parametrize('handle,required_metrics', (
    (handle2, set(['metric5', 'metric7'])),
))
async def test_log_reporter(tap: PytestTap, caplog: LogCaptureFixture,
                            handle, required_metrics):
    reporter = MetricLogReporter()

    with tap, propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):
        await handle(reporter)

        sent_metrics = set(
            rec.ctx['name']
            for rec in caplog.records
            if rec.name == metrics_log.name and 'name' in rec.ctx
        )

        tap.eq_ok(sent_metrics, required_metrics, 'Отправлены все метрики')
