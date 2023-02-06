import pytest


@pytest.mark.parametrize('role', ['admin', 'category_manager'])
async def test_save_exists(tap, dataset, api, role):
    with tap.plan(8):
        user = await dataset.user(role=role)

        parent_assortment = await dataset.assortment(company_id=user.company_id)
        assortment = await dataset.assortment(company_id=user.company_id)
        tap.ok(assortment, 'ассортимент сгенерирован')

        t = await api(user=user)
        await t.post_ok('api_admin_assortments_save',
                        json={
                            'assortment_id': assortment.assortment_id,
                            'title': 'привет, медвед!',
                            'parents': [parent_assortment.assortment_id],
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('assortment', 'ассортимент есть в выдаче')

        t.json_is('assortment.assortment_id',
                  assortment.assortment_id, 'assortment_id')
        t.json_is('assortment.title',
                  'привет, медвед!', 'title')
        t.json_is('assortment.parents.0',
                  parent_assortment.assortment_id,
                  'Родительский ассортимент')


@pytest.mark.parametrize('role', ['admin', 'category_manager'])
async def test_parent_id_null(tap, dataset, api, role):
    with tap.plan(8):
        user = await dataset.user(role=role)

        parent_assortment = await dataset.assortment(company_id=user.company_id)
        assortment = await dataset.assortment(
            company_id=user.company_id,
            parents=[parent_assortment.assortment_id])
        tap.ok(assortment, 'ассортимент сгенерирован')

        t = await api(user=user)
        await t.post_ok('api_admin_assortments_save',
                        json={
                            'assortment_id': assortment.assortment_id,
                            'title': 'привет, медвед!',
                            'parent_id': None,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('assortment', 'ассортимент есть в выдаче')

        t.json_is('assortment.assortment_id',
                  assortment.assortment_id, 'assortment_id')
        t.json_is('assortment.title',
                  'привет, медвед!', 'title')
        t.json_hasnt('assortment.parents.0'
                     'Нет родителя')


async def test_save_unexists(tap, api, dataset, uuid, cfg):
    with tap.plan(9):
        cfg.set('flags.assortment_company_id', True)

        parent_assortment = await dataset.assortment()
        external_id = uuid()

        user = await dataset.user(role='admin')
        t = await api(user=user)
        await t.post_ok('api_admin_assortments_save',
                        json={
                            'external_id': external_id,
                            'parents': [parent_assortment.assortment_id],
                            'title': 'привет!'
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('assortment', 'ассортимент есть в выдаче')

        t.json_is('assortment.external_id', external_id, 'external_id')
        t.json_is('assortment.title', 'привет!', 'title')
        t.json_is('assortment.parents.0',
                  parent_assortment.assortment_id,
                  'Родительский ассортимент')
        t.json_is('assortment.user_id', user.user_id, 'user_id')
        t.json_is('assortment.company_id', user.company_id)


@pytest.mark.parametrize('role', ['authen_guest', 'executer',
                                  'barcode_executer', 'store_admin',
                                  'expansioner', 'category_manager'])
async def test_create_prohibited(tap, api, uuid, role):
    with tap.plan(4):
        t = await api(role=role)
        await t.post_ok('api_admin_assortments_save',
                        json={
                            'external_id': uuid(),
                            'title': 'привет!'
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_has('message', 'Access denied')


@pytest.mark.parametrize('role', ['authen_guest', 'executer',
                                  'barcode_executer', 'store_admin',
                                  'expansioner'])
async def test_update_prohibited(tap, dataset, api, role):
    with tap.plan(5):
        assortment = await dataset.assortment()
        tap.ok(assortment, 'ассортимент сгенерирован')

        t = await api(role=role)
        await t.post_ok('api_admin_assortments_save',
                        json={
                            'assortment_id': assortment.assortment_id,
                            'title': 'привет, медвед!'
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_has('message', 'Access denied')


async def test_save_user_id(tap, dataset, api):
    with tap:
        assortment = await dataset.assortment()

        t = await api(role='admin')

        await t.post_ok('api_admin_assortments_save',
                        json={
                            'assortment_id': assortment.assortment_id,
                            'title': 'привет, медвед!',
                            'user_id': 'hello',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_isnt('assortment.user_id', 'hello')


async def test_parents(tap, api, dataset, uuid):
    with tap.plan(7, 'проверка родителей на вменяемость'):
        assortment = await dataset.assortment()
        assortment_with_parents = await dataset.assortment(parents=[uuid()])
        assortment_not_found = uuid()

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_assortments_save',
            json={
                'assortment_id': assortment.assortment_id,
                'parents': [
                    assortment.assortment_id,
                    assortment_with_parents.assortment_id,
                    assortment_not_found,
                ],
            }
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Wrong parents')
        t.json_is(
            'details.errors.0.message',
            'Assortment refers to itself',
            'ассортимент ссылается сам на себя зачем?',
        )
        t.json_is(
            'details.errors.1.message',
            f'Parent assortment is not root: '
            f'{assortment_with_parents.assortment_id}',
            'глубина больше 2',
        )
        t.json_is(
            'details.errors.2.message',
            f'Parent assortment not found: {assortment_not_found}',
            'не нашли такой родительсткий ассортимент',
        )


async def test_set_empty_parents(tap, api, dataset):
    with tap.plan(4, 'пустой список родителей'):
        parent = await dataset.assortment()
        assortment = await dataset.assortment(parents=[parent.assortment_id])

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_assortments_save',
            json={
                'assortment_id': assortment.assortment_id,
                'parents': [],
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_hasnt('assortment.parents.0',
                     'Нет родителя')


@pytest.mark.parametrize('flag_value', [True, False])
async def test_save_foreign_company(tap, api, dataset, uuid, cfg, flag_value):
    with tap.plan(
            17 if flag_value else 20,
            'сохранять можно только для своей компании'
    ):
        cfg.set('flags.assortment_company_id', flag_value)

        external_id = uuid()

        user = await dataset.user(role='company_admin')
        tap.ok(user, 'user created')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_assortments_save',
            json={
                'external_id': external_id,
                'title': 'hello',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('assortment')
        t.json_is('assortment.company_id',
                  user.company_id if flag_value else None)
        t.json_is('assortment.title', 'hello')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_assortments_save',
            json={
                'external_id': external_id,
                'title': 'hello origin',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('assortment')
        t.json_is('assortment.company_id',
                  user.company_id if flag_value else None)
        t.json_is('assortment.title', 'hello origin')

        foreign_user = await dataset.user(role='company_admin')
        tap.ok(foreign_user, 'foreign_user created')

        t.set_user(foreign_user)

        await t.post_ok(
            'api_admin_assortments_save',
            json={
                'external_id': external_id,
                'title': 'hello foreign',
            }
        )
        if flag_value:
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
        else:
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('assortment')
            t.json_is('assortment.company_id', None)
            t.json_is('assortment.title', 'hello foreign')
