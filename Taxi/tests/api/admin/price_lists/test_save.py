import pytest


async def test_create(tap, api, dataset, uuid, cfg):
    with tap:
        cfg.set('flags.price_list_company_id', True)

        external_id = uuid()

        user = await dataset.user(role='admin')
        t = await api(user=user)

        await t.post_ok(
            'api_admin_price_lists_save',
            json={
                'external_id': external_id,
                'title': 'hello',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list')

        t.json_is('price_list.external_id', external_id)
        t.json_is('price_list.title', 'hello')
        t.json_has('price_list.created')
        t.json_has('price_list.updated')
        t.json_is('price_list.user_id', user.user_id)
        t.json_is('price_list.company_id', user.company_id)


async def test_update(tap, api, dataset):
    with tap:
        price_list = await dataset.price_list()
        tap.ok(price_list, 'Price-list created')

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_price_lists_save',
            json={
                'price_list_id': price_list.price_list_id,
                'title': 'hello',
                'user_id': 'some_user_id',
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list')

        t.json_is('price_list.price_list_id', price_list.price_list_id)
        t.json_is('price_list.title', 'hello')
        t.json_has('price_list.created')
        t.json_has('price_list.updated')
        t.json_isnt('price_list.user_id', 'some_user_id')


@pytest.mark.parametrize('role', ['store_admin', 'expansioner'])
async def test_access(tap, dataset, api, role):
    with tap.plan(5):
        price_list = await dataset.price_list()
        tap.ok(price_list, 'Price-list created')

        t = await api(role=role)

        await t.post_ok(
            'api_admin_price_lists_save',
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
                                  'expansioner', 'category_manager'])
async def test_create_prohibited(tap, api, uuid, role):
    with tap.plan(2):
        t = await api(role=role)
        await t.post_ok(
            'api_admin_price_lists_save',
            json={
                'external_id': uuid(),
                'title': 'hello',
            },
        )
        t.status_is(403, diag=True)


@pytest.mark.parametrize('role', ['authen_guest', 'executer',
                                  'barcode_executer', 'store_admin',
                                  'expansioner'])
async def test_update_prohibited(tap, api, dataset, role):
    with tap.plan(3):
        price_list = await dataset.price_list()
        tap.ok(price_list, 'Price-list created')

        t = await api(role=role)
        await t.post_ok(
            'api_admin_price_lists_save',
            json={
                'price_list_id': price_list.price_list_id,
                'title': 'hello',
            },
        )
        t.status_is(403, diag=True)


@pytest.mark.parametrize('flag_value', [True, False])
async def test_save_foreign(tap, api, dataset, uuid, cfg, flag_value):
    with tap.plan(
            15 if flag_value else 18,
            'сохранять можно только для своей компании'
    ):
        cfg.set('flags.price_list_company_id', flag_value)

        external_id = uuid()

        user = await dataset.user(role='company_admin')
        t = await api(user=user)

        await t.post_ok(
            'api_admin_price_lists_save',
            json={
                'external_id': external_id,
                'title': 'hello',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list')
        t.json_is('price_list.company_id',
                  user.company_id if flag_value else None)
        t.json_is('price_list.title', 'hello')

        await t.post_ok(
            'api_admin_price_lists_save',
            json={
                'external_id': external_id,
                'title': 'hello origin',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('price_list')
        t.json_is('price_list.company_id',
                  user.company_id if flag_value else None)
        t.json_is('price_list.title', 'hello origin')

        foreign_user = await dataset.user(role='company_admin')
        t.set_user(user=foreign_user)

        await t.post_ok(
            'api_admin_price_lists_save',
            json={
                'external_id': external_id,
                'title': 'hello foreign',
            },
        )
        if flag_value:
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
        else:
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('price_list')
            t.json_is('price_list.company_id', None)
            t.json_is('price_list.title', 'hello foreign')
