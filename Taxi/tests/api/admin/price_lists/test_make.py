# pylint: disable=too-many-locals,too-many-statements
import pytest
from stall.model.draft.price_list import DraftPriceList
from stall.model.price_list_product import PriceListProduct


async def test_make_update(tap, api, dataset, job, lp):
    with tap.plan(29, 'Обновление прайс листа'):

        user1        = await dataset.user()
        user2        = await dataset.user()
        user3        = await dataset.user()
        user4        = await dataset.user()

        product0    = await dataset.product()
        product1    = await dataset.product()
        product2    = await dataset.product()
        product3    = await dataset.product()
        product4    = await dataset.product()

        price_list  = await dataset.price_list()
        await dataset.price_list_product(
            product=product0,
            price_list=price_list,
            price={'store': 11},
            user=user1,
        )
        await dataset.price_list_product(
            product=product1,
            price_list=price_list,
            price={'store': 100},
            user=user1,
        )
        await dataset.price_list_product(
            product=product2,
            price_list=price_list,
            price={'store': 200},
            user=user1,
        )
        await dataset.price_list_product(
            product=product4,
            price_list=price_list,
            price={'store': 400},
            user=user1,
        )

        draft1      = await dataset.draft_price_list(status='ready',
                                                     user=user1)
        with draft1 as draft:
            await dataset.draft_price_list_product(
                product=product1,
                price_list=draft,
                price={'store': 110},
                user=user2,
            )
            await dataset.draft_price_list_product(
                product=product2,
                price_list=draft,
                price={'store': 220},
                user=user2,
            )
            await dataset.draft_price_list_product(
                product=product4,
                price_list=draft,
                price={'store': 440},
                user=user2,
                status='deleted',
            )

        draft2      = await dataset.draft_price_list(status='ready',
                                                     user=user2)
        with draft2 as draft:
            await dataset.draft_price_list_product(
                product=product2,
                price_list=draft,
                price={'store': 222},
                user=user3,
            )
            await dataset.draft_price_list_product(
                product=product3,
                price_list=draft,
                price={'store': 330},
                user=user3,
            )

        t = await api(user=user4)
        await t.post_ok(
            'api_admin_price_lists_make',
            json={
                'price_list_id': price_list.price_list_id,
                'drafts': [draft1.price_list_id, draft2.price_list_id],
                'mode': 'update',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('job_id')

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Та же что в событии')

        updated = await job.call(task)
        tap.ok(updated, 'Сборка выполнена')
        tap.eq(updated.user_id, user4.user_id, 'Пользователь применивший')

        pp_list = (
            await PriceListProduct.list(
                by='look',
                conditions=('price_list_id', price_list.price_list_id),
            )
        ).list
        tap.eq(len(pp_list), 5, 'Всего записей прайса (включая удаленные)')
        pp_list = dict((x.product_id, x) for x in pp_list)

        with pp_list[product0.product_id] as pp:
            tap.eq(pp.price.store, 11, 'Цена не менялась')
            tap.eq(pp.user_id, user1.user_id, 'Пользователь остался')
            tap.eq(pp.status, 'active', 'Активный')

        with pp_list[product1.product_id] as pp:
            tap.eq(pp.price.store, 110, 'Цена обновлена')
            tap.eq(pp.user_id, user2.user_id, 'Пользователь изменился')
            tap.eq(pp.status, 'active', 'Активный')

        with pp_list[product2.product_id] as pp:
            tap.eq(pp.price.store, 222, 'Последняя перезаписывает')
            tap.eq(pp.user_id, user3.user_id, 'Пользователь последний')
            tap.eq(pp.status, 'active', 'Активный')

        with pp_list[product3.product_id] as pp:
            tap.eq(pp.price.store, 330, 'Новые добавлены')
            tap.eq(pp.user_id, user3.user_id, 'Пользователь добавлен')
            tap.eq(pp.status, 'active', 'Активный')

        with pp_list[product4.product_id] as pp:
            tap.eq(pp.price.store, 400, 'Цена не менялась')
            tap.eq(pp.user_id, user2.user_id, 'Пользователь добавлен')
            tap.eq(pp.status, 'removed', 'Удален')

        tap.ok(lp.exists(['system']), 'Событие отправлено')

        with await draft1.reload() as draft:
            tap.eq(draft.status, 'applied', 'Статус применен')

        with await draft2.reload() as draft:
            tap.eq(draft.status, 'applied', 'Статус применен')

        t = await api(user=user1)
        await t.post_ok(
            'api_admin_price_lists_make',
            json={
                'price_list_id': price_list.price_list_id,
                'drafts': [draft1.price_list_id, draft2.price_list_id],
                'mode': 'update',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_make_replace(tap, api, dataset, job, lp):
    with tap.plan(29, 'Замена прайс листа'):

        user1        = await dataset.user()
        user2        = await dataset.user()
        user3        = await dataset.user()
        user4        = await dataset.user()

        product0    = await dataset.product()
        product1    = await dataset.product()
        product2    = await dataset.product()
        product3    = await dataset.product()
        product4    = await dataset.product()

        price_list  = await dataset.price_list()
        await dataset.price_list_product(
            product=product0,
            price_list=price_list,
            price={'store': 11},
            user=user1,
        )
        await dataset.price_list_product(
            product=product1,
            price_list=price_list,
            price={'store': 100},
            user=user1,
        )
        await dataset.price_list_product(
            product=product2,
            price_list=price_list,
            price={'store': 200},
            user=user1,
        )
        await dataset.price_list_product(
            product=product4,
            price_list=price_list,
            price={'store': 400},
            user=user1,
        )

        draft1      = await dataset.draft_price_list(status='ready',
                                                     user=user1)
        with draft1 as draft:
            await dataset.draft_price_list_product(
                product=product1,
                price_list=draft,
                price={'store': 110},
                user=user2,
            )
            await dataset.draft_price_list_product(
                product=product2,
                price_list=draft,
                price={'store': 220},
                user=user2,
            )
            await dataset.draft_price_list_product(
                product=product4,
                price_list=draft,
                price={'store': 440},
                user=user2,
                status='deleted',
            )

        draft2      = await dataset.draft_price_list(status='ready',
                                                     user=user2)
        with draft2 as draft:
            await dataset.draft_price_list_product(
                product=product2,
                price_list=draft,
                price={'store': 222},
                user=user3,
            )
            await dataset.draft_price_list_product(
                product=product3,
                price_list=draft,
                price={'store': 330},
                user=user3,
            )

        t = await api(user=user4)
        await t.post_ok(
            'api_admin_price_lists_make',
            json={
                'price_list_id': price_list.price_list_id,
                'drafts': [draft1.price_list_id, draft2.price_list_id],
                'mode': 'replace',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('job_id')

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Та же что в событии')

        updated = await job.call(task)
        tap.ok(updated, 'Сборка выполнена')
        tap.eq(updated.user_id, user4.user_id, 'Пользователь применивший')

        pp_list = (
            await PriceListProduct.list(
                by='look',
                conditions=('price_list_id', price_list.price_list_id),
            )
        ).list
        tap.eq(len(pp_list), 5, 'Всего записей прайса (включая удаленные)')

        pp_list = dict((x.product_id, x) for x in pp_list)

        with pp_list[product0.product_id] as pp:
            tap.eq(pp.price.store, 11, 'Цена не менялясь')
            tap.eq(pp.user_id, user1.user_id, 'Пользователь не менялся')
            tap.eq(pp.status, 'removed', 'Удален')

        with pp_list[product1.product_id] as pp:
            tap.eq(pp.price.store, 110, 'Цена обновлена')
            tap.eq(pp.user_id, user2.user_id, 'Пользователь изменился')
            tap.eq(pp.status, 'active', 'Активный')

        with pp_list[product2.product_id] as pp:
            tap.eq(pp.price.store, 222, 'Последняя перезаписывает')
            tap.eq(pp.user_id, user3.user_id, 'Пользователь последний')
            tap.eq(pp.status, 'active', 'Активный')

        with pp_list[product3.product_id] as pp:
            tap.eq(pp.price.store, 330, 'Новые добавлены')
            tap.eq(pp.user_id, user3.user_id, 'Пользователь добавлен')
            tap.eq(pp.status, 'active', 'Активный')

        with pp_list[product4.product_id] as pp:
            tap.eq(pp.price.store, 400, 'Цена не менялась')
            tap.eq(pp.user_id, user2.user_id, 'Пользователь добавлен')
            tap.eq(pp.status, 'removed', 'Удален')

        tap.ok(lp.exists(['system']), 'Событие отправлено')

        with await draft1.reload() as draft:
            tap.eq(draft.status, 'applied', 'Статус применен')

        with await draft2.reload() as draft:
            tap.eq(draft.status, 'applied', 'Статус применен')

        t = await api(user=user1)
        await t.post_ok(
            'api_admin_price_lists_make',
            json={
                'price_list_id': price_list.price_list_id,
                'drafts': [draft1.price_list_id, draft2.price_list_id],
                'mode': 'update',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_make_update_one_field(tap, api, dataset, job, lp):
    with tap.plan(18, 'Обновление прайс листа без затирания цен'):
        user1 = await dataset.user()
        user2 = await dataset.user()
        user3 = await dataset.user()

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        price_list = await dataset.price_list()
        await dataset.price_list_product(
            product=product1,
            price_list=price_list,
            price={'store': '300.12', 'markdown': '200.23'},
            user=user1,
        )
        await dataset.price_list_product(
            product=product2,
            price_list=price_list,
            price={'store': '334.26', 'markdown': '232.98'},
            user=user1,
        )

        draft = await dataset.draft_price_list(status='ready',
                                               user=user1)
        await dataset.draft_price_list_product(
            product=product1,
            price_list=draft,
            price={'markdown': 110},
            user=user2,
        )
        await dataset.draft_price_list_product(
            product=product2,
            price_list=draft,
            price={'markdown': 220},
            user=user2,
        )
        await dataset.draft_price_list_product(
            product=product3,
            price_list=draft,
            price={'markdown': 440},
            user=user2,
        )

        t = await api(user=user3)
        await t.post_ok(
            'api_admin_price_lists_make',
            json={
                'price_list_id': price_list.price_list_id,
                'drafts': [draft.price_list_id],
                'mode': 'update',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('job_id')

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Та же что в событии')

        updated = await job.call(task)
        tap.ok(updated, 'Сборка выполнена')
        tap.eq(updated.user_id, user3.user_id, 'Пользователь применивший')

        pp_list = (
            await PriceListProduct.list(
                by='look',
                conditions=('price_list_id', price_list.price_list_id),
            )
        ).list
        tap.eq(len(pp_list), 3, 'Всего записей прайс-листа')
        pp_list = dict((x.product_id, x) for x in pp_list)

        with pp_list[product1.product_id] as pp:
            tap.eq(pp.price.store, '300.12', 'Цена store не менялась')
            tap.eq(pp.price.markdown, 110, 'Цена markdown обновилась')
            tap.eq(pp.status, 'active', 'Активный')

        with pp_list[product2.product_id] as pp:
            tap.eq(pp.price.store, '334.26', 'Цена store не менялась')
            tap.eq(pp.price.markdown, 220, 'Цена markdown обновилась')
            tap.eq(pp.status, 'active', 'Активный')

        with pp_list[product3.product_id] as pp:
            tap.eq(pp.price.store, None, 'Цена store не установлена')
            tap.eq(pp.price.markdown, 440, 'Цена markdown установлена')
            tap.eq(pp.status, 'active', 'Активный')

        tap.ok(lp.exists(['system']), 'Событие отправлено')


async def test_make_replace_one_field(tap, api, dataset, job, lp):
    with tap.plan(18, 'Замена прайс листа без затирания цен'):
        user1 = await dataset.user()
        user2 = await dataset.user()
        user3 = await dataset.user()

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        price_list = await dataset.price_list()
        await dataset.price_list_product(
            product=product1,
            price_list=price_list,
            price={'store': '300.12', 'markdown': '200.23'},
            user=user1,
        )
        await dataset.price_list_product(
            product=product2,
            price_list=price_list,
            price={'store': '334.26', 'markdown': '232.98'},
            user=user1,
        )

        draft = await dataset.draft_price_list(status='ready',
                                               user=user1)
        await dataset.draft_price_list_product(
            product=product2,
            price_list=draft,
            price={'markdown': 220},
            user=user2,
        )
        await dataset.draft_price_list_product(
            product=product3,
            price_list=draft,
            price={'markdown': 440},
            user=user2,
        )

        t = await api(user=user3)
        await t.post_ok(
            'api_admin_price_lists_make',
            json={
                'price_list_id': price_list.price_list_id,
                'drafts': [draft.price_list_id],
                'mode': 'replace',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('job_id')

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Та же что в событии')

        updated = await job.call(task)
        tap.ok(updated, 'Сборка выполнена')
        tap.eq(updated.user_id, user3.user_id, 'Пользователь применивший')

        pp_list = (
            await PriceListProduct.list(
                by='look',
                conditions=('price_list_id', price_list.price_list_id),
            )
        ).list
        tap.eq(len(pp_list), 3, 'Всего записей прайс-листа (с удаленными)')
        pp_list = dict((x.product_id, x) for x in pp_list)

        with pp_list[product1.product_id] as pp:
            tap.eq(pp.price.store, '300.12', 'Цена store не менялясь')
            tap.eq(pp.price.markdown, '200.23', 'Цена markdown не менялась')
            tap.eq(pp.status, 'removed', 'Удален')

        with pp_list[product2.product_id] as pp:
            tap.eq(pp.price.store, '334.26', 'Цена store не менялась')
            tap.eq(pp.price.markdown, 220, 'Цена markdown обновилась')
            tap.eq(pp.status, 'active', 'Активный')

        with pp_list[product3.product_id] as pp:
            tap.eq(pp.price.store, None, 'Цена store не установлена')
            tap.eq(pp.price.markdown, 440, 'Цена markdown установлена')
            tap.eq(pp.status, 'active', 'Активный')

        tap.ok(lp.exists(['system']), 'Событие отправлено')


async def test_applied(tap, dataset, api, job):
    with tap:
        creator = await dataset.user()


        product1 = await dataset.product()
        product2 = await dataset.product()

        price_list = await dataset.price_list()
        await dataset.price_list_product(
            product=product1,
            price_list=price_list,
            price={'store': '300.12', 'markdown': '200.23'},
            user=creator,
        )
        await dataset.price_list_product(
            product=product2,
            price_list=price_list,
            price={'store': '334.26', 'markdown': '232.98'},
            user=creator,
        )
        user_ready_1 = await dataset.user(role='admin')
        user_ready_2 = await dataset.user(role='admin')
        logs = [
            {
                'user_id': user_ready_1.user_id,
                'status':  'ready'
            },
            {
                'user_id': user_ready_2.user_id,
                'status': 'ready'
            }
        ]
        draft = await dataset.draft_price_list(status='ready',
                                               user=creator,
                                               user_ready=user_ready_1.user_id,
                                               vars={'logs': logs}
                                               )

        t = await api()
        applied_user = await dataset.user(role='admin')
        t.set_user(applied_user)

        await t.post_ok(
            'api_admin_price_lists_make',
            json={
                'price_list_id': price_list.price_list_id,
                'drafts': [draft.price_list_id],
                'mode': 'update',
                },
            )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('job_id')

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Та же что в событии')

        updated = await job.call(task)
        tap.ok(updated, 'Сборка выполнена')
        tap.eq(updated.user_id, applied_user.user_id,
               'Пользователь применивший')

        draft = await DraftPriceList.load(draft.price_list_id)
        tap.eq(draft.user_applied, applied_user.user_id,
               ' Пользователь apply совпал')
        tap.eq(len(draft.vars['logs']), 3, 'Логирование верно')


@pytest.mark.parametrize('mode', ('update', 'replace'))
async def test_active_product(tap, api, dataset, job, mode):
    with tap.plan(8):
        product = await dataset.product()
        price_list = await dataset.price_list()

        await dataset.price_list_product(
            price_list_id=price_list.price_list_id,
            product_id=product.product_id,
            status='removed',
        )

        draft_price_list = await dataset.draft_price_list(status='ready')

        draft_product = await dataset.draft_price_list_product(
            price_list_id=draft_price_list.price_list_id,
            product_id=product.product_id,
            status='active',
            price={'store': 1984},
        )

        user = await dataset.user(role='admin')
        t = await api(user=user)

        await t.post_ok(
            'api_admin_price_lists_make',
            json={
                'price_list_id': price_list.price_list_id,
                'drafts': [draft_product.price_list_id],
                'mode': mode,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('job_id')

        task = await job.take()
        tap.eq(task.id, t.res['json']['job_id'], 'Та же что в событии')

        updated = await job.call(task)
        tap.ok(updated, 'Сборка выполнена')

        pp_list = (
            await PriceListProduct.list(
                by='look',
                conditions=('price_list_id', price_list.price_list_id),
            )
        ).list

        pp_list = dict((x.product_id, x) for x in pp_list)

        with pp_list[product.product_id] as pp:
            tap.eq(pp.price.store, 1984, 'Цена не менялась')
            tap.eq(pp.status, 'active',
                   'Статус изменился на переданный в драфт листе', )

