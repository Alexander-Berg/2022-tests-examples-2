import random
import datetime

from easytap.pytest_plugin import PytestTap
from asyncpg.exceptions import (
    ConnectionDoesNotExistError
)

from libstall.util import time2time

from scripts.cron.sync_analytics import (
    SyncTask,
    StoreFinder,
)
from stall.model.stash import Stash
from stall.model.analytics.courier_metric import CourierMetric
from stall.model.analytics.store_metric import StoreMetric
from stall.model.greenplum.base import (
    retry,
    GreenplumBaseModel,
    GreenplumConnectionError,
)
from stall.model.greenplum.psv_4wms_metrics import PsvWmsMetrics

import tests.dataset as dt

class PsvWmsMetricsMock(PsvWmsMetrics):
    moc_external_store_id: str = None
    mock_date: datetime.date = None
    mock_processed: datetime.datetime = None

    @classmethod
    async def get_last_update(cls, last_processed):
        # pylint: disable=unused-argument
        return (
            cls.mock_processed,
            cls.mock_date,
            cls.mock_date,
        )

    @classmethod
    def get_couriers(cls):
        return [12345, 23456], ['Courier1', None]

    @classmethod
    async def fetch_all_metrics(
            cls,
            min_date: datetime.date,
            max_date: datetime.date,
    ):
        # pylint: disable=unused-argument
        store_metric = PsvWmsMetrics(
            dat=max_date,
            hr=datetime.datetime(*max_date.timetuple()[:-2]),
            place_id=int(cls.moc_external_store_id),
            s_cluster=2,
            s_factor=3,
            compensations={
                'not_delivered': 3,
                'bad_product': 5,
                'overcooked': 7,
            }
        )
        courier_metrics = [
            PsvWmsMetrics(
                dat=max_date,
                hr=datetime.datetime(*max_date.timetuple()[:-2]),
                place_id=int(cls.moc_external_store_id),
                courier_id=courier_id,
                courier_name=courier_name,
            )
            for courier_id, courier_name in zip(*cls.get_couriers())
        ]
        executer_metrics = [
            PsvWmsMetrics(
                dat=max_date,
                hr=datetime.datetime(*max_date.timetuple()[:-2]),
                place_id=int(cls.moc_external_store_id),
                storekeeper_fullname=executer_name,
            )
            for executer_name
            in ['Executer1', 'Executer2']
        ]
        yield store_metric, courier_metrics, executer_metrics


async def test_sync_analytics_values(tap: PytestTap, dataset: dt, now):
    # pylint: disable=too-many-locals
    class SyncTaskMock(SyncTask):
        PsvWmsMetrics = PsvWmsMetricsMock

    with tap.plan(9, '???????????????? ???????????????? ?????????? ??????????????????????????'):
        external_id = str(random.randint(10000000, 99999999))
        store = await dataset.store(external_id=external_id)
        some_date = datetime.date(2019, 2, 3)

        PsvWmsMetricsMock.mock_processed = (
            now() + datetime.timedelta(hours=2)
        )
        PsvWmsMetricsMock.mock_date = some_date
        PsvWmsMetricsMock.moc_external_store_id = external_id
        await StoreFinder.clear_cache()
        await SyncTaskMock().sync_cycle()

        cursor = await CourierMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
                ('external_courier_id', ''),
            )
        )
        tap.eq_ok(len(cursor.list), 1, '1 ???????????????????? ?????????????? ?????? ??????????')
        with cursor.list[0] as metric:
            tap.eq_ok(metric.store_cluster, 2, 'store_cluster')
            tap.eq_ok(metric.store_factor, 3, 'store_factor')

        cursor = await StoreMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
                ('external_executer_id', ''),
            )
        )
        tap.eq_ok(len(cursor.list), 1, '1 ???????????????????? ?????????????? ?????? ??????????')
        with cursor.list[0] as metric:
            tap.eq_ok(metric.store_cluster, 2, 'store_cluster')
            tap.eq_ok(metric.store_factor, 3, 'store_factor')
            tap.eq_ok(
                metric.compensations['not_delivered'],
                3,
                'not_delivered'
            )
            tap.eq_ok(metric.compensations['bad_product'], 5, 'bad_product')
            tap.eq_ok(metric.compensations['overcooked'], 7, 'overcooked')

async def test_sync_analytics_courier_id(tap: PytestTap, dataset: dt, now):
    # pylint: disable=too-many-locals

    with tap.plan(3, '???????????????? ???????????????? ?????????? ??????????????????????????'):
        external_id = str(random.randint(10000000, 99999999))
        store = await dataset.store(external_id=external_id)

        external_courier_id = random.randint(10000000, 99999999)
        courier = await dataset.courier(
            store=store,
            vars={'external_ids': {'eats': str(external_courier_id)}},
        )
        some_date = datetime.date(2019, 2, 3)

        class PsvWmsMetricsCouriersMock(PsvWmsMetricsMock):
            @classmethod
            def get_couriers(cls):
                return [external_courier_id, 12345], ['Courier1', None]

        class SyncTaskMock(SyncTask):
            PsvWmsMetrics = PsvWmsMetricsCouriersMock

        PsvWmsMetricsMock.mock_processed = (
            now() + datetime.timedelta(hours=2)
        )
        PsvWmsMetricsMock.mock_date = some_date
        PsvWmsMetricsMock.moc_external_store_id = external_id
        await StoreFinder.clear_cache()
        await SyncTaskMock().sync_cycle()

        cursor = await CourierMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
                ('external_courier_id', courier.vars('external_ids.eats')),
            )
        )
        tap.eq_ok(len(cursor.list), 1, '???????? ?????????????? ?????? ??????????????')
        with cursor.list[0] as metric:
            tap.eq_ok(metric.courier_id, courier.courier_id, 'courier id')
            tap.eq_ok(metric.courier_name, 'Courier1', 'courier name')


async def test_sync_analytics(tap: PytestTap, dataset: dt, uuid, now):
    # pylint: disable=too-many-locals
    class SyncTaskMock(SyncTask):
        PsvWmsMetrics = PsvWmsMetricsMock

    with tap.plan(11, '????????????????, ?????? ?????????????? ???????????????????????????????? ?? ??????????????????'):
        external_id = str(random.randint(10000000, 99999999))
        store = await dataset.store(external_id=external_id)
        some_date = datetime.date(2019, 2, 3)
        period = (some_date, some_date)

        couriers = [
            await dataset.courier(external_id=uuid(), store=store)
            for _ in range(4)
        ] + [
            await dataset.courier(external_id='12345', store=store)
        ]
        await dataset.courier_metric_daily(
            _store=store,
            period=period,
            couriers=[it.courier_id for it in couriers]
        )

        executers = [
            await dataset.user(fullname=uuid(), store=store, role='executer')
            for _ in range(4)
        ] + [
            await dataset.user(fullname='Executer1', store=store,
                               role='executer')
        ]
        await dataset.store_metric_daily(
            _store=store,
            period=period,
            executers=[it.user_id for it in executers]
        )

        courier_cursor = await CourierMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
            )
        )
        tap.ok(
            len(courier_cursor.list) > 0,
            f'???????????????????? ?????????????? ???????????????????? ???? ???????? {some_date}'
        )

        store_cursor = await StoreMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
            )
        )
        tap.ok(
            len(store_cursor.list) > 0,
            f'?????????????????? ?????????????? ???????????????????? ???? ???????? {some_date}'
        )

        processed = max(
            it.processed
            for it
            in courier_cursor.list + store_cursor.list
        )
        tap.ok(processed, '?? ???????????? ?????????????? ???????? ????????????????????')

        PsvWmsMetricsMock.mock_processed = (
            now() + datetime.timedelta(hours=2)
        )
        PsvWmsMetricsMock.mock_date = some_date
        PsvWmsMetricsMock.moc_external_store_id = external_id
        await StoreFinder.clear_cache()
        await SyncTaskMock().sync_cycle()

        cursor = await CourierMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
                ('external_courier_id', ''),
            )
        )

        tap.eq_ok(len(cursor.list), 1, '1 ???????????????????? ?????????????? ?????? ??????????')
        tap.ok(
            all(it.processed > processed for it in cursor.list),
            '???????????????????? ?????????????? ???? ?????????? ????????????????????????. '
            '???????? ???????????????????? ????????????????????'
        )
        cursor = await CourierMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
                ('external_courier_id', '!=', ''),
            )
        )
        tap.eq_ok(len(cursor.list), 2, '???? ?????????????? ?????? ?????????????? ???? 2 ????????????????.')
        tap.ok(
            all(it.processed > processed for it in cursor.list),
            '???????????????????? ?????????????? ???? ???????????????? ????????????????????????.'
            '???????? ???????????????????? ????????????????????'
        )

        cursor = await StoreMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
                ('external_executer_id', '')
            )
        )
        tap.eq_ok(len(cursor.list), 1, '???????? ?????????????????? ?????????????? ?????? ??????????.')
        tap.ok(
            all(it.processed > processed for it in cursor.list),
            '?????????????????? ?????????????? ???? ?????????? ????????????????????????. '
            '???????? ???????????????????? ????????????????????'
        )
        cursor = await StoreMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
                ('external_executer_id', '!=', '')
            )
        )

        tap.eq_ok(len(cursor.list), 2, '???? ?????????????? ?????? ?????????????? ????????????????????.')
        tap.ok(
            all(it.processed > processed for it in cursor.list),
            '?????????????????? ?????????????? ???? ?????????????????????? ????????????????????????.'
            '???????? ???????????????????? ????????????????????'
        )

class PsvWmsMetricsStoreException(PsvWmsMetricsMock):
    mock_date: datetime.date = None

    @classmethod
    async def get_last_update(cls, last_processed):
        # pylint: disable=unused-argument
        return (
            datetime.datetime(*cls.mock_date.timetuple()[:-2]),
            cls.mock_date,
            cls.mock_date,
        )
    @classmethod
    async def fetch_all_metrics(
            cls,
            min_date: datetime.date,
            max_date: datetime.date,
    ):
        # pylint: disable=unused-argument
        yield None, [], []
        raise GreenplumConnectionError('Something went wrong')


async def test_sync_analytics_failed(tap: PytestTap, dataset: dt):
    class SyncTaskMock(SyncTask):
        PsvWmsMetrics = PsvWmsMetricsStoreException

    with tap.plan(8, '????????????????, ?????? ?????????????? ????????????????????????????????'):
        external_id = str(random.randint(10000000, 99999999))
        store = await dataset.store(external_id=external_id)
        some_date = datetime.date(2019, 2, 3)
        period = (some_date, some_date)
        await dataset.courier_metric_daily(_store=store, period=period,
                                           courier_cnt=5)
        await dataset.store_metric_daily(_store=store, period=period,
                                         executer_cnt=5)

        courier_cursor = await CourierMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
                ('external_courier_id', ''),
            )
        )
        tap.ok(
            len(courier_cursor.list) > 0,
            f'???????????????????? ?????????????? ???????????????????? ???? ???????? {some_date}'
        )

        store_cursor = await StoreMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
            )
        )
        tap.ok(
            len(store_cursor.list) > 0,
            f'?????????????????? ?????????????? ???????????????????? ???? ???????? {some_date}'
        )

        processed = max(
            it.processed
            for it
            in courier_cursor.list + store_cursor.list
        )
        tap.ok(processed, '?? ???????????? ?????????? ???????? ????????????????????')

        PsvWmsMetricsStoreException.mock_date = some_date
        await StoreFinder.clear_cache()
        with tap.raises(GreenplumConnectionError):
            await SyncTaskMock().sync_cycle()

        cursor = await CourierMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
                ('external_courier_id', ''),
            )
        )

        tap.ok(
            all(it.processed <= processed for it in cursor.list),
            '???????????????????? ?????????????? ???? ?????????? ???? ????????????????????.'
            '???????? ???????????????????? ???? ????????????????????'
        )
        cursor = await CourierMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
                ('external_courier_id', '!=', ''),
            )
        )
        tap.ok(
            all(it.processed <= processed for it in cursor.list),
            '???????????????????? ?????????????? ???? ???????????????? ???? ????????????????????.'
            '???????? ???????????????????? ???? ????????????????????'
        )

        store_cursor = await StoreMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
                ('external_executer_id', '')
            )
        )

        tap.ok(
            all(it.processed <= processed for it in store_cursor.list),
            '?????????????????? ?????????????? ???? ?????????? ???? ????????????????????.'
            '???????? ???????????????????? ???? ????????????????????'
        )
        store_cursor = await StoreMetric.list(
            by='full',
            conditions=(
                ('date', some_date),
                ('store_id', store.store_id),
                ('external_executer_id', '!=', '')
            )
        )
        tap.ok(
            all(it.processed <= processed for it in store_cursor.list),
            '?????????????????? ?????????????? ???? ?????????????????????? ???? ????????????????????'
            '???????? ???????????????????? ???? ????????????????????'
        )


async def test_retry(tap):
    # pylint: disable=unused-argument
    async def without_retry(cls, array):
        array.append(True)
        raise ConnectionDoesNotExistError()

    @retry(4, 0.00001)
    async def with_retry(cls, array):
        array.append(True)
        raise ConnectionDoesNotExistError()

    without_retry_count = []
    with tap.raises(ConnectionDoesNotExistError):
        await without_retry(GreenplumBaseModel, without_retry_count)
    tap.eq_ok(len(without_retry_count), 1, '?????? retry ?????????????? ?????????????? 1 ??????')

    with_retry_count = []
    with tap.raises(GreenplumConnectionError):
        await with_retry(GreenplumBaseModel, with_retry_count)
    tap.eq_ok(len(with_retry_count), 4, '?? retry ?????????????? ?????????????? 4 ????????')


async def test_sync_cycle(tap, uuid, now):
    # pylint: disable=too-many-locals
    class PsvWmsMetricsMockLastUpdate(PsvWmsMetrics):
        mock_processed: datetime.datetime = None

        @classmethod
        async def get_last_update(cls, last_processed):
            return (
                cls.mock_processed,
                cls.mock_processed.date(),
                cls.mock_processed.date(),
            )
        @classmethod
        async def fetch_all_metrics(
                cls,
                min_date: datetime.date,
                max_date: datetime.date,
        ):
            # pylint: disable=unused-argument
            yield None, [], []

    class SyncTaskMock(SyncTask):
        stash_prefix = uuid()
        PsvWmsMetrics = PsvWmsMetricsMockLastUpdate

    with tap.plan(4, '????????????????, ?????? ?????????????????????????? ?????????????? ?? ????????????????????'):
        stash = await Stash.load(
            f'{SyncTaskMock.stash_prefix}_gp_processed',
            by='conflict',
        )
        tap.eq_ok(stash, None, '')

        processed1 = now() - datetime.timedelta(hours=4)
        processed2 = now() - datetime.timedelta(hours=2)

        PsvWmsMetricsMockLastUpdate.mock_processed = processed1
        await SyncTaskMock.sync_cycle()

        stash = await Stash.load(
            f'{SyncTaskMock.stash_prefix}_gp_processed',
            by='conflict',
        )
        tap.ok(
            time2time(stash.value.get('processed')) > processed1,
            '?????????? ???????????????????? ??????????????????????'
        )
        tap.ok(
            time2time(stash.value.get('processed')) < processed2,
            '?????????? ???????????????????? ???????????? ????????????????????'
        )

        PsvWmsMetricsMockLastUpdate.mock_processed = processed2
        await SyncTaskMock.sync_cycle()

        stash = await Stash.load(
            f'{SyncTaskMock.stash_prefix}_gp_processed',
            by='conflict',
        )
        tap.ok(
            time2time(stash.value.get('processed')) > processed2,
            '?????????? ???????????????????? ????????????????????'
        )
