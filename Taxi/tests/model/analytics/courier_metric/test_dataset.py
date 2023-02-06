import datetime
from easytap.pytest_plugin import PytestTap
import tests.dataset as dt


async def test_dataset_default(tap: PytestTap, dataset: dt, now):
    _now = now()
    metric_date = datetime.date(_now.year, _now.month, _now.day)
    metrics = await dataset.courier_metric_daily()
    tap.eq_ok(len(metrics), 2, 'Одна метрика для стора. Одна для курьера')
    with metrics[0] as m:
        tap.ok(m.store_id, 'Лавка задана')
        tap.eq_ok(m.courier_id, None, 'Курьер не задан')
        tap.eq_ok(m.date, metric_date, 'Дата верная')

    with metrics[1] as m:
        tap.ok(m.store_id, 'Лавка задана')
        tap.ok(m.courier_id, 'Курьер задан')
        tap.ok(m.external_courier_id, 'ИД курьера из Еды')
        tap.ok(m.courier_name, 'Имя курьера')
        tap.eq_ok(m.date, metric_date, 'Дата верная')


async def test_dataset_period(tap: PytestTap, dataset: dt):
    period = (datetime.date(2020, 1, 12), datetime.date(2020, 2, 2))
    metrics = await dataset.courier_metric_daily(period=period)
    tap.eq_ok(len(metrics), 44, 'Одна метрика для стора. Одна для курьера')


async def test_dataset_period_str(tap: PytestTap, dataset: dt):
    period = ('2020-01-12', '2020-02-02')
    metrics = await dataset.courier_metric_daily(period=period)
    tap.eq_ok(len(metrics), 44, 'Одна метрика для стора. Одна для курьера')


async def test_dataset_store(tap: PytestTap, dataset: dt):
    store = await dataset.store()
    metrics = await dataset.courier_metric_daily(_store=store)
    with metrics[0] as m:
        tap.eq(m.store_id, store.store_id, 'Лавка установлена')

    store2 = await dataset.store()
    metrics = await dataset.courier_metric_daily(_store=store2.store_id)
    with metrics[0] as m:
        tap.eq(m.store_id, store2.store_id, 'Лавка установлена')


async def test_dataset_courier_cnt(tap: PytestTap, dataset: dt):
    metrics = await dataset.courier_metric_daily(courier_cnt=5)
    tap.eq_ok(len(metrics), 6, 'Одна метрика для стора. 5 для курьера')


async def test_dataset_values(tap: PytestTap, dataset: dt):
    store_metric, *metrics = await dataset.courier_metric_daily(courier_cnt=5)
    _sum = lambda arr, field: sum(getattr(it, field, None) or 0 for it in arr)

    tap.eq_ok(len(metrics), 5, '5 записей для курьера')
    tap.eq_ok(store_metric.grand_total_cnt,
              _sum(metrics, 'grand_total_cnt'),
              'grand_total_cnt')
    tap.eq_ok(store_metric.success_delivered_cnt,
              _sum(metrics, 'success_delivered_cnt'),
              'success_delivered_cnt')
    tap.eq_ok(store_metric.success_delivered_cnt_10,
              _sum(metrics, 'success_delivered_cnt_10'),
              'success_delivered_cnt_10')
    tap.eq_ok(store_metric.success_delivered_cnt_25,
              _sum(metrics, 'success_delivered_cnt_25'),
              'success_delivered_cnt_25')
    tap.eq_ok(store_metric.success_delivered_cnt_40,
              _sum(metrics, 'success_delivered_cnt_40'),
              'success_delivered_cnt_40')
    tap.ok(store_metric.grand_total_cnt > store_metric.success_delivered_cnt,
           'Всего заказов больше чем успешных')
    tap.ok((store_metric.success_delivered_cnt
            > store_metric.success_delivered_cnt_10),
           'Успешных заказов больше чем с опозданием на 10 минут')
    tap.ok((store_metric.success_delivered_cnt
            > store_metric.success_delivered_cnt_25),
           'Успешных заказов больше чем с опозданием на 25 минут')
    tap.ok((store_metric.success_delivered_cnt
            > store_metric.success_delivered_cnt_40),
           'Успешных заказов больше чем с опозданием на 40 минут')

    tap.eq_ok(store_metric.cte_dur_sec,
              _sum(metrics, 'cte_dur_sec'),
              'cte_dur_sec')
    tap.eq_ok(store_metric.fact_shift_dur_sec,
              _sum(metrics, 'fact_shift_dur_sec'),
              'fact_shift_dur_sec')
    tap.eq_ok(store_metric.cur_dur_sec_plan,
              _sum(metrics, 'cur_dur_sec_plan'),
              'cur_dur_sec_plan')
    tap.eq_ok(store_metric.cur_dur_sec_not_start,
              _sum(metrics, 'cur_dur_sec_not_start'),
              'cur_dur_sec_not_start')
    tap.eq_ok(store_metric.early_leaving_dur_sec,
              _sum(metrics, 'early_leaving_dur_sec'),
              'early_leaving_dur_sec')
    tap.eq_ok(store_metric.lateness_dur_sec,
              _sum(metrics, 'lateness_dur_sec'),
              'lateness_dur_sec')
    tap.eq_ok(store_metric.shift_dur_sec_work_promise,
              _sum(metrics, 'shift_dur_sec_work_promise'),
              'shift_dur_sec_work_promise')
    tap.eq_ok(store_metric.shift_dur_sec_work_capability,
              _sum(metrics, 'shift_dur_sec_work_capability'),
              'shift_dur_sec_work_capability')

    tap.eq_ok(store_metric.cpo_orders,
              _sum(metrics, 'cpo_orders'),
              'cpo_orders')
    tap.eq_ok(store_metric.cpo_cost,
              _sum(metrics, 'cpo_cost'),
              'cpo_cost')
    tap.eq_ok(store_metric.batch_cnt,
              _sum(metrics, 'batch_cnt'),
              'batch_cnt')
    tap.eq_ok(store_metric.fallback_cnt,
              _sum(metrics, 'fallback_cnt'),
              'fallback_cnt')
    tap.eq_ok(store_metric.surge_cnt,
              _sum(metrics, 'surge_cnt'),
              'surge_cnt')

    tap.eq_ok(store_metric.complaints_10_cnt,
              _sum(metrics, 'complaints_10_cnt'),
              'complaints_10_cnt')
    tap.eq_ok(store_metric.complaints_all_cnt,
              _sum(metrics, 'complaints_all_cnt'),
              'complaints_all_cnt')

    tap.ok(store_metric.complaints_all_cnt >= store_metric.complaints_10_cnt,
           'Всего жалоб больше чем с компенсацией')
