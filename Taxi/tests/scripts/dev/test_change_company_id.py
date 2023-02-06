import argparse
from datetime import timedelta
from scripts.dev.change_company_id import change_company_id
from stall.model import schet_handler
from stall.model.schedule import Schedule


async def test_no_store(tap, dataset, uuid):
    with tap.plan(1, 'Проверка смены компании при отсутствии store'):
        company = await dataset.company()
        args = argparse.Namespace(
            store_id=uuid(),
            company_id=company.company_id,
            apply=True,
        )
        tap.eq(await change_company_id(args), None, 'компания не поменялась')


async def test_no_company(tap, dataset, uuid):
    with tap.plan(1, 'Проверка смены компании при отсутствии company'):
        store = await dataset.store()
        args = argparse.Namespace(
            store_id=store.store_id,
            company_id=uuid(),
            apply=True,
        )
        tap.eq(await change_company_id(args), None, 'компания не поменялась')


async def test_exists_orders(tap, dataset):
    with tap.plan(5, 'Проверка смены компании при существовании заказа'):
        company = await dataset.company()
        product = await dataset.product()
        store = await dataset.store()
        item = await dataset.item(store=store)
        tap.ok(company.company_id, 'компания создана')
        tap.ok(product.product_id, 'продукт создан')
        tap.ok(store.store_id, 'склад создан')
        tap.eq(item.store_id, store.store_id, 'посылка создана')

        await dataset.order(
            store=store,
            type='collect',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 128,
                }
            ]
        )
        args = argparse.Namespace(
            store_id=store.store_id,
            company_id=company.company_id,
            apply=True,
        )
        old_company_id = store.company_id
        await change_company_id(args)
        await store.reload()
        tap.eq(store.company_id, old_company_id, 'компания не поменялась')


async def test_exists_shifts(tap, dataset, now):
    with tap.plan(2, 'Проверка смены компании при существовании смены'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        tap.ok(store, 'склад, курьер, кластер и компания сгенерированы')
        _now = now().replace(microsecond=0)

        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='template',
            started_at=_now,
            closes_at=_now + timedelta(hours=1),
            # закидываем сколько-нибудь времени,
            # чтобы к настоящему моменту смена не закончилась
        )
        args = argparse.Namespace(
            store_id=store.external_id,
            company_id=company.company_id,
            apply=True,
        )
        old_company_id = store.company_id
        await change_company_id(args)
        await store.reload()
        tap.eq(store.company_id, old_company_id, 'компания не поменялась')


async def test_exists_periodical_tasks(tap, dataset, uuid):
    with tap.plan(3, 'Проверка смены компании при существовании остатков'):
        company = await dataset.company()
        store = await dataset.store()
        user = await dataset.user(role='admin')
        tap.ok(store, 'company + store created')
        task = await dataset.schet_task(
            handler=schet_handler.SchetHandler('dummy_cron'),
            schedule_draft=Schedule({'interval': {'seconds': 10}}),
            created_by=uuid(),
            store_id=store.store_id,
            company_id=store.company_id,
            user=user,
        )
        tap.ok(task, 'task created')
        await task.save()
        await task.approve(user_id=user.user_id)
        await task.start()
        args = argparse.Namespace(
            store_id=store.store_id,
            company_id=company.company_id,
            apply=True,
        )
        old_company_id = store.company_id
        await change_company_id(args)
        await store.reload()
        tap.eq(store.company_id, old_company_id, 'компания не поменялась')


async def test_exists_stocks(tap, dataset):
    with tap.plan(2, 'Проверка смены компании при существовании остатков'):
        company = await dataset.company()
        store = await dataset.store()
        product = await dataset.product()
        shelf = await dataset.shelf(store=store, type='store')
        order = await dataset.order(store_id=store.store_id, status='complete')
        tap.ok(store, 'склад, курьер и компания сгенерированы')
        await dataset.stock(
            product=product,
            shelf=shelf,
            store=store,
            order=order,
            lot='lot11',
            count=13
        )
        args = argparse.Namespace(
            store_id=store.store_id,
            company_id=company.company_id,
            apply=True,
        )
        old_company_id = store.company_id
        await change_company_id(args)
        await store.reload()
        tap.eq(store.company_id, old_company_id, 'компания не поменялась')


async def test_changer_company_no_apply(tap, dataset):
    with tap.plan(2, 'Проверка смены компании при отсутствии стоков, ордеров, '
                     'смен, периодических заданий и без параметра сохранения'):
        company = await dataset.company()
        store = await dataset.store()
        old_company_id = store.company_id
        tap.ok(store, 'склад сгенерирован')
        args = argparse.Namespace(
            store_id=store.store_id,
            company_id=company.company_id,
            apply=False,
        )
        await change_company_id(args)
        await store.reload()
        tap.eq(store.company_id, old_company_id, 'компания не поменялась')


async def test_changer_company_id(tap, dataset):
    with tap.plan(2, 'Проверка смены компании при отсутствии '
                     'стоков, ордеров, смен, периодических заданий'):
        company = await dataset.company()
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')
        args = argparse.Namespace(
            store_id=store.store_id,
            company_id=company.company_id,
            apply=True,
        )
        await change_company_id(args)
        await store.reload()
        tap.eq(store.company_id, company.company_id, 'компания поменялась')


async def test_changer_company_external(tap, dataset):
    with tap.plan(2, 'Проверка смены компании при отсутствии стоков, '
                     'ордеров, смен, периодических заданий by external'):
        company = await dataset.company()
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')
        args = argparse.Namespace(
            external_id=store.external_id,
            company_id=company.company_id,
            apply=True,
        )
        await change_company_id(args)
        await store.reload()
        tap.eq(store.company_id, company.company_id, 'компания поменялась')
