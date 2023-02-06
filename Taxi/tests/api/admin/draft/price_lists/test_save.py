import pytest


async def test_create(tap, api, dataset, uuid):
    with tap:
        external_id = uuid()

        user = await dataset.user(role='admin')
        t = await api(user=user)
        price_list_target = await dataset.price_list()
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'external_id': external_id,
                'title': 'hello',
                'price_list_target': price_list_target.price_list_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list')

        t.json_is('price_list.status', 'active')
        t.json_is('price_list.external_id', external_id)
        t.json_is('price_list.price_list_target',
                  price_list_target.price_list_id)
        t.json_is('price_list.title', 'hello')
        t.json_has('price_list.created')
        t.json_has('price_list.updated')
        t.json_is('price_list.user_id', user.user_id)
        t.json_is('price_list.company_id', price_list_target.company_id)


async def test_fail_create(tap, api, dataset, uuid):
    with tap:
        external_id = uuid()

        user = await dataset.user(role='admin')
        t = await api(user=user)
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'external_id': external_id,
                'title': 'hello',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        price_list_target = await dataset.price_list()
        t = await api(user=user)
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_target': price_list_target.price_list_id,
                'title': 'hello',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')


async def test_update(tap, api, dataset):
    with tap:
        user = await dataset.user(role='admin')
        price_list = await dataset.draft_price_list(user_id=user.user_id)
        tap.ok(price_list, 'Price-list created')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': price_list.price_list_id,
                'title': 'hello',
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list')

        t.json_is('price_list.price_list_id', price_list.price_list_id)
        t.json_is('price_list.title', 'hello')
        t.json_has('price_list.created')
        t.json_has('price_list.updated')


async def test_fail_applied_ready(tap, api, dataset):
    with tap:
        user = await dataset.user(role='admin')
        price_list = await dataset.draft_price_list(status='applied',
                                                    user_id=user.user_id)
        tap.ok(price_list, 'Price-list created')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': price_list.price_list_id,
                'title': 'hello',
            },
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_GONE')

        price_list.status = 'ready'
        await price_list.save()

        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': price_list.price_list_id,
                'title': 'hello',
            },
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_GONE')


@pytest.mark.parametrize('role', ['admin', 'chief_manager'])
async def test_unlock_draft(tap, api, dataset, role):
    with tap:
        author = await dataset.user(role='admin')
        user = await dataset.user(role=role)
        logs = [
            {
                'user_id': author.user_id,
                'status': 'active'
            },
        ]

        price_list = await dataset.draft_price_list(status='ready',
                                                    user_id=author.user_id,
                                                    vars={'logs': logs}
                                                    )
        tap.ok(price_list, 'Price-list created')

        t = await api(user=user)
        t_author = await api(user=author)

        await t_author.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': price_list.price_list_id,
                'status': 'active'
            },
        )
        t_author.status_is(403, diag=True)
        t_author.json_is('code', 'ER_ACCESS')

        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': price_list.price_list_id,
                'status': 'active'
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list')
        t.json_is('price_list.price_list_id', price_list.price_list_id)
        t.json_is('price_list.status', 'active')

        await t_author.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': price_list.price_list_id,
                'title': 'hello',
            },
        )
        t_author.status_is(200, diag=True)
        t_author.json_is('code', 'OK')
        t_author.json_is('price_list.price_list_id', price_list.price_list_id)
        t_author.json_is('price_list.title', 'hello')


@pytest.mark.parametrize('role', ['category_manager',
                                  'store_admin', 'expansioner'])
async def test_fail_unlock_draft(tap, api, dataset, role):
    with tap:
        author = await dataset.user(role='admin')
        price_list = await dataset.draft_price_list(status='ready',
                                                    user_id=author.user_id)
        tap.ok(price_list, 'Price-list created')
        user = await dataset.user(role=role)
        t= await api(user=user)

        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': price_list.price_list_id,
                'status': 'active'
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('role', ['store_admin', 'expansioner'])
async def test_access(tap, dataset, api, role):
    with tap.plan(5):
        user = await dataset.user(role=role)
        price_list = await dataset.draft_price_list(user_id=user.user_id)
        tap.ok(price_list, 'Price-list created')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': price_list.price_list_id,
                'title': 'hello',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


@pytest.mark.parametrize('role', ['authen_guest', 'executer',
                                  'barcode_executer', 'store_admin',
                                  'expansioner'])
async def test_create_prohibited(tap, api, dataset, uuid, role):
    with tap.plan(2):
        t = await api(role=role)
        price_list = await dataset.price_list()
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'external_id': uuid(),
                'title': 'hello',
                'price_list_target': price_list.price_list_id
            },
        )
        t.status_is(403, diag=True)


@pytest.mark.parametrize('role', ['authen_guest', 'executer',
                                  'barcode_executer', 'store_admin',
                                  'expansioner'])
async def test_update_prohibited(tap, api, dataset, role):
    with tap.plan(3):
        user = await dataset.user(role=role)
        price_list = await dataset.draft_price_list(user_id=user.user_id)
        tap.ok(price_list, 'Price-list created')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': price_list.price_list_id,
                'title': 'hello',
            },
        )
        t.status_is(403, diag=True)


async def test_save_user_id(tap, dataset, api):
    with tap:
        user = await dataset.user(role='admin')
        draft_price_list = await dataset.draft_price_list(user_id=user.user_id)

        t = await api(user=user)

        await t.post_ok('api_admin_draft_price_lists_save',
                        json={
                            'price_list_id': draft_price_list.price_list_id,
                            'title': 'привет, медвед!',
                            'user_id': 'hello',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_isnt('assortment.user_id', 'hello')


async def test_status_change(tap, dataset, api):
    with tap:
        author = await dataset.user(role='admin')

        product1 = await dataset.product()
        price_list = await dataset.price_list()
        await dataset.price_list_product(
            product=product1,
            price_list=price_list,
            price={'store': '300.12', 'markdown': '200.23'},
            user=author,
        )
        draft = await dataset.draft_price_list(user_id=author.user_id)
        tap.ok(draft, 'Price-list created')

        user_ready = await dataset.user(role='chief_manager')
        t = await api(user=user_ready)
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': draft.price_list_id,
                'status': 'ready',
            },
        )

        t.status_is(200, diag=True)

        t.json_is('price_list.price_list_id', draft.price_list_id)
        t.json_has('price_list.title')
        t.json_is('price_list.user_ready', user_ready.user_id)
        t.json_has('price_list.time_ready')
        t.json_is('price_list.status', 'ready')


@pytest.mark.parametrize('role', ['authen_guest',
                                  'executer', 'barcode_executer',
                                  'store_admin', 'expansioner'])
async def test_problem_with_status_change(tap, dataset, api, role):
    with tap:
        author = await dataset.user(role='admin')

        price_list = await dataset.draft_price_list(user_id=author.user_id)
        tap.ok(price_list, 'Price-list created')

        user_ready = await dataset.user(role=role)
        t = await api()
        # Попытка сделать ready автором
        t.set_user(user_ready)
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': price_list.price_list_id,
                'status': 'ready',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_logging(tap, dataset, api):
    with tap:
        author = await dataset.user(role='admin')
        t = await api(user=author)
        draft = await dataset.draft_price_list()
        price_list_target = await dataset.price_list()

        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': draft.price_list_id,
                'title': 'hello',
                'price_list_target': price_list_target.price_list_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list.vars.logs.0')
        t.json_hasnt('price_list.vars.logs.1')
        user_ready = await dataset.user(role='admin')
        t.set_user(user_ready)

        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': draft.price_list_id,
                'status': 'ready'
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('price_list.status', 'ready')
        t.json_has('price_list.vars.logs.1')
        t.json_hasnt('price_list.vars.logs.2')

        user_active = await dataset.user(role='chief_manager')
        t.set_user(user_active)

        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': draft.price_list_id,
                'status': 'active'
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list.vars.logs.2')
        t.json_hasnt('price_list.vars.logs.3')

        user_removed = await dataset.user(role='admin')
        t.set_user(user_removed)
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': draft.price_list_id,
                'status': 'removed'
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('price_list.status', 'removed')
        t.json_has('price_list.vars.logs.3')
        t.json_hasnt('price_list.vars.logs.4')


async def test_logging_no_duplicate(tap, dataset, api):
    with tap:
        author = await dataset.user(role='admin')
        t = await api(user=author)
        draft = await dataset.draft_price_list()
        price_list_target = await dataset.price_list()

        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': draft.price_list_id,
                'title': 'hello',
                'price_list_target': price_list_target.price_list_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list.vars.logs.0')
        t.json_hasnt('price_list.vars.logs.1')

        # Проверим что active не дублируется, даже если меняется пользователь
        for _ in range(2):
            user = await dataset.user(role='admin')
            t.set_user(user)
            await t.post_ok(
                'api_admin_draft_price_lists_save',
                json={
                    'price_list_id': draft.price_list_id,
                    'status': 'active'
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('price_list.vars.logs.0')
            t.json_hasnt('price_list.vars.logs.1')

        user_ready = await dataset.user(role='admin')
        t.set_user(user_ready)
        for _ in range(2):
            await t.post_ok(
                'api_admin_draft_price_lists_save',
                json={
                    'price_list_id': draft.price_list_id,
                    'status': 'ready'
                },
            )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list.vars.logs.1')
        t.json_hasnt('price_list.vars.logs.2')


async def test_pass_price_list_target(tap, dataset, api, uuid):
    with tap:
        author = await dataset.user(role='admin')
        price_list_target = await dataset.price_list()
        external_id = uuid()

        t = await api(user=author)
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'external_id': external_id,
                'title': 'hello',
                'price_list_target': price_list_target.price_list_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('price_list.price_list_target',
                  price_list_target.price_list_id)

        draft_id = t.res['json']['price_list']['price_list_id']
        user_ready = await dataset.user(role='admin')
        price_list_target_2 = await dataset.price_list()

        t.set_user(user_ready)

        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': draft_id,
                'price_list_target': price_list_target_2.price_list_id,
                'status': 'ready'
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('price_list.status', 'ready')
        t.json_is('price_list.price_list_target',
                  price_list_target.price_list_id)


async def test_get_last_from_logs(tap, dataset, api):
    with tap:
        author = await dataset.user(role='admin')
        t = await api(user=author)
        draft = await dataset.draft_price_list()
        price_list_target = await dataset.price_list()

        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': draft.price_list_id,
                'title': 'hello',
                'price_list_target': price_list_target.price_list_id,
            },
        )

        user1 = await dataset.user(role='admin')
        user2 = await dataset.user(role='admin')
        for user in [user1, user2]:
            t.set_user(user)
            await t.post_ok(
                'api_admin_draft_price_lists_save',
                json={
                    'price_list_id': draft.price_list_id,
                    'status': 'ready'
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

        # Попытаемся изменить статус создателем
        t.set_user(author)
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': draft.price_list_id,
                'status': 'active'
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        # Попытаемся изменить статус последним
        t.set_user(user2)
        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': draft.price_list_id,
                'status': 'active'
            },
        )
        t.status_is(200, diag=True)


async def test_save_foreign(tap, api, dataset):
    with tap.plan(9, 'сохранять можно только для своей компании'):
        user = await dataset.user(role='company_admin')
        t = await api(user=user)

        draft = await dataset.draft_price_list(company_id=user.company_id)

        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': draft.price_list_id,
                'title': 'hello origin',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list')
        t.json_is('price_list.company_id', user.company_id)
        t.json_is('price_list.title', 'hello origin')

        foreign_user = await dataset.user(role='company_admin')
        t.set_user(user=foreign_user)

        await t.post_ok(
            'api_admin_draft_price_lists_save',
            json={
                'price_list_id': draft.price_list_id,
                'title': 'hello foreign',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
