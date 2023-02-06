import pytest

from stall.model.product import Product
from stall.model.role import PERMITS

ROLES_WITHOUT_ADMIN = [
    role for role in PERMITS['roles']
    if role != 'admin' and not PERMITS['roles'][role].get('virtual', False)
]


async def test_save_create(tap, api, dataset, uuid):
    with tap.plan(18):
        user = await dataset.user(role='admin')
        t = await api(user=user)

        external_id = uuid()
        group = await dataset.product_group()

        product_data = {
            'external_id': external_id,
            'title': 'eggs',
            'long_title': 'long eggs',
            'description': 'about eggs',
            'images': ['https://localhost'],
            'order': 1,
            'vat': None,
            'groups': [group.group_id],
            'tags': ['refrigerator', 'freezer'],
            'amount': '42',
            'amount_unit': 'кусочки',
        }

        await t.post_ok('api_admin_products_save', json=product_data)

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('product.product_id')
        t.json_has('product.created')
        t.json_has('product.updated')
        t.json_is('product.external_id', external_id)
        t.json_is('product.title', product_data['title'])
        t.json_is('product.long_title', product_data['long_title'])
        t.json_is('product.description', product_data['description'])
        t.json_is('product.images', product_data['images'])
        t.json_is('product.vat', None)
        t.json_is('product.groups', product_data['groups'])
        t.json_is('product.tags', product_data['tags'])
        t.json_is('product.amount', '42.000')
        t.json_is('product.amount_unit', product_data['amount_unit'])
        t.json_is('product.user_id', user.user_id)

        product = await Product.load(external_id, by='external')

        tap.ok(product, 'product loaded from db')


async def test_save_update(tap, api, dataset, uuid):
    with tap.plan(9):
        t = await api(role='admin')

        group = await dataset.product_group(name='group')
        product = await dataset.product(title='eggs', groups=[group.group_id])

        # ok case

        await t.post_ok(
            'api_admin_products_save',
            json={
                'product_id': product.product_id,
                'title': 'spam',
                'user_id': 'hello',
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'product loaded')

        t.json_is('product.product_id', product.product_id, 'product_id')
        t.json_is('product.title', 'spam', 'title')
        t.json_isnt('product.user_id', 'hello')

        # err case: group not found

        await t.post_ok(
            'api_admin_products_save',
            json={
                'product_id': product.product_id,
                'groups': [uuid()],
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'group not found')


async def test_save_bad_data(tap, api):
    with tap.plan(3):

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_products_save',
            json={'title': 'spam'},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'create rejected')


async def test_garbadge_parent(tap, dataset, uuid, api):
    with tap.plan(3, 'лажовый родитель'):
        product = await dataset.product()
        user = await dataset.user(role='admin')
        t = await api(user=user)
        await t.post_ok(
            'api_admin_products_save',
            json={'product_id': product.product_id, 'parent_id': uuid()},
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')


@pytest.mark.parametrize('role', ['authen_guest', 'executer',
                                  'barcode_executer', 'store_admin',
                                  'expansioner','support','support_ro',
                                  'admin_ro','category_manager','support_it',
                                  'supervisor','provider','dc_admin'])
async def test_create_prohibited(tap, api, dataset, uuid, role):
    with tap.plan(2):
        t = await api(role=role)
        group = await dataset.product_group()
        product_data = {
            'external_id': uuid(),
            'title': 'eggs',
            'long_title': 'long eggs',
            'description': 'about eggs',
            'images': ['https://localhost'],
            'order': 1,
            'vat': None,
            'groups': [group.group_id],
            'tags': ['refrigerator', 'freezer'],
        }
        await t.post_ok('api_admin_products_save', json=product_data)
        t.status_is(403, diag=True, desc = f'Запрещено создавать товар {role}')


@pytest.mark.parametrize('role', ['authen_guest', 'executer',
                                  'barcode_executer', 'store_admin',
                                  'expansioner','support','support_ro',
                                  'admin_ro','supervisor','provider',
                                  'dc_admin'])
async def test_update_prohibited(tap, api, dataset, role):
    with tap.plan(2):
        t = await api(role=role)
        group = await dataset.product_group(name='group')
        product = await dataset.product(title='eggs', groups=[group.group_id])
        await t.post_ok(
            'api_admin_products_save',
            json={
                'product_id': product.product_id,
                'title': 'spam',
                'components': [],
            },
        )
        t.status_is(403, diag=True, desc = f'Запрещено сохранять товар {role}')

@pytest.mark.parametrize('role', ['support_it', 'category_manager', 'admin'])
async def test_update_components(tap, api, dataset, role):
    with tap.plan(2):
        t = await api(role=role)
        group = await dataset.product_group(name='group')
        product = await dataset.product(title='eggs', groups=[group.group_id])
        await t.post_ok(
            'api_admin_products_save',
            json={
                'product_id': product.product_id,
                'components': [],
            },
        )
        t.status_is(200, diag=True, desc = f'Разрешаем обновить рецепт {role}')


async def test_correct_components(tap, api, dataset):
    with tap.plan(4):
        t = await api(role='admin')
        product = await dataset.product(title='soup')
        tap.eq(product.components, [], 'Нет компонент')

        component = await dataset.product(title='meat')
        components = [
            [
                {
                    'product_id': component.product_id,
                    'count': 3,
                },
            ],
        ]
        await t.post_ok(
            'api_admin_products_save',
            json={
                'product_id': product.product_id,
                'components': components,
            },
        )
        t.status_is(200, diag=True, desc='Продукт обновился')
        t.json_is('product.components', components, 'Корректные компоненты')


async def test_duplicate_components(tap, api, dataset):
    with tap.plan(4):
        t = await api(role='admin')
        product = await dataset.product(title='soup')
        component = await dataset.product(title='meat')
        components = [
            [
                {
                    'product_id': component.product_id,
                    'count': 2,
                },
            ],
            [
                {
                    'product_id': component.product_id,
                    'count': 1,
                },
                {
                    'product_id': product.product_id,
                    'count': 2,
                },
            ],
        ]
        await t.post_ok(
            'api_admin_products_save',
            json={
                'product_id': product.product_id,
                'components': components,
            },
        )
        t.status_is(400, diag=True,
                    desc='Дублирование ингредиентов в рецепте, ссылка на себя')
        t.json_is('details.errors.0.message',
                  'Duplicated components')
        t.json_is('details.errors.1.message',
                  'Product component refers to itself')


async def test_duplicate_variants(tap, api, dataset):
    with tap.plan(3):
        t = await api(role='admin')
        product = await dataset.product(title='soup')
        component = await dataset.product(title='meat')
        components = [
            [
                {
                    'product_id': component.product_id,
                    'count': 2,
                },
                {
                    'product_id': component.product_id,
                    'count': 1,
                },
            ],
        ]
        await t.post_ok(
            'api_admin_products_save',
            json={
                'product_id': product.product_id,
                'components': components,
            },
        )
        t.status_is(400, diag=True,
                    desc='Дублирование ингредиентов в аналоге продукта')
        t.json_is('details.errors.0.message', 'Duplicated components')


async def test_zero_components(tap, api, dataset):
    with tap.plan(3):
        t = await api(role='admin')
        product = await dataset.product(title='soup')
        component = await dataset.product(title='meat')
        components = [
            [
                {
                    'product_id': component.product_id,
                    'count': 0,
                },
            ],
        ]
        await t.post_ok(
            'api_admin_products_save',
            json={
                'product_id': product.product_id,
                'components': components,
            },
        )
        t.status_is(400, diag=True,
                    desc='Нулевое количество ингредиента в рецепте')
        t.json_is('details.errors.0.message', 'Zero product count')


@pytest.mark.parametrize('lang', ('ru_RU', 'en_US'))
async def test_locales(tap, api, dataset, uuid, lang):
    with tap.plan(4):
        user = await dataset.user(role='admin', lang=lang)

        product = await dataset.product(
            barcode=[uuid()],
            vars={
                'locales': {
                    'title': {lang: f'есть перевод {lang}'},
                }
            },
        )

        t = await api(user=user)

        await t.post_ok(
            'api_admin_products_save',
            json={'product_id': product.product_id, 'title': 'вернем перевод'},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product.title', f'есть перевод {lang}')


@pytest.mark.parametrize('role', ROLES_WITHOUT_ADMIN)
async def test_permits(tap, api, dataset, role):
    with tap.plan(5, f'пермиты для products, role={role}'):
        product = await dataset.product()

        title = product.title
        component = await dataset.product(title='meat')

        new_comp = [
            [
                {
                    'product_id': component.product_id,
                    'count': 3,
                },
            ],
        ]
        user = await dataset.user(role=role)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_products_save',
            json={
                'product_id': product.product_id,
                'components': new_comp,
                'title': 'Не изменюсь'
            },
        )

        if role in {'company_admin', 'chief_manager',
                    'category_manager', 'support_it'}:
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('product.title', title)
            t.json_is('product.components', new_comp)
        else:
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
            t.json_is('code', 'ER_ACCESS')
            t.json_has('message')


async def test_update_vars(tap, api, dataset):
    with tap.plan(5, 'Обновление vars'):
        product = await dataset.product(
            vars={'imported': {'true_mark': True}}
        )
        user = await dataset.user(role='admin')
        t = await api(user=user)
        await t.post_ok(
            'api_admin_products_save',
            json={
                'product_id': product.product_id,
                'vars': {'imported': {'true_mark': False}}
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await product.reload(), 'Перезабрали продукт')
        tap.eq(
            product.vars['imported']['true_mark'],
            False,
            'Признак в vars изменился'
        )


async def test_update_schedule_type(tap, api, dataset):
    with tap.plan(5, 'Меняем тип расписания продукта'):
        product = await dataset.product()
        user = await dataset.user(role='admin')

        tap.eq(
            product.schedule_type,
            None,
            'Нет расписания'
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_products_save',
            json={
                'product_id': product.product_id,
                'schedule_type': 'coffee'
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await product.reload()
        tap.eq(
            product.schedule_type,
            'coffee',
            'Поменяли тип расписания'
        )
