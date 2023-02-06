async def test_list_empty(api, tap, uuid):
    with tap.plan(4):
        t = await api(role='admin')

        await t.post_ok(
            'api_admin_courier_shift_tags_list',
            json={'title': uuid()}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('courier_shift_tags', [])


async def test_list_nonempty(api, dataset, tap, uuid):
    with tap.plan(7):
        title = uuid()

        courier_shift_tags = [
            await dataset.courier_shift_tag(
                title=f'{i}-{title}'
            ) for i in range(0, 5)
        ]
        tap.ok(courier_shift_tags, 'объекты созданы')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_courier_shift_tags_list',
            json={'title': title}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('courier_shift_tags')
        t.json_has('courier_shift_tags.4')
        t.json_hasnt('courier_shift_tags.5')
