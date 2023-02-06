import datetime
from stall.model.analytics.store_metric import StoreMetric
import tests.dataset as dt


async def test_list_invalid(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')
    await t.post_ok(
        'api_report_data_store_metrics_list',
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
        'api_report_data_store_metrics_list',
        json={
            'store_id': store.store_id,
        }
    )
    t.status_is(400, diag=True)
    t.json_is('code', 'BAD_REQUEST')


async def test_list_invalid_period(api, dataset: dt):
    store = await dataset.store()
    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_list',
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
    }
    with tap.subtest(3, 'Ручка недоступна без пермита') as taps:
        t.tap = taps
        await t.post_ok(
            'api_report_data_store_metrics_list',
            json=request_body
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

    with user.role as role:
        role.add_permit('store_analytics', True)

        with tap.subtest(3, 'Пермит есть - ручка доступна') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_store_metrics_list',
                json=request_body
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        with tap.subtest(3, 'Ручка недоступна для другой лавки') as taps:
            t.tap = taps
            await t.post_ok(
                'api_report_data_store_metrics_list',
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

async def test_list_empty(api, dataset: dt):
    # with tap.plan(4):
    store = await dataset.store()

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_list',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_is('executers', [])


async def test_list_nonempty(api, dataset: dt, tap):
    period = (
        datetime.date(2020, 5, 1),
        datetime.date(2020, 5, 10)
    )
    store = await dataset.store()
    metrics = await dataset.store_metric_daily(_store=store, period=period,
                                               executer_cnt=2 )
    tap.eq_ok(len(metrics), 30, 'Метрики сгенерированы на 10 дней')

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_list',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 6),
                'end': datetime.date(2020, 5, 10),
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('executers')
    tap.eq_ok(len(t.res['json']['executers']), 2,
              'Получены метрики по 2 кладовщикам')


async def test_list_two_days(api, dataset: dt, tap):
    store = await dataset.store()
    executer = await dataset.user(store=store, role='executer')

    m1 = dataset.StoreMetric(
        date=datetime.date(2020, 5, 1),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        executer_id=executer.user_id,
        executer_name='Executer1',
        external_executer_id='1234567',
        grand_total_cnt=11,
        overall_items=77,
        overall_time=2001,
        fact_shift_dur_sec=18005,
        overall_speed_dur_sec=8055,
        cur_dur_sec_not_start=3600,
        cur_dur_sec_plan=18000,
        early_leaving_dur_sec=600,
        lateness_dur_sec=300,
        complaints_10_cnt=5
    )
    m2 = dataset.StoreMetric(
        date=datetime.date(2020, 5, 2),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        executer_id=executer.user_id,
        executer_name='Executer1',
        external_executer_id='1234567',
        grand_total_cnt=13,
        overall_items=66,
        overall_time=1563,
        fact_shift_dur_sec=20400,
        overall_speed_dur_sec=9111,
        cur_dur_sec_not_start=0,
        cur_dur_sec_plan=21600,
        early_leaving_dur_sec=360,
        lateness_dur_sec=1200,
        complaints_10_cnt=3
    )

    await m1.save()
    await m2.save()

    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_list',
        json={
            'store_id': store.store_id,
            'period': {
                'begin': datetime.date(2020, 5, 1),
                'end': datetime.date(2020, 5, 2),
            }
        }
    )
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('executers')
    tap.eq_ok(len(t.res['json']['executers']), 1,
              'Получены метрики по 1 кладовщику')
    t.json_is('executers.*.executer_name', 'Executer1')
    t.json_is('executers.*.external_executer_id', '1234567')
    # overall_items
    t.json_is(
        'executers.0.overall_items.value',
        77 + 66
    )
    # overall_time / overall_items
    t.json_is(
        'executers.0.overall_speed.value',
        round((2001 + 1563) / (77 + 66), 2)
    )
    # grand_total_cnt
    t.json_is(
        'executers.0.orders.value',
        11 + 13
    )
    # overall_time / grand_total_cnt / 60
    t.json_is(
        'executers.0.order_speed.value',
        round((2001 + 1563) / (11 + 13), 2)
    )
    # fact_shift_dur_sec // 60 // 60
    t.json_is(
        'executers.0.sh.value',
        (18005 + 20400) // 60 // 60
    )
    # 100 * cur_dur_sec_not_start / cur_dur_sec_plan
    t.json_is(
        'executers.0.shift_not_start.value',
        round(100 * (3600 + 0) / (18000 + 21600))
    )
    # 100 * (early_leaving_dur_sec + lateness_dur_sec) / cur_dur_sec_plan
    t.json_is(
        'executers.0.early_leaving_lateness.value',
        round(100 * (600 + 360 + 300 + 1200) / (18000 + 21600))
    )
    # complaints_10_cnt
    t.json_is(
        'executers.0.compensation.value',
        5 + 3
    )


async def test_list_zero_data(api, dataset: dt):
    store = await dataset.store()
    executer = await dataset.user(store=store, role='executer')
    store_metric = StoreMetric(
        date=datetime.date(2020, 5, 1),
        time=datetime.datetime(2020, 5, 1, 0, 0, 0, 0),
        store_id=store.store_id,
        executer_id=executer.user_id,
        executer_name='Executer1',
        external_executer_id='1234567',
    )
    await store_metric.save()
    t = await api(role='admin')

    await t.post_ok(
        'api_report_data_store_metrics_list',
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
    t.json_has('executers')
    t.json_is('executers.0.executer_name', 'Executer1')
    t.json_is('executers.0.external_executer_id', '1234567')
    t.json_is('executers.0.overall_items.value', 0)
    t.json_is('executers.0.orders.value', 0)
    t.json_is('executers.0.sh.value', 0)
    t.json_is('executers.0.overall_speed.value', 0)
    t.json_is('executers.0.order_speed.value', 0)
    t.json_is('executers.0.shift_not_start.value', 0)
    t.json_is('executers.0.early_leaving_lateness.value', 0)
    t.json_is('executers.0.compensation.value', 0)
