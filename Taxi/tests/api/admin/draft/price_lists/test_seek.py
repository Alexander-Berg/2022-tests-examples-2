async def test_filter_by_title(tap, dataset, api, uuid):
    with tap.plan(17):
        title_prefix = uuid()

        price_lists = []
        for i in range(3):
            price_lists.append(
                await dataset.draft_price_list(title=f'{title_prefix}-{i}')
            )
        tap.eq_ok(len(price_lists), 3, 'Price-lists created')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_draft_price_lists_seek',
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
            'api_admin_draft_price_lists_seek',
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
            'api_admin_draft_price_lists_seek',
            json={
                'title': '',
                'cursor': '',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_lists')
        t.json_has('cursor')


async def test_seek_mine(tap, dataset, api, uuid):
    user1 = await dataset.user(role='admin')
    user2 = await dataset.user(role='admin')
    price_lists1 = set()
    price_lists2 = set()
    title_prefix = uuid()
    for i in range(3):
        pl = await dataset.draft_price_list(title=f'{title_prefix}-{i}',
                                            user_id=user1.user_id)
        price_lists1.add(pl.price_list_id)
    for i in range(3):
        pl = await dataset.draft_price_list(title=f'{title_prefix}-{i}',
                                            user_id=user2.user_id)
        price_lists2.add(pl.price_list_id)
    with tap:
        t = await api(user=user1)
        await t.post_ok(
            'api_admin_draft_price_lists_seek',
            json={
                'title': title_prefix,
                'mine': True,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_lists')
        t.json_has('cursor')
        received_price_lists = t.res['json']['price_lists']
        tap.eq_ok(len(received_price_lists), 3, 'correct quantity')
        for pl in received_price_lists:
            tap.ok(pl['price_list_id'] in price_lists1,
                   'correct price list present')

        t = await api(user=user2)
        await t.post_ok(
            'api_admin_draft_price_lists_seek',
            json={
                'title': title_prefix,
                'mine': True,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_lists')
        t.json_has('cursor')
        received_price_lists = t.res['json']['price_lists']
        tap.eq_ok(len(received_price_lists), 3, 'correct quantity')
        for pl in received_price_lists:
            tap.ok(pl['price_list_id'] in price_lists2,
                   'correct price lit present')


async def test_filter_by_status(tap, dataset, api):
    with tap.plan(17):
        user = await dataset.user(role='admin')
        price_lists = []
        for status in ['active', 'removed', 'ready', 'applied']:
            price_lists.append(
                await dataset.draft_price_list(status=status,
                                               user=user)
            )

        tap.eq_ok(len(price_lists), 4, 'Price-lists created')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_draft_price_lists_seek',
            json={
                'status': 'active',
                'cursor': '',
                'mine': True,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_lists.0')
        t.json_hasnt('price_lists.1')
        t.json_is('price_lists.0.status', 'active')
        t.json_is('price_lists.0.price_list_id', price_lists[0].price_list_id)
        t.json_is('cursor', None)

        await t.post_ok(
            'api_admin_draft_price_lists_seek',
            json={
                'status': 'applied',
                'cursor': '',
                'mine': True,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_lists.0')
        t.json_hasnt('price_lists.1')
        t.json_is('price_lists.0.status', 'applied')
        t.json_is('price_lists.0.price_list_id', price_lists[3].price_list_id)
        t.json_is('cursor', None)


async def test_price_list(tap, dataset, api, uuid):
    user1 = await dataset.user(role='admin')
    price_list_target = await dataset.price_list()
    price_lists1 = set()
    title_prefix = uuid()
    user_ready = await dataset.user(role='admin')
    for i in range(3):
        pl = await dataset.draft_price_list(title=f'{title_prefix}-{i}',
                                            user_id=user1.user_id,
                                            price_list_target=
                                            price_list_target.price_list_id,
                                            status='ready',
                                            user_ready=user_ready.user_id)
        price_lists1.add(pl.price_list_id)

    with tap.plan(8, 'Список по прайс листу'):
        t = await api(user=user1)
        await t.post_ok(
            'api_admin_draft_price_lists_seek',
            json={
                'price_list_target': price_list_target.price_list_id,
                'drafts_for_applying': True
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_lists')
        t.json_has('cursor')
        received_price_lists = t.res['json']['price_lists']
        received_ids = [pl['price_list_id'] for pl in received_price_lists]
        # TODO после появления у всех price_list_target
        # проверять только 3 нужных
        for pl in price_lists1:
            tap.ok(pl in received_ids,
                   'correct price list present')


async def test_price_empty_target(tap, dataset, api, uuid):
    with tap.plan(8, 'Пустой таргет'):
        user1 = await dataset.user(role='admin')
        user2 = await dataset.user(role='admin')
        drafts = set()
        title_prefix = uuid()
        for i in range(3):
            pl = await dataset.draft_price_list(title=f'{title_prefix}-{i}',
                                                user_id=user1.user_id,
                                                status='ready',
                                                user_ready=user1.user_id,
                                                )
            drafts.add(pl.price_list_id)

        t = await api(user=user2)
        await t.post_ok(
            'api_admin_draft_price_lists_seek',
            json={
                'price_list_target': None,
                'drafts_for_applying': True
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_lists')
        t.json_has('cursor')
        received_price_lists = t.res['json']['price_lists']
        received_ids = [pl['price_list_id'] for pl in received_price_lists]

        for draft_id in drafts:
            tap.ok(draft_id in received_ids,
                   'correct price list present')


async def test_foreign_company(tap, dataset, api, uuid):
    with tap.plan(15, 'искать можно только по своей компании'):
        title = uuid()

        user = await dataset.user(role='company_admin')
        tap.ok(user, 'user created')

        price_list = await dataset.draft_price_list(company_id=user.company_id,
                                                    title=title)
        tap.ok(price_list, 'price_list created')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_draft_price_lists_seek',
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
            'api_admin_draft_price_lists_seek',
            json={
                'title': title,
                'cursor': '',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('price_lists', [])
        t.json_is('cursor', None)
