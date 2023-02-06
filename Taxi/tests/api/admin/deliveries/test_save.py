import pytest


async def test_save_exists(tap, dataset, api, uuid):
    with tap.plan(14):
        store       = await dataset.store()
        provider    = await dataset.provider(stores=[store.store_id])
        delivery    = await dataset.delivery(store=store, provider=provider)
        user        = await dataset.user(store=store)

        t = await api(user=user)

        dc_doc_number = uuid()

        tap.note('Редактирование')
        await t.post_ok('api_admin_deliveries_save',
                        json={
                            'delivery_id': delivery.delivery_id,
                            'attr_dc': {
                                'units': 1,
                                'doc_number': dc_doc_number,
                                'comment': 'тест',
                            }
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('delivery.updated', 'updated')
        t.json_has('delivery.created', 'created')
        t.json_is('delivery.attr_dc.units', 1, 'units')
        t.json_is('delivery.attr_dc.doc_number', dc_doc_number, 'doc_number')
        t.json_is('delivery.attr_dc.comment', 'тест', 'comment')

        tap.note('Редактирование')
        await t.post_ok('api_admin_deliveries_save',
                        json={
                            'delivery_id': delivery.delivery_id,
                            'attr_dc': {
                                'units': 2,
                            }
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('delivery.attr_dc.units', 2, 'units')
        t.json_is('delivery.attr_dc.doc_number', None, 'doc_number')
        t.json_is('delivery.attr_dc.comment', None, 'comment')


async def test_save_unexists(tap, dataset, api, uuid, now):
    with tap.plan(17):
        store       = await dataset.store()
        provider    = await dataset.provider(stores=[store.store_id])
        user        = await dataset.user(store=store)

        title       = f'Поставка {uuid()}'
        external_id = uuid()
        plan_date   = now().date()

        tap.note('Сохранение')
        t = await api(user=user)
        await t.post_ok('api_admin_deliveries_save',
                        json={
                            'external_id': external_id,
                            'provider_id': provider.provider_id,
                            'title': title,
                            'tags': ['freezer'],
                            'attr': {'units': 1},
                            'car': {'number': 'ББ11БББ'},
                            'driver': {'name': 'ААА'},
                            'plan_date': plan_date,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        delivery_id = t.res['json']['delivery']['delivery_id']

        t.json_has('delivery.delivery_id', 'delivery_id')
        t.json_is('delivery.external_id', external_id, 'external_id')
        t.json_is('delivery.store_id', store.store_id, 'store_id')
        t.json_is('delivery.provider_id', provider.provider_id, 'provider_id')
        t.json_is('delivery.status', 'request', 'status: request')
        t.json_is('delivery.user_id', user.user_id)
        t.json_has('delivery.plan_date', plan_date)
        t.json_has('delivery.updated', 'updated')
        t.json_has('delivery.created', 'created')
        t.json_is('delivery.title', title)

        tap.note('Редактирование')
        await t.post_ok('api_admin_deliveries_save',
                        json={
                            'delivery_id': delivery_id,
                            'attr_dc': {
                                'units': 2,
                            }
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('delivery.attr_dc.units', 2, 'units')


async def test_save_readonly(tap, dataset, api, uuid):
    with tap.plan(5, 'Проверка сохранения полей только для чтения'):

        store       = await dataset.store()
        provider    = await dataset.provider(stores=[store.store_id])
        delivery    = await dataset.delivery(store=store, provider=provider)
        user        = await dataset.user(store=store)

        t = await api(user=user)

        await t.post_ok('api_admin_deliveries_save',
                        json={
                            'delivery_id': delivery.delivery_id,
                            'title': uuid(),
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_READONLY_AFTER_CREATE')

        tap.note('Остальные поля сохраняются нормально')
        await t.post_ok(
            'api_admin_deliveries_save',
            json={
                'attr': {
                    'units': 12,
                    'doc_number': 'asd',
                    'comment': 'asdasd',
                },
                'attr_dc': {
                    'units': 12,
                    'doc_number': 'asd',
                    'comment': 'asdasd',
                },
                'comment': 'asdasd',
                'doc_number': 'asd',
                'units': 12,
                'delivery_id': delivery.delivery_id,
            }

        )
        t.status_is(200, diag=True)


@pytest.mark.parametrize('role', ['store_admin'])
async def test_save_not_my(tap, dataset, api, role):
    with tap.plan(2, 'Не своя доставка'):
        store       = await dataset.store()
        provider    = await dataset.provider(stores=[store.store_id])
        user        = await dataset.user(store=store, role=role)

        store2      = await dataset.store()
        delivery    = await dataset.delivery(store=store2, provider=provider)

        t = await api(user=user)

        await t.post_ok('api_admin_deliveries_save',
                        json={
                            'delivery_id': delivery.delivery_id,
                            'attr': {'units': 1},
                            'car': {'number': 'ББ11БББ'},
                            'driver': {'name': 'ААА'},
                            'attr_dc': {'comment': 'тест'},
                        })
        t.status_is(403, diag=True)


async def test_save_done(tap, dataset, api, uuid):
    with tap.plan(2, 'Завершонную поставку редактировать нельзя'):
        store       = await dataset.store()
        provider    = await dataset.provider(stores=[store.store_id])
        delivery    = await dataset.delivery(
            store=store,
            provider=provider,
            status='complete',
        )
        user        = await dataset.user(store=store)

        t = await api(user=user)

        dc_doc_number = uuid()

        await t.post_ok('api_admin_deliveries_save',
                        json={
                            'delivery_id': delivery.delivery_id,
                            'attr_dc': {
                                'units': 1,
                                'doc_number': dc_doc_number,
                                'comment': 'тест',
                            }
                        })
        t.status_is(410, diag=True)
