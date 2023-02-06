import pytest

from aiohttp import web

from ymlcfg.jpath import JPath
# pylint: disable=protected-access,too-many-locals


async def test_pigeon_to_db(tap, dataset, load_json, uuid, prod_sync_group):
    with tap.plan(6):
        _ext_groups = load_json('data/categories.pigeon.json')
        ext_groups = []
        for i in _ext_groups:
            i['code'] += ':' + uuid()
            ext_groups.append(i)
        ext_groups = prod_sync_group._sort_ext_groups(ext_groups)
        ext_groups_to_rm = dict()
        new, updated, removed, not_updated = await prod_sync_group.run_pim(
            ext_groups,
            ext_groups_to_rm,
        )
        synced = new + updated + removed + not_updated
        tap.ok(len(new + updated + removed) > 0, 'Groups synced')
        tap.is_ok(
            all(i.group_id for i in synced),
            True,
            'All groups have id',
        )
        tap.ok(
            set(val for val in ext_groups).issubset(
                {i.external_id for i in synced}
            ),
            'Correct groups tree',
        )
        tap.ok(
            {
                'Food',
                'Корневая категория',
            }.issubset({i.name for i in synced}),
            'Correct group names',
        )
        prod_groups = [await dataset.ProductGroup.load(i.group_id)
                       for i in synced]
        tap.ok(all(i is not None for i in prod_groups), 'в базе есть группы')
        for group in synced:
            group.name = uuid()
            await group.save()

        pim_result = await prod_sync_group.run_pim(
            ext_groups,
            ext_groups_to_rm,
        )
        _, updated, _, _ = pim_result

        tap.eq_ok(
            {i.name for i in updated},
            {
                'Food',
                'Корневая категория',
            },
            'Correct group names one more time',
        )


async def test_removed(tap, prod_sync_group, uuid, load_json):
    with tap.plan(3):
        _ext_groups = [load_json('data/category.pigeon.json')]
        ext_groups = prod_sync_group._sort_ext_groups(_ext_groups)  # pylint: disable=protected-access
        ext_groups_to_rm = dict()
        new, updated, removed, not_updated = await prod_sync_group.run_pim(
            ext_groups,
            ext_groups_to_rm,
        )
        synced = new + updated + removed + not_updated
        tap.eq_ok(len([i for i in synced if i.status != 'removed']),
                  len(ext_groups), 'загрузили категории новые')
        ext_groups = dict()
        ext_groups_to_rm = prod_sync_group._sort_ext_groups(_ext_groups)
        new, updated, removed, not_updated = await prod_sync_group.run_pim(
            ext_groups,
            ext_groups_to_rm,
        )
        synced = new + updated + removed + not_updated
        tap.eq_ok(len([i for i in synced if i.status != 'removed']),
                  len(ext_groups), 'проставили removed')
        ext_groups = dict()
        ext_groups_to_rm = [uuid()]
        new, updated, removed, not_updated = await prod_sync_group.run_pim(
            ext_groups,
            ext_groups_to_rm,
        )
        synced = new + updated + removed + not_updated
        tap.eq_ok(len([i for i in synced if i.status != 'removed']),
                  len(ext_groups), 'не прошёл мусорный id')


async def test_prepare_product_group(tap, load_json, uuid, prod_sync_group):
    a_category = load_json('data/category.pigeon.json')
    a_category['code'] = uuid()
    group = await prod_sync_group.prepare_obj(JPath(a_category))

    with tap.plan(10, 'основые поля'):
        tap.eq_ok(group.name, 'Root category', 'name')
        tap.eq_ok(group.code, None, 'code')
        tap.eq_ok(group.description, None, 'decription')
        tap.eq_ok(group.order, 50, 'order')
        tap.eq_ok(group.images, [], 'images')
        tap.eq_ok(group.serial, None, 'serial')
        tap.eq_ok(group.products_scope, ['england'], 'products_scope')
        tap.eq_ok(group.status, 'active', 'status')
        tap.eq_ok(group.legal_restrictions, [], 'legal_restrictions')
        tap.eq_ok(group.vars.keys(), {'imported', 'locales', 'errors'}, 'vars')


async def test_vars_errors(tap, dataset, load_json, prod_sync_group):
    with tap.plan(4, 'Проверяем ошибки в vars'):
        a_category = load_json('data/category.pigeon.json')
        a_category['name'] = {}
        prod_group = await dataset.product_group()
        a_category['code'] = prod_group.external_id
        new_group = await prod_sync_group.prepare_obj(JPath(a_category))

        tap.eq(
            new_group.vars['errors'],
            [
                {
                    'code': 'group_no_name',
                    'message': 'Group no name'
                }
            ],
            'Ошибка на месте'
        )

        prod_group.vars['errors'] = [
            {
                'code': 'group_no_name',
                'message': 'Group no name'
            }
        ]
        tap.eq(prod_group, new_group, 'Одинаковые группы')

        a_category['name'] = {'en_US': 'Root category'}

        await new_group.save()

        new_group = await prod_sync_group.prepare_obj(JPath(a_category))

        tap.eq(new_group.vars.get('errors'), [], 'Ошибка ушла')
        prod_group.vars['errors'] = []
        tap.ne(prod_group, new_group, 'Не одинаковые группы')


async def test_no_new_group_errors(tap, prod_sync_group, load_json, uuid):
    with tap.plan(1, 'Группа не создается, если есть ошибки'):
        a_category = load_json('data/category.pigeon.json')
        a_category['name'] = {}
        a_category['code'] = uuid()

        new_group = await prod_sync_group.prepare_obj(JPath(a_category))

        tap.eq(new_group, None, 'Не создали группу')


@pytest.mark.parametrize('categories, expected_answer', [
    (
        'data/more_categories1.pigeon.json',
        {'master', 'master:GB:master', 'master:GB:new', 'master:GB:slave'}
    ),
    (
        'data/more_categories.pigeon.json',
        {
            'front:RU:new_ctm_frozenDesserts',
            '06462c22d7fb11ea8a8f69ac9cf67806',
            'front:RU:ctm_frozenDesserts'
        }
    ),
])
async def test_sort_groups(
        tap, prod_sync_group, load_json, categories, expected_answer):
    with tap.plan(1, 'Проверяем порядок групп'):
        _ext_groups = load_json(categories)
        sort_objs = prod_sync_group._sort_objs(_ext_groups)
        tap.eq(sort_objs.keys(), expected_answer, 'Правильный порядок')


async def test_stash_errors(
        tap, prod_sync_group_client, ext_api, load_json, uuid, dataset):
    with tap.plan(2, 'Проверяем наличие стеша с ошибками'):

        categories = load_json('data/categories.pigeon.json')
        for category in categories[2:4]:
            category['code'] += ':' + uuid()
        prod_group = await dataset.product_group()
        prod_group1 = await dataset.product_group()
        categories[0]['code'] = prod_group.external_id
        categories[1]['code'] = prod_group1.external_id

        stash = await dataset.Stash.stash(
            name=prod_sync_group_client.not_updated_stash_name,
            objs=[]
        )

        stash.value['objs'] = []
        await stash.save()

        async def handler_pigeon(req):
            data = {
                'lastCursor': 2,
                'items': []
            }
            if 'actual-categories' in req.path:
                data['items'] = categories[0:2]
            return web.json_response(
                status=200,
                data=data
            )

        async def new_handler(req):
            data = {
                'lastCursor': 2,
                'items': []
            }
            if 'actual-categories' in req.path:
                data['items'] = categories
            return web.json_response(
                status=200,
                data=data
            )

        async with await ext_api(
            prod_sync_group_client.pim_client, handler_pigeon
        ):
            await prod_sync_group_client.run()

        await stash.reload()

        tap.eq(
            len(stash.value.get('objs')), 1, 'Есть ошибки'
        )

        categories[1]['parentCode'] = None
        categories[2]['parentCode'] = None

        async with await ext_api(
            prod_sync_group_client.pim_client, new_handler
        ):
            await prod_sync_group_client.run()

        await stash.reload()

        tap.eq(
            len(stash.value.get('objs')), 0, 'Ошибок нет'
        )


async def test_fix_child_errors(
        tap, prod_sync_group_client, load_json, dataset, uuid, ext_api):
    with tap.plan(2, 'Ребенок синхронизируется без ошибок'):
        categories = load_json('data/categories.pigeon.json')
        categories[0]["code"] = "Master" + uuid()
        categories[1]["code"] = "Slave" + uuid()
        categories[1]["parentCode"] = categories[0]["code"]

        stash = await dataset.Stash.stash(
            name=prod_sync_group_client.not_updated_stash_name,
            objs=[]
        )

        stash.value['objs'] = []
        await stash.save()

        async def handler_pigeon(req):
            data = {
                'lastCursor': 2,
                'items': []
            }
            if 'actual-categories' in req.path:
                data['items'] = [categories[1]]
            return web.json_response(
                status=200,
                data=data
            )

        async def new_handler(req):
            data = {
                'lastCursor': 3,
                'items': []
            }
            if 'actual-categories' in req.path:
                data['items'] = [categories[0]]
            return web.json_response(
                status=200,
                data=data
            )

        async with await ext_api(
            prod_sync_group_client.pim_client, handler_pigeon
        ):
            await prod_sync_group_client.run()

        await stash.reload()

        tap.eq(
            len(stash.value.get('objs')), 1, 'Есть ошибки'
        )

        async with await ext_api(
            prod_sync_group_client.pim_client, new_handler
        ):
            await prod_sync_group_client.run()

        await stash.reload()

        tap.eq(
            len(stash.value.get('objs')), 0, 'Ошибок нет'
        )
