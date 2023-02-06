from datetime import timedelta

import pytest


async def test_import_data(tap, api, dataset, uuid, now, job, make_csv_str):
    with tap.plan(12, 'Импорт поставок из CSV'):
        store = await dataset.store()
        provider = await dataset.provider(
            stores=[store.store_id],
            tags=['freezer'],
        )
        user = await dataset.user(role='admin', store=store)

        plan_date = (now() + timedelta(days=1)).date()
        delivery_id = uuid()

        csv_str = make_csv_str(
            [
                'Номер',
                'НомерПоДаннымПоставщика',
                'ИдЗаказаПоставщику',
                'ИдКонтрагента',
                'ДатаПоступления',
                ''
            ],
            [
                {
                    'Номер': 'Я100-063557',
                    'НомерПоДаннымПоставщика':  '',
                    'ИдЗаказаПоставщику':  delivery_id,
                    'ИдКонтрагента': provider.external_id,
                    'ДатаПоступления': plan_date.strftime('%d.%m.%Y'),
                    '': '',
                }
            ]
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_deliveries_import_data',
            json={'csv': csv_str},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        delivery = await dataset.Delivery.load(delivery_id, by='conflict')
        tap.ok(delivery, 'Доставка импортирована')
        tap.eq(delivery.external_id, delivery_id, 'delivery_id')
        tap.eq(delivery.provider_id, provider.provider_id, 'provider_id')
        tap.eq(delivery.tags, provider.tags, 'tags')
        tap.eq(delivery.plan_date, plan_date, 'plan_date')
        tap.eq(delivery.title, 'Я100-063557', 'title')
        tap.eq(delivery.attr.units, None, 'units')


@pytest.mark.parametrize('filepath', [
    'test_import_data/2020-08-10.csv',
    'test_import_data/2020-08-10.mac.csv',
    'test_import_data/2020-08-11.csv',
    'test_import_data/2020-08-11.2.csv',
])
async def test_files(tap, api, dataset, filepath, job, load_file):
    with tap.plan(4, f'Проверка реальных файлов: {filepath}'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)

        csv_str = load_file(filepath)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_deliveries_import_data',
            json={'csv': csv_str},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')
