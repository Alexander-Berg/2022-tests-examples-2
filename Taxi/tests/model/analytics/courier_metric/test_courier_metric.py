import datetime
from easytap.pytest_plugin import PytestTap
from stall.model.analytics.courier_metric import CourierMetric
import tests.dataset as dt


async def test_model_list(tap: PytestTap, dataset: dt):
    store = await dataset.store()
    period = (datetime.date(2020, 5, 1), datetime.date(2020, 5, 3))
    await dataset.courier_metric_daily(_store=store, courier_cnt=3,
                                       period=period)

    cursor = await CourierMetric.list(
        by='full',
        limit=100,
        conditions=(
            'store_id', store.store_id
        ),
        sort=(),
    )
    tap.eq_ok(len(cursor.list), (3 + 1) * 3, 'По 4 метрики в день 3 дня')


async def test_model_save(tap: PytestTap, dataset: dt, now):
    store = await dataset.store()
    some_date = now().date()
    some_time = datetime.datetime(*some_date.timetuple()[:-2])
    metric = CourierMetric(
        date=some_date,
        time=some_time,
        store_id=store.store_id,
    )
    await metric.save()
    await metric.save()

    metric2 = await CourierMetric.load(metric.courier_metric_id)
    tap.ne_ok(metric2, None, 'Метрика была сохранена и загружен')


async def test_model_save_by_chunks(tap: PytestTap, dataset: dt, now):
    store = await dataset.store()
    some_date = now().date()
    some_time = datetime.datetime(*some_date.timetuple()[:-2])
    metric = await CourierMetric(
        date=some_date,
        time=some_time,
        store_id=store.store_id,
        processed=now() - datetime.timedelta(hours=2)
    ).save()

    loaded_metric = await CourierMetric.load(metric.courier_metric_id)
    tap.ok(loaded_metric, 'Метрика была сохранена и загружен')
    tap.eq_ok(loaded_metric.processed, metric.processed,
              'Время обновления сохранено')

    rewrite_metric = await CourierMetric(
        date=some_date,
        time=some_time,
        store_id=store.store_id,
        processed=now() - datetime.timedelta(hours=1)
    ).save()

    await rewrite_metric.save(by='chunks', items=[rewrite_metric])

    metric3 = await CourierMetric.load(metric.courier_metric_id)
    tap.ok(metric3, 'Метрика пересохранена с тем же id')
    tap.eq_ok(metric3.processed, rewrite_metric.processed,
              'Время обновления изменилось на новое')
