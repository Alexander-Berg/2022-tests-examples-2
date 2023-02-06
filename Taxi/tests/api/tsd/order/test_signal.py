from datetime import timedelta
import pytest
from stall.model.suggest import Suggest


async def test_signal(tap, dataset, api):
    with tap.plan(8, 'штатная отправка сигнала'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            type='acceptance',
            store=store,
            status='processing',
            estatus='waiting',
        )
        tap.eq(order.store_id, store.store_id, 'ордер на складе создан')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'acceptance_agree',
                        })
        t.status_is(200, diag=True)

        await order.reload()
        tap.eq(len(order.signals), 1, '1 сигнал записан')
        tap.eq(order.signals[0]['type'], 'acceptance_agree', 'тип сигнала')
        tap.eq(order.signals[0]['user_id'],
               user.user_id,
               'user_id совпал с текущим пользователем')


async def test_signal_access(tap, dataset, api):
    with tap.plan(7, 'отправка неправильному типу ордера'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(type='order', store=store)
        tap.eq(order.store_id, store.store_id, 'ордер на складе создан')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'acceptance_agree',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message',
                  'Type "order" can not receive signal "acceptance_agree"')


async def test_signal_more_product_ss(tap, dataset, api):
    with tap.plan(18, 'штатная отправка сигнала more_product для раскладки'):
        store = await dataset.store(options={'exp_schrodinger': False})
        tap.ok(store, 'склад создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(type='sale_stowage',
                                    store=store,
                                    status='reserving',
                                    estatus='begin',
                                    )
        tap.eq(order.store_id, store.store_id, 'ордер на складе создан')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'more_product',
                            'data': {
                                'product_id': product.product_id,
                                'count': 27,
                            }
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Order is not waiting')

        products = await dataset.weight_products()
        tap.eq(len(products), 3 + 1, '3 детей и родитель')

        order = await dataset.order(type='sale_stowage',
                                    store=store,
                                    status='processing',
                                    estatus='waiting',
                                    required=[
                                        {
                                            'product_id':
                                                products[1].product_id,
                                            'count': 2,
                                        }
                                    ]
                                    )
        tap.eq(order.store_id, store.store_id, 'ордер на складе создан')
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'more_product',
                            'data': {
                                'product_id': products[3].product_id,
                                'count': 27,
                            }
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message',
                  'Can not pass weight product '
                  'not from required '
                  'in more_product'
                  )
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'more_product',
                            'data': {
                                'product_id': products[1].product_id,
                                'count': 27,
                            }
                        })
        t.status_is(200, diag=True)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'more_product',
                            'data': {
                                'product_id': product.product_id,
                                'count': 27,
                            }
                        })
        t.status_is(200, diag=True)


async def test_signal_more_product_ws(tap, dataset, api):
    with tap.plan(15, 'штатная отправка сигнала more_product'
                      'для весовой раскладки'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        product1 = await dataset.weight_products()
        tap.ok(product1, 'товар создан')
        product2 = await dataset.weight_products()
        tap.ok(product2, 'товар создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(
            type='weight_stowage',
            store=store,
            status='processing',
            estatus='waiting',
            required=[
                {
                    'product_id': product1[0].product_id,
                    'weight': 5000,
                }
            ],
        )
        tap.eq(order.store_id, store.store_id, 'ордер на складе создан')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'more_product',
                            'data': {
                            }
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'The product required for more_product')

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'more_product',
                            'data': {
                                'product_id': product2[0].product_id,
                            }
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'The product is not required for weight stowage')

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'more_product',
                            'data': {
                                'product_id': product1[0].product_id,
                            }
                        })
        t.status_is(200, diag=True)


async def test_signal_order_stat(tap, dataset, api, wait_order_status, now):
    with tap.plan(13, 'Отправка статистики в order'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock = await dataset.stock(store=store, count=234)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')

        order = await dataset.order(
            type='order',
            store=store,
            acks=[user.user_id],
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 12
                }
            ],
            approved=now(),
            attr={
                'hello': 'world',
            }
        )
        tap.eq(order.store_id, store.store_id, 'ордер на складе создан')
        tap.in_ok('hello', order.attr, 'начальное заполнение attr')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'stat',
                            'data': {
                                'truck_temperature': 123,
                            }
                        })
        t.status_is(200, diag=True)

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.in_ok('stat', order.attr, 'статистика сохранена')
        tap.eq(
            order.attr['stat'],
            {'truck_temperature': 123},
            'статистика сохранена'
        )

        tap.in_ok('hello', order.attr, 'начальное заполнение attr')
        tap.eq(order.attr['hello'], 'world', 'значение')


async def test_shortfall(tap, dataset, wait_order_status, now, api, uuid):
    with tap.plan(16, 'Отправка сигнала shortfall'):
        product1 = await dataset.product()
        product2 = await dataset.product()

        store = await dataset.store()
        user = await dataset.user(store=store)

        await dataset.stock(product=product1, store=store,
                            count=10)
        await dataset.stock(product=product2, store=store,
                            count=12)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            total_price='1230.00',
            approved=now(),
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 6
                },
            ],

        )

        await wait_order_status(
            order,
            ('processing', 'begin'),
            user_done=user,
        )

        t = await api(user=user)

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'shortfall',
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Field data.suggest_id is '
                             'required for shortfall signal')

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'shortfall',
                            'data': {'suggest_id': uuid()},
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Suggest not found')

        suggests = await Suggest.list_by_order(order)
        data = [{'suggest_id': s.suggest_id,
                 'source': 'sherlock'} for s in suggests]
        tap.eq_ok(len(data), 1, '1 suggests')

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'shortfall',
                            'data': data[0],
                        })
        t.status_is(200, diag=True)

        await order.reload()
        tap.eq_ok(len(order.signals), 1, '1 signal in order')
        tap.eq_ok(order.signals[0].type, 'shortfall', 'type=shortfall')
        tap.eq_ok(order.signals[0].data['suggest_id'], suggests[0].suggest_id,
                  'correct suggest_id')
        tap.eq_ok(order.signals[0].data['source'], 'sherlock', 'source')


async def test_weight(tap, dataset, api, wait_order_status):
    with tap.plan(19, 'Доверительная приёмка с проверкой вес товара'):
        store = await dataset.full_store()
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        weight = await dataset.weight_products()

        order = await dataset.order(
            store=store,
            type='acceptance',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],

            required=[
                {
                    'product_id': weight[0].product_id,
                    'count': 27,
                }
            ]
        )

        tap.eq(order.store_id, store.store_id, 'ордер сгенерирован')
        tap.eq(order.type, 'acceptance', 'тип')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'acceptance_agree',
                        })

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SUGGEST_WEIGHT_REQUIRED')
        t.json_is('message', 'For acceptance_agree need '
                             'to close all parent weight suggest')

        await suggests[0].done(count=10, weight=1000)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'acceptance_agree',
                        })

        t.status_is(200, diag=True)

        await wait_order_status(order, ('complete', 'done'))

        stowage = await dataset.Order.load(order.vars('stowage_id'))
        tap.ok(stowage, 'раскладка сгенерирована')
        tap.eq(len(stowage.required), 1, 'Одна запись required')
        required = stowage.required[0]

        tap.eq(required.count, 10, 'число по закрытому')
        tap.eq(required.weight, 1000, 'вес по закрытому')
        tap.eq(required.product_id, weight[0].product_id, 'продукт')


async def test_acc_weight_child(tap, dataset, api, wait_order_status):
    with tap.plan(12, 'Доверительная приёмка для весового'):
        store = await dataset.full_store()
        user = await dataset.user(store=store)
        weight = await dataset.weight_products()
        child = weight[-1]

        order = await dataset.order(
            store=store,
            type='acceptance',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],

            required=[
                {
                    'product_id': child.product_id,
                    'count': 27,
                    'weight': 10000,
                }
            ]
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджест')

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_signal',
            json={
                'order_id': order.order_id,
                'signal': 'acceptance_agree',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await wait_order_status(order, ('complete', 'done'))

        stowage = await dataset.Order.load(order.vars('stowage_id'))
        tap.ok(stowage, 'раскладка сгенерирована')
        tap.eq(stowage.type, 'sale_stowage', 'Обычная раскладка')
        tap.eq(len(stowage.required), 1, 'Одна запись required')
        required = stowage.required[0]

        tap.eq(required.count, 27, 'число по required')
        tap.eq(required.weight, 10000, 'вес по required')
        tap.eq(required.product_id, child.product_id, 'продукт')


@pytest.mark.parametrize('types',
                         [
                             'writeoff_prepare_day',
                             'check_valid_regular',
                             'check_valid_short',
                         ]
                         )
async def test_check_valid(tap, dataset, api, types):
    with tap.plan(11, 'Сигнал в КСГ'):
        store = await dataset.full_store()
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        order = await dataset.order(
            store=store,
            type=types,
            status='processing',
            estatus='waiting',
            acks=[user.user_id],
            vars={}
        )

        tap.eq(order.store_id, store.store_id, 'ордер сгенерирован')
        tap.eq(order.type, types, 'тип')
        tap.eq(order.fstatus, ('processing', 'waiting'), 'статус')

        suggest = await dataset.suggest(
            order.order_id,
            status='request'
        )

        t = await api(user=user)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'next_stage',
                        })

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'ER_BAD_REQUEST')
        t.json_is('message', 'Some suggests still in request. '
                             'Close all request suggests.')

        await suggest.done()

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'next_stage',
                        })

        t.status_is(200, diag=True)


async def test_complete_final_stage_vc(tap, dataset, api, wait_order_status):
    with tap.plan(6, 'Отправка сигнала complete_final_stage'
                     ' для visual control'):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')
        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='visual_control',
            status='processing',
            estatus='begin',
            acks=[user.user_id]
        )
        tap.eq(order.store_id, store.store_id, 'создали ордер')
        t = await api(user=user)

        await wait_order_status(order, ('processing', 'waiting'))

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'complete_final_stage',
                        })
        t.status_is(200, diag=True)


async def test_complete_final_stage_cvr(tap, dataset, api, wait_order_status):
    with tap.plan(6, 'Отправка сигнала complete_final_stage'
                     ' для check valid regular'):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')
        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='check_valid_regular',
            status='processing',
            estatus='begin',
            acks=[user.user_id]
        )
        tap.eq(order.store_id, store.store_id, 'создали ордер')
        t = await api(user=user)

        await wait_order_status(order, ('processing', 'waiting'))

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'complete_final_stage',
                        })

        t.status_is(200, diag=True)


async def test_complete_final_acceptance(tap, dataset, api, wait_order_status):
    with tap.plan(6, 'Отправка сигнала complete_final_stage'
                     ' для acceptance не должна работать'):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')
        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='acceptance',
            status='processing',
            estatus='begin',
            acks=[user.user_id]
        )
        tap.eq(order.store_id, store.store_id, 'создали ордер')
        t = await api(user=user)

        await wait_order_status(order, ('processing', 'waiting'))

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'complete_final_stage',
                        })
        t.status_is(400, diag=True)


@pytest.mark.parametrize(
    'role',
    [
        'support_it',
        'chief_audit',
        'company_admin',
        'admin',
    ]
)
async def test_order_defibrillation(tap,  dataset, api, now, role):
    with tap.plan(8, 'Роли, которые могут реанимировать заказ'):
        store = await dataset.full_store()
        tap.ok(store, 'склад сгенерирован')
        user = await dataset.user(role=role, store=store)
        tap.ok(user, 'пользователь')

        order = await dataset.order(
            store=store,
            type='acceptance',
            status='failed',
            estatus='done',
            acks=[user.user_id],
            vars={}
        )

        t = await api(user=user)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'order_defibrillation',
                        })

        t.status_is(200, diag=True)

        order.created = now() - timedelta(days=10)
        await order.save()

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'order_defibrillation',
                        })

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ORDER_IS_NOT_REANIMATED',
                  'ER_ORDER_IS_NOT_REANIMATED')
        t.json_is('message', 'Order cannot be defibrillated')


async def test_sale_stowage_next_stage(tap, dataset, api, wait_order_status):
    with tap.plan(14, 'тестим переход на стадию списания в раскладке'):
        store = await dataset.full_store(options={'exp_freegan_party': True})
        product = await dataset.product()
        user = await dataset.user(store=store, role='admin')

        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[{
                'product_id': product.product_id,
                'count': 3,
                'maybe_count': True,
            }],
        )
        await wait_order_status(order, ('processing', 'waiting'))

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_signal',
            json={
                'order_id': order.order_id,
                'signal': 'sale_stowage',
            }
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_TRASH_STAGE_DISABLED')
        t.json_is(
            'message',
            'Trash stage is disabled in this store (exp_freegan_party)',
        )
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.vars('stage'), 'stowage', 'стадия осталась прежней')

        store_options = store.options.copy()
        store_options['exp_freegan_party'] = False
        store.options = store_options
        await store.save()
        await store.reload()
        tap.ok(not store.options['exp_freegan_party'], 'выключили эксперимент')
        await t.post_ok(
            'api_tsd_order_signal',
            json={
                'order_id': order.order_id,
                'signal': 'sale_stowage',
            }
        )
        t.status_is(200, diag=True)
        await wait_order_status(order, ('processing', 'stowage_signals'))
        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()
        tap.eq(order.vars('stage'), 'trash', 'перешли в стадию списания')
        await wait_order_status(order, ('complete', 'done'), user_done=user)


async def test_ws_next_stage(tap,  dataset, api, wait_order_status):
    with tap.plan(21, 'Сигнал перехода на стадию'):
        store = await dataset.full_store(options={'exp_chicken_run': True})
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        child_weights = [
            [0, 10],
            [10, 20],
            [20, 30]
        ]

        products = await dataset.weight_products(children=child_weights)
        tap.eq(len(products), 3 + 1, '3 детей и родитель')

        products_2 = await dataset.weight_products()
        tap.eq(len(products_2), 3 + 1, '3 детей и родитель другой группы')

        shelves = [await dataset.shelf(store=store) for s in range(5)]
        tap.eq(len(shelves), 5, 'несколько полок создано')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': products[0].product_id,
                    'weight': 5000,
                    'count': 3,
                }
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order,
                                                       types=['shelf2box'],
                                                       status='request'
                                                       )
        tap.eq(len(suggests), 1, 'один саджест возьми с полки')
        with suggests[0] as s:
            tap.ok(
                await s.done(
                    weight=20,
                    count=3,
                ),
                'закрыт саджест'
            )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order,
                                                       types=['box2shelf'],
                                                       status='request'
                                                       )
        tap.eq(len(suggests), 1, 'один саджест положи на полку')
        t = await api(user=user)

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'sale_stowage',
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message',
                  'Need to close all b2s suggests')

        with suggests[0] as s:
            tap.ok(
                await s.done(
                    weight=20,
                    count=3,
                ),
                'закрыт саджест'
            )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order,
                                                       types=['box2shelf'],
                                                       status='request'
                                                       )
        tap.eq(len(suggests), 0, 'нет саджестов положи на полку')

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'sale_stowage',
                        })
        t.status_is(200, diag=True)
        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()
        tap.eq(order.vars['stage'], 'trash', 'стадия изменилась')


async def test_next_stage_hand_move(tap, dataset, api, wait_order_status):
    with tap.plan(11, 'проверяем работу next_stage в hand_move'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        shelves = [await dataset.shelf(store=store) for _ in range(2)]
        products = [await dataset.product() for _ in range(2)]
        for shelf in shelves:
            for product in products:
                await dataset.stock(count=100, product=product, shelf=shelf)
        order = await dataset.order(
            store=store,
            type='hand_move',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            required=[
                {
                    'product_id': products[0].product_id,
                    'src_shelf_id': shelves[0].shelf_id,
                    'dst_shelf_id': shelves[1].shelf_id,
                    'count': 40,
                },
                {
                    'product_id': products[1].product_id,
                    'src_shelf_id': shelves[1].shelf_id,
                    'dst_shelf_id': shelves[0].shelf_id,
                    'count': 60,
                },
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()

        suggests = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggests), 2, '2 саджеста shelf2box')
        await suggests[0].done()

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_signal',
            json={
                'order_id': order.order_id,
                'signal': 'next_stage',
            },
        )
        t.status_is(400)
        await suggests[1].done()
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_signal',
            json={
                'order_id': order.order_id,
                'signal': 'next_stage',
            },
        )
        t.status_is(200)
        await order.reload()
        await wait_order_status(order, ('processing', 'close_next_stage'))
        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()
        suggests = await dataset.Suggest.list_by_order(order=order)
        tap.eq(len(suggests), 4, '4 саджеста')
        tap.eq(
            len([s for s in suggests if s.type == 'box2shelf']),
            2,
            '2 саджеста box2shelf'
        )
        await wait_order_status(order, ('complete', 'done'), user_done=user)


async def test_order_stat(tap, dataset, wait_order_status, now, api):
    with tap.plan(9, 'Отправка сигнала stat с уникальным ключом'):
        product1 = await dataset.product()
        product2 = await dataset.product()

        store = await dataset.store()
        user = await dataset.user(store=store)

        await dataset.stock(product=product1, store=store,
                            count=10)
        await dataset.stock(product=product2, store=store,
                            count=12)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            total_price='1230.00',
            approved=now(),
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 6
                },
                {
                    'product_id': product2.product_id,
                    'count': 3
                },
            ],

        )

        await wait_order_status(
            order,
            ('processing', 'begin'),
            user_done=user,
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq_ok(len(suggests), 2, '1 suggests')

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_signal',
            json={
                'order_id': order.order_id,
                'signal': 'stat',
                'data': {
                    suggests[0].suggest_id: {'count': 2,
                                             'duration': 0}
                }
            })
        t.status_is(200, diag=True)

        await t.post_ok(
            'api_tsd_order_signal',
            json={
                'order_id': order.order_id,
                'signal': 'stat',
                'data': {
                    suggests[1].suggest_id: {'count': 10,
                                             'duration': 0.25}
                }
            })
        t.status_is(200, diag=True)

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.in_ok('stat', order.attr, 'статистика сохранена')
        tap.eq(
            order.attr['stat'],
            {suggests[0].suggest_id: {'count': 2,
                                      'duration': 0},
             suggests[1].suggest_id: {'count': 10,
                                      'duration': 0.25}},
            'статистика сохранена'
        )
