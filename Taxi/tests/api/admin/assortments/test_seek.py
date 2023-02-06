async def test_seek(tap, dataset, api, uuid):
    with tap.plan(7):
        assortment = await dataset.assortment(title=uuid())
        tap.ok(assortment, 'Ассортимент создан')
        tap.like(assortment.title, r'^[a-fA-F0-9]{32}$', 'имя присвоено')

        t = await api(role='admin')
        await t.post_ok('api_admin_assortments_seek', json={'cursor': ''})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_has('assortments', 'список')
        t.json_has('cursor', 'курсор есть')


async def test_seek_endcursor(tap, dataset, api, uuid):
    with tap.plan(7):
        assortment = await dataset.assortment(title=uuid())
        tap.ok(assortment, 'Ассортимент создан')
        tap.like(assortment.title, r'^[a-fA-F0-9]{32}$', 'имя присвоено')

        t = await api(role='admin')
        await t.post_ok('api_admin_assortments_seek',
                        json={'title': assortment.title})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_has('assortments', 'список')
        t.json_is('cursor', None, 'курсор закончен')


async def test_foreign_company(tap, dataset, api, uuid):
    with tap.plan(15, 'искать можно только по своей компании'):
        title = uuid()

        user = await dataset.user(role='company_admin')
        tap.ok(user, 'user created')

        assortment = await dataset.assortment(company_id=user.company_id,
                                              title=title)
        tap.ok(assortment, 'assortment created')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_assortments_seek',
            json={'title': title}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('assortments')
        t.json_has('cursor')
        t.json_has('assortments.0')
        t.json_is('assortments.0.assortment_id', assortment.assortment_id)

        foreign_user = await dataset.user(role='company_admin')
        tap.ok(foreign_user, 'foreign_user created')

        t.set_user(foreign_user)

        await t.post_ok(
            'api_admin_assortments_seek',
            json={'title': title}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('assortments', [])
        t.json_is('cursor', None)
