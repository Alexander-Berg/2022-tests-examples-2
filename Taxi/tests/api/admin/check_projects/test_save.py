from datetime import timedelta

import pytest

from stall.model.check_project import job_main
from tests.model.check_project.test_create_checks import get_orders_by_project


async def test_save_happy_flow(tap, dataset, uuid, api, now):
    with tap.plan(37, 'тестируем happy flow'):
        user = await dataset.user()
        external_id = uuid()
        cp_tmp = await dataset.check_project()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'external_id': external_id,
                'title': uuid(),
                'products': {'product_id': ['lala1']},
                'stores': {'store_id': ['lala2']},
                'schedule': cp_tmp.schedule,
                'shelf_types': ['store'],
            },
        )

        cp = await dataset.CheckProject.load(external_id, by='external')
        t.status_is(200)
        t.json_is('check_project.external_id', external_id)
        tap.eq(cp.external_id, external_id, 'external_id')
        t.json_is('check_project.status', 'draft')
        tap.eq(cp.status, 'draft', 'status')
        t.json_has('check_project.title')
        t.json_is('check_project.products.product_id', ['lala1'])
        tap.eq(cp.products['product_id'], ['lala1'], 'products')
        t.json_is('check_project.stores.store_id', ['lala2'])
        tap.eq(cp.stores['store_id'], ['lala2'], 'products')
        t.json_is('check_project.schedule', cp_tmp.schedule)
        tap.eq(cp.schedule, cp_tmp.schedule, 'schedule')
        t.json_is('check_project.shelf_types', ['store'])
        tap.eq(cp.shelf_types, ['store'], 'shelf_types')
        t.json_is(
            'check_project.vars',
            {'created_by': user.user_id, 'last_edited_by': user.user_id},
        )
        tap.eq(
            cp.vars,
            {'created_by': user.user_id, 'last_edited_by': user.user_id},
            'vars',
        )

        user2 = await dataset.user()
        schedule = cp.schedule
        some_datetime = now().replace(microsecond=0) + timedelta(days=10)
        schedule.end = some_datetime

        t = await api(user=user2)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'waiting_approve',
                'title': 'trash check project',
                'products': {'product_id': ['lalala1']},
                'stores': {'store_id': ['lalala2']},
                'schedule': schedule,
                'shelf_types': [],
            },
        )
        cp = await dataset.CheckProject.load(external_id, by='external')
        t.status_is(200)
        t.json_is('check_project.external_id', external_id)
        tap.eq(cp.external_id, external_id, 'external_id')
        t.json_is('check_project.status', 'waiting_approve')
        tap.eq(cp.status, 'waiting_approve', 'status')
        t.json_is('check_project.title', 'trash check project')
        tap.eq(cp.title, 'trash check project', 'title')
        t.json_is('check_project.products.product_id', ['lalala1'])
        tap.eq(cp.products['product_id'], ['lalala1'], 'products')
        t.json_is('check_project.stores.store_id', ['lalala2'])
        tap.eq(cp.stores['store_id'], ['lalala2'], 'products')
        t.json_is('check_project.schedule', cp.schedule)
        t.json_is(
            'check_project.schedule.end', str(some_datetime).replace(' ', 'T')
        )
        tap.eq(cp.schedule, cp.schedule, 'schedule')
        tap.eq(cp.schedule.end, some_datetime, 'schedule.end')
        t.json_is('check_project.shelf_types', [])
        tap.eq(cp.shelf_types, [], 'shelf_types')

        t.json_is(
            'check_project.vars',
            {'created_by': user.user_id, 'last_edited_by': user2.user_id},
        )
        tap.eq(
            cp.vars,
            {'created_by': user.user_id, 'last_edited_by': user2.user_id},
            'vars',
        )


async def test_save_approve(tap, dataset, uuid, api):
    with tap.plan(12, 'тестируем аппрувы'):
        user = await dataset.user()
        external_id = uuid()
        cp_tmp = await dataset.check_project()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'external_id': external_id,
                'title': uuid(),
                'products': {'product_id': ['lala1']},
                'stores': {'store_id': ['lala2']},
                'schedule': cp_tmp.schedule,
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'draft')
        cp = await dataset.CheckProject.load(external_id, by='external')

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'waiting_approve',
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'waiting_approve')

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'active',
            },
        )
        t.status_is(403)
        t.json_is('code', 'ER_ACCESS')

        user2 = await dataset.user()
        t = await api(user=user2)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'active',
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'active')


@pytest.mark.parametrize(
    'path',
    [
        ['draft', 'waiting_approve', 'active', 'disabled', 'removed'],
        ['draft', 'draft', 'waiting_approve', 'draft', 'removed'],
        ['draft', 'draft', 'removed'],
        [
            'draft',
            'waiting_approve',
            'draft',
            'waiting_approve',
            'active',
            'removed',
        ],
        ['draft', 'draft', 'removed'],
        ['draft', 'waiting_approve', 'removed'],
        [
            'draft',
            'waiting_approve',
            'waiting_approve',
            'active',
            'disabled',
            'removed',
        ],
    ]
)
async def test_save_diff_status_paths(tap, dataset, api, uuid, path):
    #pylint: disable=too-many-locals
    add_steps_cnt = 0
    for i, status in enumerate(path[:-1]):
        if status == 'waiting_approve' and path[i+1] == 'active':
            add_steps_cnt += 2

    with tap.plan(
            add_steps_cnt + len(path) * 5,
            'тестируем разные прогулки по статусам'
    ):
        users = [await dataset.user() for _ in range(2)]
        external_id = uuid()
        cp = await dataset.check_project()
        check_project_id = None

        for status in path:
            for user in users:
                t = await api(user=user)
                json = {
                    'external_id': external_id,
                    'title': cp.title,
                    'status': status,
                    'products': cp.products,
                    'stores': cp.stores,
                    'schedule': cp.schedule,
                }
                if check_project_id:
                    json['check_project_id'] = check_project_id
                await t.post_ok(
                    'api_admin_check_projects_save',
                    json=json,
                )
                t.json_has('code')
                res = t.res
                if res['status'] == 200:
                    t.status_is(200)
                    t.json_is('code', 'OK')
                    t.json_is('check_project.status', status)
                    res_check_project = res['json']['check_project']
                    check_project_id = res_check_project['check_project_id']
                    break


async def test_save_permit(tap, dataset, api):
    with tap.plan(8, 'тестируем пермит на save'):
        user = await dataset.user(role='support_it')
        cp = await dataset.check_project(status='draft')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_check_projects_load',
            json={'check_project_id': cp.check_project_id},
        )
        t.status_is(200)
        t.json_is('code', 'OK')
        t.json_is('check_project.check_project_id', cp.check_project_id)
        t.json_is('check_project.title', cp.title)

        await t.post_ok(
            'api_admin_check_projects_save',
            json={'check_project_id': cp.check_project_id, 'status': 'draft'},
        )
        t.status_is(403)
        t.json_is('code', 'ER_ACCESS')


async def test_save_decline_other_fix(tap, dataset, api, uuid):
    with tap.plan(19, 'отклонил один фиксит другой'):
        user = await dataset.user()
        external_id = uuid()
        cp_tmp = await dataset.check_project()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'external_id': external_id,
                'title': uuid(),
                'products': {'product_id': ['lala1']},
                'stores': {'store_id': ['lala2']},
                'schedule': cp_tmp.schedule,
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'draft')
        cp = await dataset.CheckProject.load(external_id, by='external')

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'waiting_approve',
            }
        )
        t.status_is(200)
        t.json_is('check_project.status', 'waiting_approve')

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'draft',
            }
        )
        t.status_is(200)
        t.json_is('check_project.status', 'draft')
        t.json_is('check_project.vars.declined_by', user.user_id)

        user2 = await dataset.user()
        t = await api(user=user2)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'waiting_approve',
            }
        )
        t.status_is(200)
        t.json_is('check_project.status', 'waiting_approve')

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'active',
            }
        )
        t.status_is(403)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'active',
            }
        )
        t.status_is(200)
        t.json_is('check_project.status', 'active')
        t.json_is('check_project.vars.approved_by', user.user_id)


async def test_save_decline_same_fix(tap, dataset, api, uuid):
    with tap.plan(36, 'отклонил один фиксит он же'):
        user = await dataset.user()
        external_id = uuid()
        cp_tmp = await dataset.check_project()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'external_id': external_id,
                'title': uuid(),
                'products': {'product_id': ['lala1']},
                'stores': {'store_id': ['lala2']},
                'schedule': cp_tmp.schedule,
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'draft')
        cp = await dataset.CheckProject.load(external_id, by='external')

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'waiting_approve',
            }
        )
        t.status_is(200)
        t.json_is('check_project.status', 'waiting_approve')

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'draft',
            }
        )
        t.status_is(200)
        t.json_is('check_project.status', 'draft')
        t.json_is('check_project.vars.declined_by', user.user_id)

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'waiting_approve',
            }
        )
        t.status_is(200)
        t.json_is('check_project.status', 'waiting_approve')
        t.json_hasnt('check_project.vars.declined_by')

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'active',
            }
        )
        t.status_is(403)

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'draft',
            }
        )
        t.status_is(200)
        t.json_is('check_project.status', 'draft')
        t.json_is('check_project.vars.declined_by', user.user_id)

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'draft',
            }
        )
        t.status_is(200)
        t.json_is('check_project.status', 'draft')
        t.json_hasnt('check_project.vars.declined_by')
        t.json_is('check_project.vars.last_edited_by', user.user_id)

        user2 = await dataset.user()
        t = await api(user=user2)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'waiting_approve',
            }
        )
        t.status_is(200)
        t.json_is('check_project.status', 'waiting_approve')
        t.json_is('check_project.vars.last_edited_by', user2.user_id)

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'active',
            }
        )
        t.status_is(403)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'active',
            }
        )
        t.status_is(200)
        t.json_is('check_project.status', 'active')
        t.json_hasnt('check_project.vars.declined_by')
        t.json_is('check_project.vars.approved_by', user.user_id)


async def test_save_no_draft_changes(tap, dataset, api, now, uuid):
    with tap.plan(32, 'тестируем изменения не в статусе draft'):
        user = await dataset.user()
        external_id = uuid()
        cp_tmp = await dataset.check_project()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'external_id': external_id,
                'title': uuid(),
                'products': {'product_id': ['lala1']},
                'stores': {'store_id': ['lala2']},
                'schedule': cp_tmp.schedule,
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'draft')
        cp = await dataset.CheckProject.load(external_id, by='external')

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'waiting_approve',
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'waiting_approve')

        cp_tmp2 = await dataset.check_project()
        cp_tmp2.schedule.end = now() + timedelta(days=123)

        changes = {
            'title': uuid(),
            'products': {'product_id': ['lalala1']},
            'stores': {'store_id': ['lalala2']},
            'schedule': cp_tmp2.schedule,
            'shelf_types': ['store'],
        }

        for att_name, att_value in changes.items():
            await t.post_ok(
                'api_admin_check_projects_save',
                json={
                    'check_project_id': cp.check_project_id,
                    'status': 'draft',
                    att_name: att_value,
                },
            )
            t.status_is(403)
            await cp.reload()
            tap.eq(cp.status, 'waiting_approve', 'статус тот же')
            tap.ok(getattr(cp, att_name) != att_value, 'не поменялось')

        old_title = cp.title
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'draft',
                'title': old_title,
                'products': {'product_id': ['lala1']},
                'stores': {'store_id': ['lala2']},
                'schedule': cp_tmp.schedule,
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'draft')

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'waiting_approve',
                **changes,
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'waiting_approve')


async def test_save_approved(tap, dataset, uuid, api):
    with tap.plan(10, 'тестируем появление approved_by'):
        user = await dataset.user()
        external_id = uuid()
        cp_tmp = await dataset.check_project()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'external_id': external_id,
                'title': uuid(),
                'products': {'product_id': ['lala1']},
                'stores': {'store_id': ['lala2']},
                'schedule': cp_tmp.schedule,
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'draft')
        cp = await dataset.CheckProject.load(external_id, by='external')

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'waiting_approve',
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'waiting_approve')

        user2 = await dataset.user()
        t = await api(user=user2)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'active',
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'active')
        t.json_is('check_project.vars.approved_by', user2.user_id)


async def test_save_check_schedule(tap, dataset, uuid, api, now):
    with tap.plan(11, 'тестируем проверку корректности schedule'):
        user = await dataset.user()
        external_id = uuid()
        _now = now()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'external_id': external_id,
                'title': uuid(),
                'products': {'product_id': ['lala1']},
                'stores': {'store_id': ['lala2']},
                'schedule': {'timetable': [], 'begin': _now},
            },
        )
        t.status_is(403)

        cp_tmp = await dataset.check_project()
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'external_id': external_id,
                'title': uuid(),
                'products': {'product_id': ['lala1']},
                'stores': {'store_id': ['lala2']},
                'schedule': cp_tmp.schedule,
            },
        )
        t.status_is(200)
        t.json_is('check_project.status', 'draft')
        cp = await dataset.CheckProject.load(external_id, by='external')

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'schedule': {
                    'timetable': [{
                        'type': 'everyday',
                        'begin': _now.time(),
                        'end': (_now + timedelta(seconds=1)).time()
                    }],
                    'begin': cp_tmp.schedule.begin,
                    'end': cp_tmp.schedule.end,
                }
            }
        )
        t.status_is(400)
        t.json_is(
            'message',
            'begin should be equal end for every timetable item',
        )

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'schedule': {
                    'timetable': [],
                    'begin': cp_tmp.schedule.begin,
                    'end': None,
                }
            }
        )
        t.status_is(400)
        t.json_is(
            'message',
            'begin should be equal end for single launch',
        )


async def test_save_after_error(tap, dataset, api, now, cfg):
    with tap.plan(7, 'тестим сохранение ошибки в проекте'):
        cfg.set('business.order.check.products_count_limit', 2)
        store = await dataset.store(options={'exp_big_brother': True})
        _now = now()

        products = [await dataset.product() for _ in range(3)]

        cp = await dataset.check_project(
            products={
                'product_id': [product.product_id for product in products],
            },
            stores={'store_id': [store.store_id]},
            schedule={
                'timetable': [{
                    'type': 'everyday',
                    'begin': _now.time(),
                    'end': _now.time(),
                }],
                'begin': _now,
            },
        )
        await job_main(_now, [cp.check_project_id])
        created_orders = await get_orders_by_project(
            cp.check_project_id, store.store_id,
        )
        tap.ok(not created_orders, 'ордеры не созданы')
        await cp.reload()
        tap.eq(cp.vars['errors'], ['too_many_products'], 'ошибка есть')

        user = await dataset.user(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'status': 'removed',
            }
        )
        t.status_is(200)
        t.json_is('code', 'OK')

        await cp.reload()
        tap.eq(cp.status, 'removed', 'статус поменялся')
        tap.eq(cp.vars['errors'], ['too_many_products'], 'ошибка есть')


async def test_removed_product(tap, dataset, api):
    with tap.plan(4, 'Добавить в проект удаленный продукт'):
        store = await dataset.store()
        good_product = await dataset.product()
        bad_product = await dataset.product(status='removed')

        cp = await dataset.check_project(
            products={
                'product_id': [good_product.product_id],
            },
            stores={'store_id': [store.store_id]},
            status='draft',
        )
        user = await dataset.user()

        t = await api(user=user)

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'products': {'product_id': [bad_product.product_id]}
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Removed product')


async def test_removed_new(tap, dataset, api, uuid):
    with tap.plan(4, 'Новый проект с удаленным продуктом'):
        store = await dataset.store()
        bad_product = await dataset.product(status='removed')

        cp_tmp = await dataset.check_project()
        user = await dataset.user()

        t = await api(user=user)

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'external_id': uuid(),
                'title': uuid(),
                'products': {'product_id': [bad_product.product_id]},
                'stores': {'store_id': [store.store_id]},
                'schedule': cp_tmp.schedule,
                'shelf_types': ['store'],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Removed product')


async def test_kitchen_product(tap, dataset, api):
    with tap.plan(4, 'Добавить в проект кухонный продукт'):
        store = await dataset.store()
        component = await dataset.product()
        good_product = await dataset.product()
        bad_product = await dataset.product(
            components=[[{'product_id': component.product_id, 'count': 1}]]
        )

        cp = await dataset.check_project(
            products={
                'product_id': [good_product.product_id],
            },
            stores={'store_id': [store.store_id]},
            status='draft',
        )
        user = await dataset.user()

        t = await api(user=user)

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'check_project_id': cp.check_project_id,
                'products': {'product_id': [bad_product.product_id]}
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Kitchen product')


async def test_kitchen_new(tap, dataset, api, uuid):
    with tap.plan(4, 'Новый проект с удаленным продуктом'):
        store = await dataset.store()
        component = await dataset.product()
        bad_product = await dataset.product(
            components=[[{'product_id': component.product_id, 'count': 1}]]
        )
        cp_tmp = await dataset.check_project()
        user = await dataset.user()

        t = await api(user=user)

        await t.post_ok(
            'api_admin_check_projects_save',
            json={
                'external_id': uuid(),
                'title': uuid(),
                'products': {'product_id': [bad_product.product_id]},
                'stores': {'store_id': [store.store_id]},
                'schedule': cp_tmp.schedule,
                'shelf_types': ['store'],
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Kitchen product')
