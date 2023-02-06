import datetime
from stall.model.analytics.md_audit import MDAudit
import tests.dataset as dt


async def test_graph_invalid(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')
    await t.post_ok(
        'api_report_data_store_metrics_graph',
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
        'api_report_data_store_metrics_graph',
        json={
            'store_id': store.store_id,
            'detalization': 'day',
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')
    await t.post_ok(
        'api_report_data_store_metrics_graph',
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
        'api_report_data_store_metrics_graph',
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
            'api_report_data_store_metrics_graph',
            json=request_body
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

    with user.role as role:
        role.add_permit('store_analytics', True)

        with tap.subtest(3, 'Пермит есть - ручка доступна') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_store_metrics_graph',
                json=request_body
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        with tap.subtest(3, 'Ручка недоступна для другой лавки') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_store_metrics_graph',
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
        'api_report_data_store_metrics_graph',
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
    t.json_is('graphs.overall_speed', [])
    t.json_is('graphs.waiting_time', [])
    t.json_is('graphs.compensation', [])
    t.json_is('graphs.md_audit', [])


async def test_graph_two_days(api, dataset: dt, uuid):
    store = await dataset.store(external_id=uuid())
    await dataset.StoreMetric(
        date=datetime.date(2020, 5, 1),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        grand_total_cnt=24,
        success_delivered_cnt=22,
        overall_items=77,
        overall_time=2001,
        waiting_sec=4012.2,
        waiting_orders=23,
        fact_shift_dur_sec=18005,
        overall_speed_dur_sec=8055,
        cur_dur_sec_not_start=3600,
        cur_dur_sec_plan=18000,
        early_leaving_dur_sec=600,
        lateness_dur_sec=300,
        complaints_10_cnt=5,
        compensations={
            'not_delivered': 3
        }
    ).save()
    await dataset.StoreMetric(
        date=datetime.date(2020, 5, 2),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        grand_total_cnt=13,
        success_delivered_cnt=11,
        overall_items=66,
        overall_time=1563,
        waiting_sec=3013.3,
        waiting_orders=12,
        fact_shift_dur_sec=20400,
        overall_speed_dur_sec=9111,
        cur_dur_sec_not_start=0,
        cur_dur_sec_plan=21600,
        early_leaving_dur_sec=360,
        lateness_dur_sec=1200,
        complaints_10_cnt=3,
        compensations={
            'not_delivered': 2
        }
    ).save()
    await MDAudit(
        date=datetime.date(2020, 4, 27), # Понедельник
        store_id=store.store_id,
        external_store_id=store.external_id,
        value=87.723
    ).save()


    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_graph',
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
    # overall_time / overall_items
    t.json_is('graphs.overall_speed.0.value', round(2001 / 77, 2))
    t.json_is('graphs.overall_speed.1.value', round(1563 / 66, 2))
    t.json_is('graphs.overall_speed.0.threshold', 0)
    t.json_is('graphs.overall_speed.0.date', '2020-05-01')

    # waiting_sec / waiting_orders
    t.json_is('graphs.waiting_time.0.value', round(4012.2 / 23 / 60, 2))
    t.json_is('graphs.waiting_time.1.value', round(3013.3 / 12 / 60, 2))
    t.json_is('graphs.waiting_time.0.threshold', 0)
    t.json_is('graphs.waiting_time.0.date', '2020-05-01')

    # 100 * complaints_10_cnt / grand_total_cnt
    t.json_is('graphs.compensation.0.value', round(100 * 5 / 24, 2))
    t.json_is('graphs.compensation.0.details.total.value', 5)
    t.json_is('graphs.compensation.0.details.not_delivered.value', 3)
    t.json_is('graphs.compensation.1.value', round(100 * 3 / 13, 2))
    t.json_is('graphs.compensation.1.details.total.value', 3)
    t.json_is('graphs.compensation.1.details.not_delivered.value', 2)
    t.json_is('graphs.compensation.0.threshold', 0)
    t.json_is('graphs.compensation.0.date', '2020-05-01')

    # MD Audit
    t.json_is('graphs.md_audit.0.value', round(87.723, 2))
    t.json_is('graphs.md_audit.1.value', round(87.723, 2))
    t.json_is('graphs.md_audit.0.date', '2020-05-01')

    # Aggregations
    t.json_is('aggregations.total.value', 13 + 24)
    t.json_has('aggregations.total.threshold')
    t.json_is('aggregations.waiting_for_assemble.value', 23 + 12)
    t.json_has('aggregations.waiting_for_assemble.threshold')
    t.json_is(
        'aggregations.speed_assemble.value',
        round((1563 + 2001) / (13 + 24), 2)
    )
    t.json_has('aggregations.speed_assemble.threshold')


async def test_graph_zero_data(api, dataset: dt, tap):
    period = (
        datetime.date(2020, 5, 1),
        datetime.date(2020, 5, 1)
    )
    store = await dataset.store()
    metrics = await dataset.store_metric_daily(_store=store, period=period,
                                               executer_cnt=0)
    tap.eq_ok(len(metrics), 1, 'Метрики сгенерированы на 1 день')
    for metric in metrics:
        metric.compensations = {}
        await metric.save()

    t = await api(role='admin')
    await t.post_ok(
        'api_report_data_store_metrics_graph',
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
    t.json_is('graphs.overall_speed.0.value', None)
    t.json_is('graphs.overall_speed.0.threshold', 0)
    t.json_is('graphs.overall_speed.0.date', '2020-05-01')

    t.json_is('graphs.waiting_time.0.value', None)
    t.json_is('graphs.waiting_time.0.threshold', 0)
    t.json_is('graphs.waiting_time.0.date', '2020-05-01')

    t.json_is('graphs.compensation.0.value', None)
    t.json_is('graphs.compensation.0.threshold', 0)
    t.json_is('graphs.compensation.0.details.total.value', 0)
    t.json_is('graphs.compensation.0.details.not_delivered.value', 0)
    t.json_is('graphs.compensation.0.date', '2020-05-01')

    t.json_is('graphs.md_audit.0.date', '2020-05-01')

    t.json_is('aggregations.total.value', 0)
    t.json_is('aggregations.waiting_for_assemble.value', 0)
    t.json_is('aggregations.speed_assemble.value', 0)


async def test_graph_week(api, dataset: dt, tap):
    period = (
        datetime.date(2020, 5, 4), # Понедельник
        datetime.date(2020, 5, 18)
    )
    store = await dataset.store()
    metrics = await dataset.store_metric_daily(_store=store, period=period)
    tap.eq_ok(len(metrics), 30, 'Метрики сгенерированы на 2 недели')

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_graph',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 4),
                'end': datetime.date(2020, 5, 10),
            },
            'detalization': 'week'
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    tap.eq_ok(len(t.res['json']['graphs']['overall_speed']), 1,
              'График overall_speed за 1 неделю')
    t.json_is('graphs.overall_speed.0.date', '2020-05-04')

    tap.eq_ok(len(t.res['json']['graphs']['waiting_time']), 1,
              'График waiting_time за 1 неделю')
    t.json_is('graphs.waiting_time.0.date', '2020-05-04')

    tap.eq_ok(len(t.res['json']['graphs']['compensation']), 1,
              'График compensation за 1 неделю')
    t.json_is('graphs.compensation.0.date', '2020-05-04')

    tap.eq_ok(len(t.res['json']['graphs']['compensation']), 1,
              'График md_audit за 1 неделю')
    t.json_is('graphs.md_audit.0.date', '2020-05-04')

    await t.post_ok(
        'api_report_data_store_metrics_graph',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 5),
                'end': datetime.date(2020, 5, 13),
            },
            'detalization': 'week'
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('graphs')
    tap.eq_ok(len(t.res['json']['graphs']['overall_speed']), 2,
              'График overall_speed за 2 недели')
    t.json_is('graphs.overall_speed.0.date', '2020-05-05')
    t.json_is('graphs.overall_speed.1.date', '2020-05-11')

    tap.eq_ok(len(t.res['json']['graphs']['waiting_time']), 2,
              'График waiting_time за 2 недели')
    t.json_is('graphs.waiting_time.0.date', '2020-05-05')
    t.json_is('graphs.waiting_time.1.date', '2020-05-11')

    tap.eq_ok(len(t.res['json']['graphs']['compensation']), 2,
              'График compensation за 2 недели')
    t.json_is('graphs.compensation.0.date', '2020-05-05')
    t.json_is('graphs.compensation.1.date', '2020-05-11')

    tap.eq_ok(len(t.res['json']['graphs']['md_audit']), 2,
              'График md_audit за 2 недели')
    t.json_is('graphs.md_audit.0.date', '2020-05-05')
    t.json_is('graphs.md_audit.1.date', '2020-05-11')


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
        'api_report_data_store_metrics_graph',
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
    tap.eq_ok(len(t.res['json']['graphs']['overall_speed']), 1,
              'График overall_speed за 1 месяц')
    t.json_is('graphs.overall_speed.0.date', '2020-05-04')

    tap.eq_ok(len(t.res['json']['graphs']['waiting_time']), 1,
              'График waiting_time за 1 месяц')
    t.json_is('graphs.waiting_time.0.date', '2020-05-04')

    tap.eq_ok(len(t.res['json']['graphs']['compensation']), 1,
              'График compensation за 1 месяц')
    t.json_is('graphs.compensation.0.date', '2020-05-04')

    tap.eq_ok(len(t.res['json']['graphs']['md_audit']), 1,
              'График md_audit за 1 месяц')
    t.json_is('graphs.md_audit.0.date', '2020-05-04')

    await t.post_ok(
        'api_report_data_store_metrics_graph',
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
    tap.eq_ok(len(t.res['json']['graphs']['overall_speed']), 2,
              'График overall_speed за 2 недели')
    t.json_is('graphs.overall_speed.0.date', '2020-05-01')
    t.json_is('graphs.overall_speed.1.date', '2020-06-01')

    tap.eq_ok(len(t.res['json']['graphs']['waiting_time']), 2,
              'График waiting_time за 2 недели')
    t.json_is('graphs.waiting_time.0.date', '2020-05-01')
    t.json_is('graphs.waiting_time.1.date', '2020-06-01')

    tap.eq_ok(len(t.res['json']['graphs']['compensation']), 2,
              'График compensation за 2 недели')
    t.json_is('graphs.compensation.0.date', '2020-05-01')
    t.json_is('graphs.compensation.1.date', '2020-06-01')

    tap.eq_ok(len(t.res['json']['graphs']['md_audit']), 2,
              'График md_audit за 2 недели')
    t.json_is('graphs.md_audit.0.date', '2020-05-01')
    t.json_is('graphs.md_audit.1.date', '2020-06-01')

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
        'api_report_data_store_metrics_graph',
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
    tap.eq_ok(len(t.res['json']['graphs']['overall_speed']), 31,
              'График overall_speed за 1 месяц')
    t.json_is('graphs.overall_speed.0.date', '2020-05-01')
    t.json_is('graphs.overall_speed.30.date', '2020-05-31')

    tap.eq_ok(len(t.res['json']['graphs']['waiting_time']), 31,
              'График waiting_time за 1 месяц')
    t.json_is('graphs.waiting_time.0.date', '2020-05-01')
    t.json_is('graphs.waiting_time.30.date', '2020-05-31')

    tap.eq_ok(len(t.res['json']['graphs']['compensation']), 31,
              'График compensation за 1 месяц')
    t.json_is('graphs.compensation.0.date', '2020-05-01')
    t.json_is('graphs.compensation.30.date', '2020-05-31')

    tap.eq_ok(len(t.res['json']['graphs']['md_audit']), 31,
              'График md_audit за 1 месяц')
    t.json_is('graphs.md_audit.0.date', '2020-05-01')
    t.json_is('graphs.md_audit.30.date', '2020-05-31')
