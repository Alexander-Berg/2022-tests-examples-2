async def test_filter_by_title(tap, dataset, api, uuid):
    with tap.plan(17):
        title_prefix = uuid()

        price_lists = []
        for i in range(3):
            price_lists.append(
                await dataset.price_list(title=f'{title_prefix}-{i}')
            )

        tap.eq_ok(len(price_lists), 3, 'Price-lists created')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_price_lists_seek',
            json={
                'title': title_prefix,
                'cursor': '',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_lists')
        t.json_has('cursor')

        tap.eq_ok(
            {i['title'] for i in t.res['json']['price_lists']},
            {i.title for i in price_lists},
            'Correct price-lists returned',
        )

        await t.post_ok(
            'api_admin_price_lists_seek',
            json={
                'title': uuid(),
                'cursor': '',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('price_lists', [])
        t.json_is('cursor', None)

        await t.post_ok(
            'api_admin_price_lists_seek',
            json={
                'title': '',
                'cursor': '',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_lists')
        t.json_has('cursor')


async def test_foreign_company(tap, dataset, api, uuid):
    with tap.plan(15, 'искать можно только по своей компании'):
        title = uuid()

        user = await dataset.user(role='company_admin')
        tap.ok(user, 'user created')

        price_list = await dataset.price_list(title=title,
                                              company_id=user.company_id)
        tap.ok(price_list, 'price_list created')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_price_lists_seek',
            json={
                'title': title,
                'cursor': '',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_lists')
        t.json_has('cursor')
        t.json_has('price_lists.0')
        t.json_is('price_lists.0.price_list_id', price_list.price_list_id)

        foreign_user = await dataset.user(role='company_admin')
        tap.ok(foreign_user, 'foreign_user created')

        t.set_user(foreign_user)

        await t.post_ok(
            'api_admin_price_lists_seek',
            json={
                'title': title,
                'cursor': '',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('price_lists', [])
        t.json_is('cursor', None)
