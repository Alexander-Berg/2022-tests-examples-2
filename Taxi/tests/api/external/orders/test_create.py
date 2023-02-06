import pytest

from stall.model.order import Order


async def test_create_token_access(tap, dataset, uuid, api):
    with tap.plan(6):
        t = await api(role='token:web.cookie.auth.name')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': uuid(),
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 123,
                                }
                            ],
                            'store_id': store.store_id
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код')
        t.json_is('message', 'Access denied')
        t.json_is('details.message',
                  'Can not find valid service token or TVM2 ticket',
                  'уточнение к коду')


@pytest.mark.parametrize('maybe_rover', [None, True, False])
@pytest.mark.parametrize('external_order_revision', [None, '', 'v1', '11'])
@pytest.mark.parametrize('total_price', [None, '23.27', '11'])
@pytest.mark.parametrize('price_type', ('store', 'markdown'))
async def test_create(tap, dataset, uuid, api,
                      price_type, total_price, external_order_revision,
                      maybe_rover):
    with tap.plan(26):
        t = await api(role='token:web.external.tokens.0')

        external_id = uuid()
        client_phone_id = uuid()

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        params = {}
        if total_price is not None:
            params['total_price'] = total_price
        if external_order_revision is not None:
            params['external_order_revision'] = external_order_revision
        if maybe_rover is not None:
            params['maybe_rover'] = maybe_rover

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 121,
                                    'price': '27.00',
                                    'price_unit': 123,
                                    'price_type': price_type,
                                }
                            ],
                            'store_id': store.store_id,
                            'approved': True,
                            'client_id': 'some_client_id',
                            'client_phone_id': client_phone_id,
                            'client_comment': 'Тест',
                            'timeout_approving': 300,
                            **params,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')

        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.external_id', external_id, 'external_id в ответе')
        t.json_is('order.status', 'reserving', 'резервируется')

        order = await Order.load(t.res['json']['order']['order_id'])
        tap.ok(order, 'ордер загружен')
        tap.eq(len(order.required), 1, 'Один товар в required')
        tap.eq(order.required[0].product_id, 'abc', 'product_id')
        tap.eq(order.required[0].price, '27.00', 'цена')
        tap.eq(order.required[0].price_unit, 123, 'Цена за всё')
        tap.eq(order.required[0].count, 121, 'количество')
        tap.eq(order.required[0].price_type, price_type, 'тип цены')
        tap.ok(order.approved, 'Подтвержден')
        tap.ok(
            300 - (order.timeout_approving - order.created).seconds <= 1,
            'Таймаут на подтверждение',
        )
        tap.eq(order.total_price, total_price, f'total_price = {total_price}')
        tap.ok(order.attr.get('doc_date'), 'doc_date is set')
        tap.ok(order.attr.get('doc_number'), 'doc_number is set')
        tap.eq(order.attr.get('doc_number').split('-')[-1],
               str(int(external_id[:6], 16))[:6].rjust(6, '0'),
               'doc_number built by external_id converted to dec')
        tap.eq(order.attr.get('client_id'), 'some_client_id', 'client_id')
        tap.eq(order.attr.get('client_phone_id'),
               client_phone_id, 'client_phone_id')
        tap.eq(order.attr.get('client_comment'), 'Тест', 'client_comment')

        if not external_order_revision:
            tap.ok('external_order_revision' not in order.vars,
                   'external_order_revision is not set')
        else:
            tap.eq(order.vars.get('external_order_revision'),
                   external_order_revision,
                   f'external_order_revision = {external_order_revision}')

        if maybe_rover is not None:
            tap.eq(order.attr['maybe_rover'], maybe_rover, 'maybe_rover_set')
        else:
            tap.ok('maybe_rover' not in order.attr, 'maybe rover not set')


@pytest.mark.parametrize(
    'status',
    ('imported', 'searching', 'searching_low', 'agreement',
     'signed', 'repair', 'closed')
)
async def test_store_unable_to_order(tap, dataset, uuid, api, status):
    with tap.plan(3, f'Склад в статусе {status} не может принимать заказы'):
        t = await api(role='token:web.external.tokens.0')

        external_id = uuid()

        store = await dataset.store(status=status)
        tap.ok(store, 'склад создан')

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 123,
                                }
                            ],
                            'store_id': store.store_id
                        })
        t.status_is(404, diag=True)


async def test_create_repeat(tap, dataset, uuid, api):
    with tap.plan(19):
        t = await api(role='token:web.external.tokens.0')

        external_id = uuid()

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        for i in range(1, 4):
            await t.post_ok('api_external_orders_create',
                            json={
                                'external_id': external_id,
                                'required': [
                                    {
                                        'product_id': 'abc',
                                        'count': 123,
                                    }
                                ],
                                'store_id': store.store_id
                            },
                            desc=f'Запрос на создание {i}')
            t.status_is(200, diag=True)
            t.json_is('code', 'OK', 'код')

            t.json_is('order.store_id', store.store_id, 'резервируется')
            t.json_is('order.external_id', external_id, 'external_id в ответе')
            t.json_is('order.status', 'reserving', 'резервируется')


@pytest.mark.parametrize('order_status',
                         ['reserving', 'approving', 'request', 'processing'])
async def test_create_processing(tap, dataset, api, order_status):
    with tap.plan(11):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        order = await dataset.order(store=store,
                                    status=order_status,
                                    required=[
                                        {
                                            'product_id': 'abc',
                                            'count': 123,
                                        }
                                    ])
        external_id = order.external_id

        tap.ok(order, 'Заказ создан')
        tap.eq(order.store_id, store.store_id, 'на складе')
        tap.ok(order.required, 'секция required заполнена')
        tap.eq(order.status, order_status, 'статус заказа')

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': order.required,
                            'store_id': order.store_id
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')

        t.json_is('order.store_id', store.store_id, 'резервируется')
        t.json_is('order.external_id', external_id, 'external_id в ответе')
        t.json_is('order.status', order_status, 'резервируется')


@pytest.mark.parametrize('order_status',
                         ['complete', 'canceled', 'failed'])
async def test_create_closed(tap, dataset, api, order_status):
    with tap.plan(
            9, 'изменение не редактируемого заказа в терминальных стадиях',
    ):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        order = await dataset.order(store=store,
                                    status=order_status,
                                    required=[
                                        {
                                            'product_id': 'abc',
                                            'count': 123,
                                        }
                                    ])
        external_id = order.external_id

        tap.ok(order, 'Заказ создан')
        tap.eq(order.store_id, store.store_id, 'на складе')
        tap.ok(order.required, 'секция required заполнена')
        tap.eq(order.status, order_status, f'статус заказа: {order_status}')
        tap.eq(order.vars('editable', False), False, 'не редактируемый')

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': order.required,
                            'store_id': order.store_id
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')


@pytest.mark.parametrize('order_status', ['complete', 'canceled', 'failed'])
async def test_create_closed_editable(tap, dataset, api, uuid, order_status):
    with tap.plan(
            13, 'изменение редактируемого заказа в терминальных стадиях',
    ):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        order = await dataset.order(
            store=store,
            status=order_status,
            required=[
                {
                    'product_id':  uuid(),
                    'count': 300,
                },
            ],
            vars={'editable': True},
        )

        tap.ok(order, 'Заказ создан')
        tap.eq(order.store_id, store.store_id, 'на складе')
        tap.ok(order.required, 'секция required заполнена')
        tap.eq(order.status, order_status, f'статус заказа: {order_status}')
        tap.eq(order.vars('editable', False), True, 'редактируемый')

        await t.post_ok(
            'api_external_orders_create',
            json={
                'external_id': order.external_id,
                'store_id': order.store_id,
                'required': order.required,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'если заказ не изменился, то все ок')

        await t.post_ok(
            'api_external_orders_create',
            json={
                'external_id': order.external_id,
                'store_id': order.store_id,
                'required': [
                    {
                        'product_id': uuid(),
                        'count': 300,
                    },
                ],
            }
        )
        t.status_is(410, diag=True)
        t.json_is(
            'code',
            'ER_GONE',
            'если заказ хотят изменить в терминальной стадии, то не разрешаем',
        )
        t.json_is('message', 'Order has already done', 'сообщение')


async def test_create_with_doc_number(tap, dataset, uuid, api):
    with tap.plan(18):
        t = await api(role='token:web.external.tokens.0')

        external_id = uuid()

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        doc_number = 'externally_provided_doc_number'
        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 121,
                                    'price': '27.00',
                                    'price_unit': 123,
                                    'price_type': 'store',
                                }
                            ],
                            'store_id': store.store_id,
                            'approved': True,
                            'client_id': 'some_client_id',
                            'doc_number': doc_number,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')

        t.json_is('order.store_id', store.store_id, 'резервируется')
        t.json_is('order.external_id', external_id, 'external_id в ответе')
        t.json_is('order.status', 'reserving', 'резервируется')

        order = await Order.load(t.res['json']['order']['order_id'])
        tap.ok(order, 'ордер загружен')
        tap.eq(len(order.required), 1, 'Один товар в required')
        tap.eq(order.required[0].product_id, 'abc', 'product_id')
        tap.eq(order.required[0].price, '27.00', 'цена')
        tap.eq(order.required[0].price_unit, 123, 'Цена за всё')
        tap.eq(order.required[0].count, 121, 'количество')
        tap.eq(order.required[0].price_type, 'store', 'тип цены')
        tap.ok(order.approved, 'Подтвержден')
        tap.ok(order.attr.get('doc_date'), 'doc_date is set')
        tap.eq_ok(order.attr.get('doc_number'),
                  doc_number, 'doc_number is set externally')
        tap.eq(order.attr.get('client_id'),
               'some_client_id', 'client_id is set')


async def test_create_vat_discount(tap, dataset, uuid, api):
    with tap.plan(14):
        t = await api(role='token:web.external.tokens.0')

        external_id = uuid()

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        doc_number = 'externally_provided_doc_number'
        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 121,
                                    'price': '27.00',
                                    'price_unit': 123,
                                    'price_type': 'store',

                                    'discount': '12.11',
                                    'vat': '3.2',
                                }
                            ],
                            'store_id': store.store_id,
                            'approved': True,
                            'client_id': 'some_client_id',
                            'doc_number': doc_number,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')

        t.json_is('order.store_id', store.store_id, 'резервируется')
        t.json_is('order.external_id', external_id, 'external_id в ответе')
        t.json_is('order.status', 'reserving', 'резервируется')

        order = await Order.load(t.res['json']['order']['order_id'])
        tap.ok(order, 'ордер загружен')
        tap.eq(len(order.required), 1, 'Один товар в required')
        tap.eq(order.required[0].product_id, 'abc', 'product_id')
        tap.eq(order.required[0].price, '27.00', 'цена')
        tap.eq(order.required[0].price_unit, 123, 'Цена за всё')
        tap.eq(order.required[0].discount, '12.11', 'скидка')
        tap.eq(order.required[0].vat, '3.20', 'НДС')


async def test_dispatch(tap, dataset, uuid, api):
    with tap.plan(7, 'Проверка настроек диспетчеризации заказа'):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': uuid(),
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 121,
                                    'price': '27.00',
                                    'price_unit': 123,
                                }
                            ],
                            'store_id': store.store_id,
                            'approved': True,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')

        order = await Order.load(t.res['json']['order']['order_id'])
        tap.ok(order, 'ордер загружен')
        tap.eq(order.dispatch_type, 'external', 'dispatch_type')
        tap.eq(order.courier_id, None, 'courier_id')
        tap.eq(order.courier_pri, None, 'courier_pri')


@pytest.mark.parametrize('client_tags', [None, ['tag1', 'tag2']])
async def test_client_tags(tap, dataset, uuid, api, client_tags):
    with tap.plan(11):
        t = await api(role='token:web.external.tokens.0')

        external_id = uuid()
        client_phone_id = uuid()

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        params = {}
        if client_tags is not None:
            params['client_tags'] = client_tags

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 121,
                                    'price': '27.00',
                                    'price_unit': 123,
                                    'price_type': 'store',
                                }
                            ],
                            'store_id': store.store_id,
                            'approved': True,
                            'client_id': 'some_client_id',
                            'client_phone_id': client_phone_id,
                            'client_comment': 'Тест',
                            'timeout_approving': 300,
                            **params,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'OK status')

        order = await Order.load(t.res['json']['order']['order_id'])
        tap.ok(order, 'ордер загружен')

        if client_tags is not None:
            tap.eq(order.attr.get('client_tags'), client_tags, 'client_tags')
        else:
            tap.ok('client_tags' not in order.attr, 'client_tags not set')

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 121,
                                    'price': '27.00',
                                    'price_unit': 123,
                                    'price_type': 'store',
                                }
                            ],
                            'store_id': store.store_id,
                            'approved': True,
                            'client_id': 'some_client_id',
                            'client_phone_id': client_phone_id,
                            'client_comment': 'Тест',
                            'timeout_approving': 300,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'OK status, order updated')

        tap.ok(await order.reload(), 'ордер перезагружен')

        if client_tags is not None:
            tap.eq(order.attr.get('client_tags'), client_tags,
                   'client_tags did not change')
        else:
            tap.ok('client_tags' not in order.attr, 'client_tags not set')


@pytest.mark.parametrize('logistic_tags_v1, logistic_tags_v2',
                         [([], ['tag2', 'tag3']), (['tag1'], [])])
async def test_logistic_tags(
        tap, dataset, uuid, api, logistic_tags_v1, logistic_tags_v2):
    with tap.plan(15, 'logistic_tags создается и обновляется'):
        t = await api(role='token:web.external.tokens.0')

        external_id = uuid()
        client_phone_id = uuid()

        store = await dataset.store()

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 121,
                                    'price': '27.00',
                                    'price_unit': 123,
                                    'price_type': 'store',
                                }
                            ],
                            'store_id': store.store_id,
                            'approved': True,
                            'editable': False,
                            'client_id': 'some_client_id',
                            'client_phone_id': client_phone_id,
                            'client_comment': 'Тест',
                            'timeout_approving': 300,
                            'logistic_tags': logistic_tags_v1
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        order = await Order.load(t.res['json']['order']['order_id'])
        tap.ok(order, 'ордер загружен')

        tap.eq(
            order.attr.get('logistic_tags'),
            logistic_tags_v1,
            'logistic_tags created'
        )

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 121,
                                    'price': '27.00',
                                    'price_unit': 123,
                                    'price_type': 'store',
                                }
                            ],
                            'store_id': store.store_id,
                            'approved': True,
                            'client_id': 'some_client_id',
                            'client_phone_id': client_phone_id,
                            'client_comment': 'Тест',
                            'timeout_approving': 300,
                            'logistic_tags': logistic_tags_v2
                        })
        t.status_is(200, diag=True)
        t.json_is(
            'code', 'OK', 'OK status, order updated'
        )

        tap.ok(await order.reload(), 'ордер перезагружен')
        tap.eq(
            order.attr.get('logistic_tags'),
            logistic_tags_v2,
            'logistic_tags updated'
        )

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': 'abc',
                                    'count': 121,
                                    'price': '27.00',
                                    'price_unit': 123,
                                    'price_type': 'store',
                                }
                            ],
                            'store_id': store.store_id,
                            'approved': True,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await order.reload(), 'ордер перезагружен')
        tap.eq(
            order.attr.get('logistic_tags'),
            logistic_tags_v2,
            'logistic_tags is not updated'
        )


async def test_reset_pause_on_change(tap, dataset, api, uuid):
    with tap.plan(10, 'не сносим паузу при редактировании заказа'):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            status='processing',
            required=[
                {
                    'product_id':  uuid(),
                    'count': 300,
                },
            ],
            vars={'editable': True},
        )

        tap.ok(order.paused_until is None, 'пауза не выставлена')

        await t.post_ok(
            'api_external_orders_create',
            json={
                'external_id': order.external_id,
                'store_id': order.store_id,
                'required': [
                    {
                        'product_id': uuid(),
                        'count': 300,
                    },
                ],
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await order.reload()
        tap.ok(order.paused_until is None, 'пауза не выставлена')

        order.set_paused_until(30)
        await order.save()
        tap.ok(order.paused_until, 'пауза выставлена')

        first_paused_until = order.paused_until

        await t.post_ok(
            'api_external_orders_create',
            json={
                'external_id': order.external_id,
                'store_id': order.store_id,
                'required': [
                    {
                        'product_id': uuid(),
                        'count': 300,
                    },
                ],
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await order.reload()
        tap.eq(order.paused_until, first_paused_until, 'не убрали паузу')


async def test_company(tap, dataset, api, uuid):
    with tap.plan(5, 'Создание ордера в компании, по ее ключу'):

        company = await dataset.company()
        store = await dataset.store(company=company)

        external_id = uuid()

        t = await api(token=company.token)
        await t.post_ok(
            'api_external_orders_create',
            json={
                'external_id': external_id,
                'required': [
                    {
                        'product_id': 'abc',
                        'count': 121,
                        'price': '27.00',
                        'price_unit': 123,
                        'price_type': 'store',
                    }
                ],
                'store_id': store.store_id,
                'approved': True,
                'client_id': 'some_client_id',
                'client_phone_id': uuid(),
                'client_comment': 'Тест',
                'timeout_approving': 300,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.external_id', external_id)
        t.json_is('order.company_id', company.company_id)


async def test_out_of_company(tap, dataset, api, uuid):
    with tap.plan(6, 'Попытка создать ордер в лавке другой компании'):
        company_1 = await dataset.company()
        company_2 = await dataset.company()
        store = await dataset.store(company=company_2)
        json = {
            'external_id': uuid(),
            'required': [
                {
                    'product_id': 'abc',
                    'count': 121,
                    'price': '27.00',
                    'price_unit': 123,
                    'price_type': 'store',
                }
            ],
            'store_id': store.store_id,
            'approved': True,
            'client_id': 'some_client_id',
            'client_phone_id': uuid(),
            'client_comment': 'Тест',
            'timeout_approving': 300,
        }

        # создание через токен компании
        t = await api(token=company_1.token)
        await t.post_ok('api_external_orders_create', json=json)
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        # создание через токен из Секретницы (компания не проверяется)
        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_orders_create', json=json)
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
