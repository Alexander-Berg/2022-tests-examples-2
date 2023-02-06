import datetime
import random
import tests.dataset as dt

async def test_rank_invalid(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')
    await t.post_ok(
        'api_report_data_store_metrics_rank',
        json={
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            },
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')

    await t.post_ok(
        'api_report_data_store_metrics_rank',
        json={
            'store_id': store.store_id,
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')

async def test_rank_invalid_period(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_rank',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2010, 5, 1),
            },
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'ER_BAD_REQUEST')

async def test_rank_access(api, tap, dataset: dt):
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
    }
    with tap.subtest(3, 'Ручка недоступна без пермита') as taps:
        t.tap = taps
        await t.post_ok(
            'api_report_data_store_metrics_rank',
            json=request_body
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

    with user.role as role:
        role.add_permit('store_analytics', True)

        with tap.subtest(3, 'Пермит есть - ручка доступна') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_store_metrics_rank',
                json=request_body
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        with tap.subtest(3, 'Ручка недоступна для другой лавки') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_store_metrics_rank',
                json={
                    'store_id': other_store.store_id,
                    'period': {
                        'begin': datetime.date(2020, 5, 5),
                        'end': datetime.date(2020, 5, 5),
                    },
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

async def test_rank_empty(api, dataset: dt):
    store = await dataset.store()
    user = await dataset.user(role='admin', store=store)
    t = await api(user=user)

    await t.post_ok(
        'api_report_data_store_metrics_rank',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2002, 5, 5),
                'end': datetime.date(2002, 5, 10),
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_is('rank.overall_speed', None)
    t.json_is('rank.waiting_time', None)
    t.json_is('rank.compensation', None)
    t.json_is('rank.writeoff', None)
    t.json_is('rank.md_audit', None)


async def test_rank(api, dataset: dt):
    store1 = await dataset.store()
    store2 = await dataset.store()
    store_cluster = random.randint(10000, 99999)
    store_factor = random.randint(10000, 99999)
    not_similar_store = await dataset.store()
    some_date = datetime.date(2000, 5, 6)
    some_monday = some_date - datetime.timedelta(days=some_date.weekday())

    await dataset.StoreMetric(
        date=some_date,
        time=datetime.datetime(*some_date.timetuple()[:-2]),
        store_id=store1.store_id,
        store_cluster=store_cluster,
        store_factor=store_factor,

        overall_items=100,
        overall_time=9000,

        waiting_orders=10,
        waiting_sec=1200,

        complaints_10_cnt=20,
        success_delivered_cnt=50,

        check_valid_writeoffs_cost_lcy=10,
        gross_revenue_w_pur_cost_lcy=100,
    ).save()

    await dataset.MDAudit(
        date=some_monday,
        store_id=store1.store_id,
        external_store_id=store1.external_id,
        value=40.0
    ).save()

    await dataset.StoreMetric(
        date=some_date,
        time=datetime.datetime(*some_date.timetuple()[:-2]),
        store_id=store2.store_id,
        store_cluster=store_cluster,
        store_factor=store_factor,

        overall_items=100,
        overall_time=11000,

        waiting_orders=10,
        waiting_sec=1600,

        complaints_10_cnt=10,
        success_delivered_cnt=50,

        check_valid_writeoffs_cost_lcy=20,
        gross_revenue_w_pur_cost_lcy=100,
    ).save()

    await dataset.MDAudit(
        date=some_monday,
        store_id=store2.store_id,
        external_store_id=store2.external_id,
        value=60.0
    ).save()

    await dataset.StoreMetric(
        date=some_date,
        time=datetime.datetime(*some_date.timetuple()[:-2]),
        store_id=not_similar_store.store_id,
        store_cluster=random.randint(10000, 99999),
        store_factor=random.randint(10000, 99999),

        overall_items=100,
        overall_time=7000,
    ).save()

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_rank',
        json={
            'store_id': store1.store_id,
            'period': {
                'begin': some_date,
                'end': some_date,
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    # overall_time / overall_items
    # 9000 / 100 = 90 # 1 место
    # Меньше - лучше
    t.json_is('rank.overall_speed', 1)
    # waiting_sec / waiting_orders
    # 1200 / 10 = 120 # 1 место
    # Меньше - лучше
    t.json_is('rank.waiting_time', 1)
    # complaints_10_cnt / success_delivered_cnt
    # 20 / 50 = 0.4 # 2 место
    # Меньше - лучше
    t.json_is('rank.compensation', 2)
    # 100 * (
    #     0.3 * recount_writeoffs_cost_lcy
    #     + 0.3 * damage_writeoffs_cost_lcy
    #     + 0.3 * refund_writeoffs_cost_lcy
    #     + 0.1 * check_valid_writeoffs_cost_lcy
    # ) / gross_revenue_w_pur_cost_lcy
    # 0.1 #  2 место
    # Меньше лучше
    t.json_is('rank.writeoff', 1)
    # MD Audit
    # 40.0 # 2 место
    # Больше - лучше
    t.json_is('rank.md_audit', 2)

    await t.post_ok(
        'api_report_data_store_metrics_rank',
        json={
            'store_id': store2.store_id,
            'period': {
                'begin': some_date,
                'end': some_date,
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    # overall_time / overall_items
    # 11000 / 100 = 110 # 2 место
    # Меньше - лучше
    t.json_is('rank.overall_speed', 2)
    # waiting_sec / waiting_orders
    # 1600 / 10 = 160 # 2 место
    # Меньше - лучше
    t.json_is('rank.waiting_time', 2)
    # complaints_10_cnt / success_delivered_cnt
    # 10 / 50 # 1 место
    # Меньше - лучше
    t.json_is('rank.compensation', 1)
    # 100 * (
    #     0.3 * recount_writeoffs_cost_lcy
    #     + 0.3 * damage_writeoffs_cost_lcy
    #     + 0.3 * refund_writeoffs_cost_lcy
    #     + 0.1 * check_valid_writeoffs_cost_lcy
    # ) / gross_revenue_w_pur_cost_lcy
    # 0.2 #  2 место
    # Меньше лучше
    t.json_is('rank.writeoff', 2)
    # MD Audit
    # 60.0 # 1 место
    # Больше - лучше
    t.json_is('rank.md_audit', 1)

    await t.post_ok(
        'api_report_data_store_metrics_rank',
        json={
            'store_id': not_similar_store.store_id,
            'period': {
                'begin': some_date,
                'end': some_date,
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    # overall_time / overall_items
    # Меньше - лучше
    t.json_is('rank.overall_speed', 1)

async def test_last_cluster_and_factor(tap, dataset: dt):
    begin_date = datetime.date(2003, 5, 6)
    empty_date = datetime.date(2003, 5, 7)
    end_date = datetime.date(2003, 5, 8)
    store = await dataset.store()
    begin_metric, *_ = await dataset.store_metric_daily(
        _store=store,
        executer_cnt=0,
        period=(begin_date, begin_date),
    )
    tap.ok(begin_metric, 'Метрика создана на 6 число')
    begin_metric.store_cluster = 3
    begin_metric.store_factor = 5
    await begin_metric.save()

    end_metric, *_ = await dataset.store_metric_daily(
        _store=store,
        executer_cnt=0,
        period=(end_date, end_date),
    )
    tap.ok(end_metric, 'Метрика создана на 8 число')
    end_metric.store_cluster = 7
    end_metric.store_factor = 9
    await end_metric.save()

    with tap.subtest(4, 'Данные о лавке из первой метрки') as taps:
        cursor = await dataset.StoreMetric.list(
            by='last_cluster_and_factor',
            full=True,
            db={'mode': 'slave'},
            conditions=(
                ('date', '<=', begin_date),
            ),
        )
        metric = next(iter(
            it for it in cursor.list
            if it.store_id == store.store_id
        ), None)
        taps.ok(metric, 'Актуальная метрика получена')
        taps.eq_ok(metric.store_id, store.store_id,
                   'Актуальная метрика принадлежит правильной лавке')
        taps.eq_ok(metric.store_cluster, begin_metric.store_cluster,
                   'Кластер от begin_date')
        taps.eq_ok(metric.store_factor, begin_metric.store_factor,
                   'Фактор от begin_date')

    with tap.subtest(4, 'Данные о лавке изменились') as taps:
        cursor = await dataset.StoreMetric.list(
            by='last_cluster_and_factor',
            full=True,
            db={'mode': 'slave'},
            conditions=(
                ('date', '<=', end_date),
            ),
        )
        metric = next(iter(
            it for it in cursor.list
            if it.store_id == store.store_id
        ), None)
        taps.ok(metric, 'Актуальная метрика получена')
        taps.eq_ok(metric.store_id, store.store_id,
                   'Актуальная метрика принадлежит правильной лавке')
        taps.eq_ok(metric.store_cluster, end_metric.store_cluster,
                   'Кластер от end_date')
        taps.eq_ok(metric.store_factor, end_metric.store_factor,
                   'Фактор от end_date')

    with tap.subtest(
            4, 'На искомую дату данных о лавке нет, они были вчера'
    ) as taps:
        cursor = await dataset.StoreMetric.list(
            by='last_cluster_and_factor',
            full=True,
            db={'mode': 'slave'},
            conditions=(
                ('date', '<=', empty_date),
            ),
        )
        metric = next(iter(
            it for it in cursor.list
            if it.store_id == store.store_id
        ), None)
        taps.ok(metric, 'Актуальная метрика получена')
        taps.eq_ok(metric.store_id, store.store_id,
                   'Актуальная метрика принадлежит правильной лавке')
        taps.eq_ok(metric.store_cluster, begin_metric.store_cluster,
                   'Кластер от begin_date')
        taps.eq_ok(metric.store_factor, begin_metric.store_factor,
                   'Фактор от begin_date')
