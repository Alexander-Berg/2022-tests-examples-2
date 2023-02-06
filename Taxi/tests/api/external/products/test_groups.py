# pylint: disable=unused-variable


async def test_list_subscribe(tap, api, uuid, dataset):
    with tap.plan(12):

        groups = []
        for _ in range(5):
            group = await dataset.product_group(name=f'Группа {uuid()}')
            tap.ok(group, 'группа создана')
            groups.append(group)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_products_groups',
                        json={'cursor': None, 'subscribe': True})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('groups', 'Список присутствует')

        with tap.subtest(None, 'Дочитываем до конца') as taps:
            t.tap = taps

            while True:
                if not t.res['json']['groups']:
                    break

                cursor = t.res['json']['cursor']
                await t.post_ok('api_external_products_groups',
                                json={'cursor': cursor})
                t.status_is(200, diag=True)
                t.json_is('code', 'OK', 'ответ получен')
                t.json_has('cursor', 'Курсор присутствует')
        t.tap = tap

        t.json_has('cursor', 'Курсор присутствует')


async def test_list_once(tap, api, uuid, dataset):
    with tap.plan(12):
        groups = []
        for _ in range(5):
            group = await dataset.product_group(name=f'Группа {uuid()}')
            tap.ok(group, 'группа создана')
            groups.append(group)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_products_groups',
                        json={'cursor': None, 'subscribe': False})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('groups', 'Список присутствует')

        with tap.subtest(None, 'Дочитываем до конца') as taps:
            t.tap = taps

            while True:
                if not t.res['json']['groups']:
                    break

                cursor = t.res['json']['cursor']
                if not cursor:
                    break

                await t.post_ok('api_external_products_groups',
                                json={'cursor': cursor})
                t.status_is(200, diag=True)
                t.json_is('code', 'OK', 'ответ получен')
                t.json_has('cursor', 'Курсор присутствует')
        t.tap = tap

        t.json_is('cursor', None, 'Курсор пустой говорит что все забрали')


async def test_item_required(tap, api, dataset):
    with tap.plan(13):
        group = await dataset.product_group()
        tap.ok(group, 'группа создана')

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok(
            'api_external_products_groups',
            json={'cursor': None, 'subscribe': False},
        )

        t.json_has('groups.0.group_id')
        t.json_has('groups.0.external_id')
        t.json_has('groups.0.name')
        t.json_has('groups.0.parent_group_id')
        t.json_has('groups.0.order')
        t.json_has('groups.0.status')
        t.json_has('groups.0.images')
        t.json_has('groups.0.locales')
        t.json_has('groups.0.deeplink_id')
        t.json_has('groups.0.legal_restrictions')
        t.json_has('groups.0.timetable')


async def test_list_company(tap, dataset, api, uuid):
    with tap.plan(7, 'Получение списка для компании, по ее ключу'):

        scope1 = uuid()
        scope2 = uuid()

        company = await dataset.company(products_scope=[scope1])
        group1 = await dataset.product_group(products_scope=[scope1, scope2])
        group2 = await dataset.product_group(products_scope=[scope2])

        t = await api(token=company.token)

        await t.post_ok(
            'api_external_products_groups',
            json={'cursor': None, 'subscribe': False},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor', 'курсор в ответе')
        t.json_is('groups.0.group_id', group1.group_id)
        t.json_is('groups.0.products_scope', [scope1, scope2])
        t.json_hasnt('groups.1')


async def test_list_locales(tap, dataset, api, uuid):
    with tap.plan(24, 'Получение списка в указанной локали'):

        name_ru = f'ru_RU: {uuid()}'
        name_en = f'en_EN: {uuid()}'
        description_ru = f'ru_RU: {uuid()}'

        company = await dataset.company(products_scope=[uuid()])
        group = await dataset.product_group(
            products_scope=company.products_scope,
            description=description_ru,
            vars={'locales': {
                'name': {
                    'ru_RU': name_ru,
                    'en_EN': name_en,
                }
            }},
        )

        t = await api(token=company.token)

        tap.note('По умолчанию')
        await t.post_ok(
            'api_external_products_groups',
            json={'cursor': None, 'subscribe': False},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor', 'курсор в ответе')
        t.json_is('locale', 'ru_RU')
        t.json_is('groups.0.group_id', group.group_id)
        t.json_is('groups.0.name', name_ru)
        t.json_is('groups.0.description', description_ru)

        tap.note('Локаль ru_RU')
        await t.post_ok(
            'api_external_products_groups',
            json={'cursor': None, 'subscribe': False, 'locale': 'ru_RU'},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor', 'курсор в ответе')
        t.json_is('locale', 'ru_RU')
        t.json_is('groups.0.group_id', group.group_id)
        t.json_is('groups.0.name', name_ru)
        t.json_is('groups.0.description', description_ru)

        tap.note('Локаль en_EN')
        await t.post_ok(
            'api_external_products_groups',
            json={'cursor': None, 'subscribe': False, 'locale': 'en_EN'},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor', 'курсор в ответе')
        t.json_is('locale', 'en_EN')
        t.json_is('groups.0.group_id', group.group_id)
        t.json_is('groups.0.name', name_en)
        t.json_is('groups.0.description', description_ru)
