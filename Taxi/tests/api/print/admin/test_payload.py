
async def test_payload(tap, api, dataset, uuid):
    with tap.plan(5, 'Получение тела документа для печати'):

        store = await dataset.store()
        admin = await dataset.user(store=store)

        payload = await dataset.printer_task_payload(data=uuid())
        task = await dataset.printer_task(
            payload=payload,
            store=store,
        )

        t = await api(user=admin)
        await t.post_ok(
            'api_print_admin_payload',
            json={'payload_id': task.payload_id},
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('payload.payload_id', payload.payload_id)
        t.json_is('payload.data', payload.data)


async def test_unknown(tap, api, dataset, uuid):
    with tap.plan(3, 'Получение тела документа для печати'):

        store = await dataset.store()
        admin = await dataset.user(store=store)

        t = await api(user=admin)
        await t.post_ok(
            'api_print_admin_payload',
            json={'payload_id': uuid()},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
