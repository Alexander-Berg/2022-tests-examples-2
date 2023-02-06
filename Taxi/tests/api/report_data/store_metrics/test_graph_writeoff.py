import datetime
import tests.dataset as dt
from stall.api.report_data.store_metrics.graph_writeoffs import (
    StoreMetricView,
    split_period_by_months
)

def test_split_period(tap):
    periods = split_period_by_months(
        datetime.date(2021, 1, 10),
        datetime.date(2021, 1, 10),
    )
    tap.eq_ok(
        list(periods),
        [
            (datetime.date(2021, 1, 10), datetime.date(2021, 1, 10))
        ],
        ''
    )

    periods = split_period_by_months(
        datetime.date(2021, 1, 10),
        datetime.date(2021, 2, 1),
    )
    tap.eq_ok(
        list(periods),
        [
            (datetime.date(2021, 1, 10), datetime.date(2021, 1, 31)),
            (datetime.date(2021, 2, 1), datetime.date(2021, 2, 1)),
        ],
        ''
    )

    periods = split_period_by_months(
        datetime.date(2020, 11, 10),
        datetime.date(2021, 1, 2),
    )
    tap.eq_ok(
        list(periods),
        [
            (datetime.date(2020, 11, 10), datetime.date(2020, 11, 30)),
            (datetime.date(2020, 12, 1), datetime.date(2020, 12, 31)),
            (datetime.date(2021, 1, 1), datetime.date(2021, 1, 2)),
        ],
        ''
    )


async def test_graph_invalid(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')
    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            },
            'detalization': 'day',
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')

    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'store_id': store.store_id,
            'detalization': 'day',
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')
    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            },
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')


async def test_graph_invalid_period(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2010, 5, 1),
            },
            'detalization': 'day',
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'ER_BAD_REQUEST')


async def test_list_access(api, tap, dataset: dt):
    store = await dataset.store()
    other_store = await dataset.store()
    user = await dataset.user(store=store, role='executer')

    t = await api(user=user)
    request_body = {
        'store_id': store.store_id,
        'period': {
            'begin': datetime.date(2020, 5, 5),
            'end': datetime.date(2020, 5, 5),
        },
        'detalization': 'day',
    }
    with tap.subtest(3, 'Ручка недоступна без пермита') as taps:
        t.tap = taps
        await t.post_ok(
            'api_report_data_store_metrics_graph_writeoffs',
            json=request_body
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

    with user.role as role:
        role.add_permit('store_analytics', True)

        with tap.subtest(3, 'Пермит есть - ручка доступна') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_store_metrics_graph_writeoffs',
                json=request_body
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        with tap.subtest(3, 'Ручка недоступна для другой лавки') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_store_metrics_graph_writeoffs',
                json={
                    'store_id': other_store.store_id,
                    'period': {
                        'begin': datetime.date(2020, 5, 5),
                        'end': datetime.date(2020, 5, 5),
                    },
                    'detalization': 'day',
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


async def test_graph_empty(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            },
            'detalization': 'day',
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    t.json_is('graphs.writeoff', [])
    t.json_has('aggregations')
    t.json_is('aggregations.writeoff.kpi', None)
    t.json_is('aggregations.writeoff.check_valid', None)
    t.json_is('aggregations.writeoff.damage', None)
    t.json_is('aggregations.writeoff.refund', None)
    t.json_is('aggregations.writeoff.recount', None)


async def test_graph_two_days(api, dataset: dt, uuid):
    cluster = await dataset.cluster()
    store = await dataset.store(external_id=uuid(), cluster=cluster)
    await dataset.writeoff_limit(
        date=datetime.date(2020, 5, 1),
        cluster=cluster,
        factor=15,
        check_valid_max=20.0,
        damage_max=None,
        refund_max=0.5001,
        recount_min=-0.123,
        recount_max=0.123,
    )
    await dataset.StoreMetric(
        date=datetime.date(2020, 5, 1),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        store_factor=15,
        store_cluster=14,
        recount_writeoffs_cost_lcy=40.0,
        damage_writeoffs_cost_lcy=120.0,
        refund_writeoffs_cost_lcy=160.0,
        check_valid_writeoffs_cost_lcy=3000.0,
        gross_revenue_w_pur_cost_lcy=20000.0,
    ).save()
    await dataset.StoreMetric(
        date=datetime.date(2020, 5, 2),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        store_factor=15,
        store_cluster=14,
        recount_writeoffs_cost_lcy=300.0,
        damage_writeoffs_cost_lcy=500.0,
        refund_writeoffs_cost_lcy=701.12,
        check_valid_writeoffs_cost_lcy=2000.0,
        gross_revenue_w_pur_cost_lcy=10000.0,
    ).save()


    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 1),
                'end': datetime.date(2020, 5, 2),
            },
            'detalization': 'day',
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')

    t.json_has('graphs.writeoff.0.value')
    t.json_has('graphs.writeoff.1.value')
    t.json_has('graphs.writeoff.0.details.kpi.value')
    t.json_has('graphs.writeoff.1.details.kpi.value')

    # 100 * (
    #     recount_writeoffs_cost_lcy
    #     + damage_writeoffs_cost_lcy
    #     + refund_writeoffs_cost_lcy
    #     + check_valid_writeoffs_cost_lcy
    # ) / gross_revenue_w_pur_cost_lcy
    #
    t.json_is('graphs.writeoff.1.details.total.value', round(
        100 * (300.0 + 500.0 + 701.12 + 2000.0) / 10000.0,
        2
    ))

    # recount_writeoffs_cost_lcy / gross_revenue_w_pur_cost_lcy
    t.json_is('graphs.writeoff.1.details.recount.value',
              round(100 * 300.0 / 10000.0, 2))
    t.json_is('graphs.writeoff.1.details.recount.threshold_min', -0.12)
    t.json_is('graphs.writeoff.1.details.recount.threshold_max', 0.12)
     # damage_writeoffs_cost_lcy / gross_revenue_w_pur_cost_lcy
    t.json_is('graphs.writeoff.1.details.damage.value',
              round(100 * 500.0 / 10000.0, 2))
    t.json_is('graphs.writeoff.1.details.damage.threshold_max', None)
     # refund_writeoffs_cost_lcy / gross_revenue_w_pur_cost_lcy
    t.json_is('graphs.writeoff.1.details.refund.value',
              round(100 * 701.12 / 10000.0, 3))
    t.json_is('graphs.writeoff.1.details.refund.threshold_max', 0.5)
     # check_valid_writeoffs_cost_lcy / gross_revenue_w_pur_cost_lcy
    t.json_is('graphs.writeoff.1.details.check_valid.value',
              round(100 * 2000.0 / 10000.0, 2))
    t.json_is('graphs.writeoff.1.details.check_valid.threshold_max', 20.0)
    t.json_is('graphs.writeoff.0.date', '2020-05-01')
    t.json_hasnt('graphs.writeoff.0.threshold')

    t.json_has('aggregations')
    t.json_is('aggregations.writeoff.recount',
              round(100 * (40.0 + 300.0) / (20000.0 + 10000.0), 2))
    t.json_is('aggregations.writeoff.damage',
              round(100 * (120.0 + 500.0) / (20000.0 + 10000.0), 2))
    t.json_is('aggregations.writeoff.refund',
              round(100 * (160.0 + 700.0) / (20000.0 + 10000.0), 2))
    t.json_is('aggregations.writeoff.check_valid',
              round(100 * (3000.0 + 2000.0) / (20000.0 + 10000.0), 2))
    t.json_has('aggregations.writeoff.kpi')


async def test_graph_in_diff_months(api, dataset: dt, uuid):
    cluster = await dataset.cluster()
    store = await dataset.store(external_id=uuid(), cluster=cluster)
    await dataset.StoreMetric(
        date=datetime.date(2020, 3, 1),
        time=datetime.datetime(2020, 3, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        recount_writeoffs_cost_lcy=10.0,
        gross_revenue_w_pur_cost_lcy=12.0,
    ).save()
    await dataset.StoreMetric(
        date=datetime.date(2020, 4, 1),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        recount_writeoffs_cost_lcy=10.0,
        gross_revenue_w_pur_cost_lcy=23.0,
    ).save()
    await dataset.StoreMetric(
        date=datetime.date(2020, 5, 1),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        recount_writeoffs_cost_lcy=10.0,
        gross_revenue_w_pur_cost_lcy=34.0,
    ).save()


    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 3, 1),
                'end': datetime.date(2020, 5, 1),
            },
            'detalization': 'month',
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('aggregations')
    t.json_is(
        'aggregations.writeoff.recount',
        round(100 * ((10.0 / 12.0) + (10.0 / 23.0) + (10.0 / 34.0)) / 3, 2)
    )


async def test_graph_zero_data(api, dataset: dt, tap):
    period = (
        datetime.date(2020, 5, 1),
        datetime.date(2020, 5, 1)
    )
    store = await dataset.store()
    metrics = await dataset.store_metric_daily(_store=store, period=period,
                                               executer_cnt=0)
    tap.eq_ok(len(metrics), 1, 'Метрики сгенерированы на 1 день')
    with metrics[0] as m:
        m.recount_writeoffs_cost_lcy = 0.0
        m.damage_writeoffs_cost_lcy = 0.0
        m.refund_writeoffs_cost_lcy = 0.0
        m.check_valid_writeoffs_cost_lcy = 0.0
        m.gross_revenue_w_pur_cost_lcy = 0.0
        await m.save()

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 1),
                'end': datetime.date(2020, 5, 1),
            },
            'detalization': 'day',
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')

    t.json_is('graphs.writeoff.0.date', '2020-05-01')
    t.json_is('graphs.writeoff.0.value', None)
    t.json_is('graphs.writeoff.0.details.kpi.value', None)
    t.json_is('graphs.writeoff.0.details.total.value', None)
    t.json_is('graphs.writeoff.0.details.recount.value', None)
    t.json_is('graphs.writeoff.0.details.recount.threshold_min', None)
    t.json_is('graphs.writeoff.0.details.recount.threshold_max', None)
    t.json_is('graphs.writeoff.0.details.damage.value', None)
    t.json_is('graphs.writeoff.0.details.damage.threshold_max', None)
    t.json_is('graphs.writeoff.0.details.refund.value', None)
    t.json_is('graphs.writeoff.0.details.refund.threshold_max', None)
    t.json_is('graphs.writeoff.0.details.check_valid.value', None)
    t.json_is('graphs.writeoff.0.details.check_valid.threshold_max', None)

    t.json_has('aggregations')
    t.json_is('aggregations.writeoff.check_valid', None)
    t.json_is('aggregations.writeoff.damage', None)
    t.json_is('aggregations.writeoff.refund', None)
    t.json_is('aggregations.writeoff.recount', None)
    t.json_is('aggregations.writeoff.kpi', None)

async def test_graph_week(api, dataset: dt, tap):
    period = (
        datetime.date(2020, 4, 27), # Понедельник
        datetime.date(2020, 5, 4) # Понедельник
    )
    store = await dataset.store()
    metrics = await dataset.store_metric_daily(_store=store, period=period)
    tap.eq_ok(len(metrics), 16, 'Метрики сгенерированы на 2 неполные недели')

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 4, 27),
                'end': datetime.date(2020, 5, 3),
            },
            'detalization': 'week'
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    tap.eq_ok(len(t.res['json']['graphs']['writeoff']), 2,
              'График writeoff за 1 неделю')
    t.json_is('graphs.writeoff.0.date', '2020-04-27')
    t.json_is('graphs.writeoff.1.date', '2020-05-01')

    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 1),
                'end': datetime.date(2020, 5, 10),
            },
            'detalization': 'week'
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')

    tap.eq_ok(len(t.res['json']['graphs']['writeoff']), 2,
              'График writeoff за 2 недели')
    t.json_is('graphs.writeoff.0.date', '2020-05-01')
    t.json_is('graphs.writeoff.1.date', '2020-05-04')


async def test_graph_month(api, dataset: dt, tap):
    period = (
        datetime.date(2020, 5, 4), # Понедельник
        datetime.date(2020, 6, 18)
    )
    store = await dataset.store()
    metrics = await dataset.store_metric_daily(_store=store, period=period)
    tap.eq_ok(len(metrics), 92, 'Метрики сгенерированы на 2 месяца')

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 4),
                'end': datetime.date(2020, 5, 18),
            },
            'detalization': 'month'
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    tap.eq_ok(len(t.res['json']['graphs']['writeoff']), 1,
              'График writeoff за 1 месяц')
    t.json_is('graphs.writeoff.0.date', '2020-05-04')

    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 1),
                'end': datetime.date(2020, 6, 20),
            },
            'detalization': 'month'
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    tap.eq_ok(len(t.res['json']['graphs']['writeoff']), 2,
              'График writeoff за 2 недели')
    t.json_is('graphs.writeoff.0.date', '2020-05-01')
    t.json_is('graphs.writeoff.1.date', '2020-06-01')

async def test_graph_month_by_days(api, dataset: dt, tap):
    period = (
        datetime.date(2020, 5, 1),
        datetime.date(2020, 5, 31)
    )
    store = await dataset.store()
    metrics = await dataset.store_metric_daily(_store=store, period=period)
    tap.eq_ok(len(metrics), 62, 'Метрики сгенерированы на 2 месяца')

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_graph_writeoffs',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 1),
                'end': datetime.date(2020, 5, 31),
            },
            'detalization': 'day'
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    tap.eq_ok(len(t.res['json']['graphs']['writeoff']), 31,
              'График writeoff за 1 месяц')
    t.json_is('graphs.writeoff.0.date', '2020-05-01')
    t.json_is('graphs.writeoff.30.date', '2020-05-31')

async def test_kpi(tap, dataset: dt, uuid):
    writeoff_limit = dataset.WriteoffLimit(
        date=datetime.date(2020, 5, 1),
        cluster_id=uuid(),
        factor=15,
        recount_min=-0.2,
        recount_max=0.2,
        damage_max=5.0,
        refund_max=0.5,
        check_valid_max=20.0,
    )
    metric = dataset.StoreMetric(
        date=datetime.date(2020, 5, 1),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=uuid(),
        recount_writeoffs_cost_lcy=0.12,
        damage_writeoffs_cost_lcy=4.0,
        refund_writeoffs_cost_lcy=0.04,
        check_valid_writeoffs_cost_lcy=19.0,
        gross_revenue_w_pur_cost_lcy=100.0,
    )

    view = StoreMetricView(metric, writeoff_limit)
    tap.eq_ok(view.writeoff_kpi, 100, 'Проходим по всем лимитам')

    metric.recount_writeoffs_cost_lcy = -0.12
    tap.eq_ok(view.writeoff_kpi, 100, 'Отрицательный пересчёт')

    metric.recount_writeoffs_cost_lcy = -0.3
    tap.eq_ok(view.writeoff_kpi, 70, 'Отрицательный пересчёт выше лимита')

    metric.recount_writeoffs_cost_lcy = 0.3
    tap.eq_ok(view.writeoff_kpi, 70, 'Положительный пересчёт выше лимита')

    metric.damage_writeoffs_cost_lcy = 5.01
    tap.eq_ok(view.writeoff_kpi, 40, 'Брак выше лимита')

    metric.refund_writeoffs_cost_lcy = 0.49999999
    tap.eq_ok(view.writeoff_kpi, 10, 'Возвраты округлились до лимита')

    metric.check_valid_writeoffs_cost_lcy = 20.0
    tap.eq_ok(view.writeoff_kpi, 0, 'КСГ ровно равны лимиту')

    writeoff_limit.recount_max = None
    tap.eq_ok(view.writeoff_kpi, 30, 'Лимит пересчёта не задан')

    writeoff_limit.damage_max = None
    tap.eq_ok(view.writeoff_kpi, 60, 'Лимит брака не задан')

    writeoff_limit.refund_max = None
    tap.eq_ok(view.writeoff_kpi, 90, 'Лимит возвратов не задан')

    writeoff_limit.check_valid_max = None
    tap.eq_ok(view.writeoff_kpi, 100, 'Лимит КСГ не задан')

    view = StoreMetricView(metric, None)
    tap.eq_ok(view.writeoff_kpi, None, 'Лимиты не заданы')
