# pylint: disable=unused-variable
import pytest


async def test_list_subscribe(tap, api, uuid, dataset):
    with tap.plan(16):

        products = []
        for _ in range(5):
            product = await dataset.product(name=f'Группа {uuid()}')
            tap.ok(product, 'продукт создан')
            products.append(product)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_products_products',
                        json={'cursor': None, 'subscribe': True})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('products', 'Список присутствует')
        t.json_has('locale', 'Базовая локаль присутствует')
        t.json_has('products.0.product_id')
        t.json_has('products.0.external_id')
        t.json_has('products.0.barcode')

        with tap.subtest(None, 'Дочитываем до конца') as taps:
            t.tap = taps

            while True:
                if not t.res['json']['products']:
                    break

                cursor = t.res['json']['cursor']
                await t.post_ok('api_external_products_products',
                                json={'cursor': cursor})
                t.status_is(200, diag=True)
                t.json_is('code', 'OK', 'ответ получен')
                t.json_has('cursor', 'Курсор присутствует')
        t.tap = tap

        t.json_has('cursor', 'Курсор присутствует')


async def test_list_once(tap, api, uuid, dataset):
    with tap.plan(13):
        products = []
        for _ in range(5):
            product = await dataset.product(name=f'Группа {uuid()}')
            tap.ok(product, 'продукт создан')
            products.append(product)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_products_products',
                        json={'cursor': None, 'subscribe': False})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('products', 'Список присутствует')
        t.json_has('locale', 'Базовая локаль присутствует')

        with tap.subtest(None, 'Дочитываем до конца') as taps:
            t.tap = taps

            while True:
                if not t.res['json']['products']:
                    break

                cursor = t.res['json']['cursor']
                if not cursor:
                    break

                await t.post_ok('api_external_products_products',
                                json={'cursor': cursor})
                t.status_is(200, diag=True)
                t.json_is('code', 'OK', 'ответ получен')
                t.json_has('cursor', 'Курсор присутствует')
        t.tap = tap

        t.json_is('cursor', None, 'Курсор пустой говорит что все забрали')


async def test_list_company(tap, dataset, api, uuid):
    with tap.plan(7, 'Получение списка для компании, по ее ключу'):

        scope1 = uuid()
        scope2 = uuid()

        company = await dataset.company(products_scope=[scope1])
        product1 = await dataset.product(products_scope=[scope1, scope2])
        product2 = await dataset.product(products_scope=[scope2])

        t = await api(token=company.token)

        await t.post_ok(
            'api_external_products_products',
            json={'cursor': None, 'subscribe': False},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor', 'курсор в ответе')
        t.json_is('products.0.product_id', product1.product_id)
        t.json_is('products.0.products_scope', [scope1, scope2])
        t.json_hasnt('products.1')


async def test_list_locales(tap, dataset, api, uuid):
    with tap.plan(24, 'Получение списка в указанной локали'):

        title_ru = f'ru_RU: {uuid()}'
        title_en = f'en_EN: {uuid()}'
        description_ru = f'ru_RU: {uuid()}'

        company = await dataset.company(products_scope=[uuid()])
        product = await dataset.product(
            products_scope=company.products_scope,
            description=description_ru,
            vars={'locales': {
                'title': {
                    'ru_RU': title_ru,
                    'en_EN': title_en,
                }
            }},
        )

        t = await api(token=company.token)

        tap.note('По умолчанию')
        await t.post_ok(
            'api_external_products_products',
            json={'cursor': None, 'subscribe': False},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor', 'курсор в ответе')
        t.json_is('locale', 'ru_RU')
        t.json_is('products.0.product_id', product.product_id)
        t.json_is('products.0.title', title_ru)
        t.json_is('products.0.description', description_ru)

        tap.note('Локаль ru_RU')
        await t.post_ok(
            'api_external_products_products',
            json={'cursor': None, 'subscribe': False, 'locale': 'ru_RU'},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor', 'курсор в ответе')
        t.json_is('locale', 'ru_RU')
        t.json_is('products.0.product_id', product.product_id)
        t.json_is('products.0.title', title_ru)
        t.json_is('products.0.description', description_ru)

        tap.note('Локаль en_EN')
        await t.post_ok(
            'api_external_products_products',
            json={'cursor': None, 'subscribe': False, 'locale': 'en_EN'},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor', 'курсор в ответе')
        t.json_is('locale', 'en_EN')
        t.json_is('products.0.product_id', product.product_id)
        t.json_is('products.0.title', title_en)
        t.json_is('products.0.description', description_ru)


@pytest.mark.parametrize('type_accounting', [
    'unit',
    'weight'
])
@pytest.mark.parametrize('parent_id', [
    True,
    None
])
@pytest.mark.parametrize(['upper_weight_limit', 'lower_weight_limit'], [
    (1300, 1200),
    (None, None),
])
async def test_weighted_products(
        tap, dataset, uuid, api,
        upper_weight_limit, lower_weight_limit,
        parent_id, type_accounting
):
    with tap:
        scope = uuid()

        if parent_id:
            parent_id = (await dataset.product(external_id=uuid())).product_id

        company = await dataset.company(products_scope=[scope])

        product = await dataset.product(
            external_id=uuid(),
            upper_weight_limit=upper_weight_limit,
            lower_weight_limit=lower_weight_limit,
            parent_id=parent_id,
            type_accounting=type_accounting,
            products_scope=[scope],
        )

        t = await api(token=company.token)
        await t.post_ok('api_external_products_products',
                        json={'cursor': None, 'subscribe': False})
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('products', 'Список присутствует')
        t.json_is('products.0.product_id', product.product_id)
        t.json_is('products.0.external_id', product.external_id)
        t.json_is('products.0.upper_weight_limit', upper_weight_limit)
        t.json_is('products.0.lower_weight_limit', lower_weight_limit)
        t.json_is('products.0.parent_id', parent_id)
        t.json_is('products.0.type_accounting', type_accounting)


@pytest.mark.parametrize('product_params, expected_params', [
    (
        {
            'vars': {
                'imported': {
                    'product_kind': 'noway',
                    'is_meta': True,
                    'manufacturer': 'Успешный',
                    'nonsearchable': False,
                    'orders': [300, 300],
                    'virtual_product': True,
                }
            },
            'order': 10,
            'tags': ['refrigerator'],
        },
        {
            'product_kind': 'noway',
            'is_meta': True,
            'tags': ['refrigerator'],
            'manufacturer': 'Успешный',
            'nonsearchable': False,
            'orders': [10, 300, 300],
            'virtual_product': True,
        }
    ),
    (
        {
            'description': 'random description',
            'vars': {'imported': {'carbohydrate': ''}},
        },
        {
            'carbohydrate': None,
            'product_kind': None,
            'tags': [],
            'description': 'random description',
            'manufacturer': None,
        }
    ),
    (
        {
            'vars': {
                'imported': {
                    'main_allergens': ['fish', 'cat'],
                    'photo_stickers': [],
                    'custom_tags': ['halal', 'kosher'],
                    'logistic_tags': ['hot', 'fragile'],
                    'true_mark': False,
                    'private_label': True,
                    'nomenclature_type': 'product',
                },
            },
        },
        {
            'important_ingredients': None,
            'main_allergens': ['fish', 'cat'],
            'photo_stickers': [],
            'custom_tags': ['halal', 'kosher'],
            'logistic_tags': ['hot', 'fragile'],
            'true_mark': False,
            'private_label': True,
            'nomenclature_type': 'product',
        },
    )
])
async def test_products_field(
        tap, dataset, api, product_params,
        expected_params, uuid
):
    with tap:
        company = await dataset.company(products_scope=[uuid()])
        product = await dataset.product(
            products_scope=company.products_scope,
            **product_params
        )

        t = await api(token=company.token)

        await t.post_ok('api_external_products_products',
                        json={'cursor': None, 'subscribe': False})
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('products', 'Список присутствует')
        t.json_is('products.0.product_id', product.product_id)

        for name, value in expected_params.items():
            t.json_is(f'products.0.{name}', value)


@pytest.mark.parametrize(
    'test_params,expected_params',
    [
        (
            {
                'vars': {
                    'imported': {
                        'grade_values': ['500 тонн'],
                        'grade_size': 'L',
                        'grade_order': 10000,
                    },
                },
            },
            {
                'grades': {
                    'values': ['500 тонн'],
                    'size': 'L',
                    'order': 10000,
                },
            },
        ),
        (
            {
                'vars': {
                    'imported': {
                        'grade_values': [],
                        'grade_size': None,
                        'grade_order': None,
                    },
                },
            },
            {
                'grades': {
                    'values': [],
                    'size': None,
                    'order': 0,
                },
            },
        ),
    ]
)
async def test_get_parent_grades(
        tap, dataset, api, uuid, test_params, expected_params
):
    with tap.plan(5, 'Проверяем наличие родителя и грейдов'):
        company = await dataset.company(products_scope=[uuid()])
        await dataset.product(
            products_scope=company.products_scope,
            **test_params
        )


        t = await api(token=company.token)

        await t.post_ok(
            'api_external_products_products',
            json={'cursor': None, 'subscribe': False},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor', 'курсор в ответе')
        t.json_is('products.0.grades', expected_params['grades'])


@pytest.mark.parametrize(
    'private_label, expected_param', [
        (
            {
                'private_label': True
            },
            True
        ),
        (
            {
                'private_label': False
            },
            False
        ),
        (
            {},
            False
        ),
        (
            {
                'private_label': None
            },
            False
        ),
    ]
)
async def test_private_label(
        tap, dataset, api, uuid, private_label, expected_param):
    with tap.plan(4, 'Проверка значения поля private_label'):
        company = await dataset.company(products_scope=[uuid()])
        await dataset.product(
            products_scope=company.products_scope,
            vars={
                'imported': private_label,
            },
        )

        t = await api(token=company.token)

        await t.post_ok('api_external_products_products',
                        json={'cursor': None, 'subscribe': False})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')

        t.json_is('products.0.private_label', expected_param)


@pytest.mark.parametrize(
    'client_attributes, expected_param', [
        (
            {
                'client_attributes': {
                    'main_allergens': ['fish', 'cat'],
                    'photo_stickers': ['hot'],
                    'custom_tags': ['halal', 'kosher']
                }
            },
            {
                'main_allergens': ['fish', 'cat'],
                'photo_stickers': ['hot'],
                'custom_tags': ['halal', 'kosher']
            }
        ),
        (
            {
                'client_attributes': {}
            },
            {}
        ),
        (
            None,
            None
        ),
        (
            {
                'client_attributes': None
            },
            None
        ),
    ]
)
async def test_client_attributes(
    tap, dataset, uuid, api, client_attributes, expected_param):
    with tap.plan(4, 'Проверка поля client_attributes'):
        company = await dataset.company(products_scope=[uuid()])

        await dataset.product(
            products_scope=company.products_scope,
            vars={
                'imported': client_attributes
            }
        )

        t = await api(token=company.token)

        await t.post_ok('api_external_products_products',
                        json={'cursor': None, 'subscribe': False})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')

        t.json_is('products.0.client_attributes', expected_param)


async def test_supplier_tin(tap, dataset, uuid, api):
    with tap.plan(4, 'Проверка поля supplier_tin'):
        company = await dataset.company(products_scope=[uuid()])
        supplier_tin = uuid()

        await dataset.product(
            products_scope=company.products_scope,
            vars={'supplier_tin': supplier_tin},
        )

        t = await api(token=company.token)

        await t.post_ok(
            'api_external_products_products',
            json={'cursor': None, 'subscribe': False}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')

        t.json_is('products.0.supplier_tin', supplier_tin)
