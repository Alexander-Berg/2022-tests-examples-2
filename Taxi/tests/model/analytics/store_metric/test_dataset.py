import datetime
from easytap.pytest_plugin import PytestTap
import tests.dataset as dt


async def test_dataset_default(tap: PytestTap, dataset: dt, now):
    _now = now()
    metric_date = datetime.date(_now.year, _now.month, _now.day)
    metrics = await dataset.store_metric_daily()
    tap.eq_ok(len(metrics), 2, 'Одна метрика для стора. Одна для кладовщика')
    with metrics[0] as m:
        tap.ok(m.store_id, 'Лавка задана')
        tap.eq_ok(m.executer_id, None, 'Кладовщик не задан')
        tap.eq_ok(m.date, metric_date, 'Дата верная')

    with metrics[1] as m:
        tap.ok(m.store_id, 'Лавка задана')
        tap.ok(m.executer_name, 'Имя кладовщика задано')
        tap.ok(m.external_executer_id, 'ИД кладовщика из еды')
        tap.ok(m.executer_id, 'Кладовщик задан')
        tap.eq_ok(m.date, metric_date, 'Дата верная')


async def test_dataset_period(tap: PytestTap, dataset: dt):
    period = (datetime.date(2020, 1, 12), datetime.date(2020, 2, 2))
    metrics = await dataset.store_metric_daily(period=period)
    tap.eq_ok(len(metrics), 44, 'Одна метрика для стора. Одна для кладовщика')


async def test_dataset_period_str(tap: PytestTap, dataset: dt):
    period = ('2020-01-12', '2020-02-02')
    metrics = await dataset.store_metric_daily(period=period)
    tap.eq_ok(len(metrics), 44, 'Одна метрика для стора. Одна для кладовщика')


async def test_dataset_store(tap: PytestTap, dataset: dt):
    store = await dataset.store()
    metrics = await dataset.store_metric_daily(_store=store)
    with metrics[0] as m:
        tap.eq(m.store_id, store.store_id, 'Лавка установлена')

    store2 = await dataset.store()
    metrics = await dataset.store_metric_daily(_store=store2.store_id)
    with metrics[0] as m:
        tap.eq(m.store_id, store2.store_id, 'Лавка установлена')


async def test_dataset_executer_cnt(tap: PytestTap, dataset: dt):
    metrics = await dataset.store_metric_daily(executer_cnt=5)
    tap.eq_ok(len(metrics), 6, 'Одна метрика для стора. 5 для кладовщика')


async def test_dataset_values(tap: PytestTap, dataset: dt):
    store_metric, *metrics = await dataset.store_metric_daily(
        executer_cnt=5
    )
    _sum = lambda arr, field: sum(getattr(it, field, None) or 0 for it in arr)

    tap.eq_ok(len(metrics), 5, '5 записей для кладовщиков')
    tap.eq_ok(store_metric.grand_total_cnt,
              _sum(metrics, 'grand_total_cnt'),
              'grand_total_cnt')
    tap.eq_ok(store_metric.success_delivered_cnt,
              _sum(metrics, 'success_delivered_cnt'),
              'success_delivered_cnt')
    tap.eq_ok(store_metric.overall_time,
              _sum(metrics, 'overall_time'),
              'overall_time')
    tap.eq_ok(store_metric.overall_items,
              _sum(metrics, 'overall_items'),
              'overall_items')

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

    tap.eq_ok(store_metric.complaints_10_cnt,
              _sum(metrics, 'complaints_10_cnt'),
              'complaints_10_cnt')
    tap.eq_ok(store_metric.complaints_all_cnt,
              _sum(metrics, 'complaints_all_cnt'),
              'complaints_all_cnt')

    tap.ok(store_metric.complaints_all_cnt >= store_metric.complaints_10_cnt,
           'Всего жалоб больше чем с компенсацией')

    tap.ne_ok(store_metric.recount_writeoffs_cost_lcy, None, 'Недостача')
    tap.ne_ok(store_metric.damage_writeoffs_cost_lcy, None, 'Брак')
    tap.ne_ok(store_metric.refund_writeoffs_cost_lcy, None, 'Возврат')
    tap.ne_ok(store_metric.check_valid_writeoffs_cost_lcy, None, 'КСГ')

