from stall import lp


async def test_set_count(api, tap, dataset, uuid):
    with tap:
        store = await dataset.store(messages_count=0)
        tap.eq_ok(store.messages_count, 0, 'Messages count is 0')
        old_lsn = store.lsn

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok('api_external_stores_set_messages_count',
                        json={
                            'store_id': store.store_id,
                            'count_change': 23,
                            'token': uuid(),
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('messages_count', 23)
        await store.reload()
        tap.eq_ok(store.messages_count, 23, 'Messages count set correctly')
        tap.ok(
            lp.exists(['store', store.store_id], {
                'type': 'messages_count',
                'count': 23,
            }),
            'Event exists'
        )
        await store.reload()
        tap.eq_ok(store.lsn, old_lsn, 'lsn did not change')

        await t.post_ok('api_external_stores_set_messages_count',
                        json={
                            'store_id': store.store_id,
                            'count_change': -3,
                            'token': uuid(),
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('messages_count', 20)
        await store.reload()
        tap.eq_ok(store.messages_count, 20, 'Messages count set correctly')
        tap.ok(
            lp.exists(['store', store.store_id], {
                'type': 'messages_count',
                'count': 20,
            }),
            'Event exists'
        )
        await store.reload()
        tap.eq_ok(store.lsn, old_lsn, 'lsn did not change')


async def test_list_company_forbidden(tap, dataset, api, uuid):
    with tap.plan(3, 'Нельзя выставлять число сообщений не на своем складе'):
        company1 = await dataset.company()
        company2 = await dataset.company()
        store2 = await dataset.store(company=company2, messages_count=0)

        t = await api(token=company1.token)

        await t.post_ok('api_external_stores_set_messages_count',
                        json={
                            'store_id': store2.store_id,
                            'count_change': 23,
                            'token': uuid(),
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_list_company_unknown(tap, dataset, api, uuid):
    with tap.plan(3, 'неизвестный идентификатор склада'):
        company1 = await dataset.company()

        t = await api(token=company1.token)

        await t.post_ok('api_external_stores_set_messages_count',
                        json={
                            'store_id': uuid(),
                            'count_change': 23,
                            'token': uuid(),
                        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')


async def test_idempotency(api, tap, dataset, uuid):
    with tap:
        store = await dataset.store(messages_count=10)
        tap.eq_ok(store.messages_count, 10, 'Messages count is 10')
        old_lsn = store.lsn
        token = uuid()

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok('api_external_stores_set_messages_count',
                        json={
                            'store_id': store.store_id,
                            'count_change': -3,
                            'token': token,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('messages_count', 7)
        await store.reload()
        tap.eq_ok(store.messages_count, 7, 'Messages count set correctly')
        tap.ok(
            lp.exists(['store', store.store_id], {
                'type': 'messages_count',
                'count': 7,
            }),
            'Event exists'
        )
        await store.reload()
        tap.eq_ok(store.lsn, old_lsn, 'lsn did not change')

        await t.post_ok('api_external_stores_set_messages_count',
                        json={
                            'store_id': store.store_id,
                            'count_change': -3,
                            'token': token,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('messages_count', 7)
        await store.reload()
        tap.eq_ok(store.messages_count, 7, 'Messages count did not change')
        await store.reload()
        tap.eq_ok(store.lsn, old_lsn, 'lsn did not change')
