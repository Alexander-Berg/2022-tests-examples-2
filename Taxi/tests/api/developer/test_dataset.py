import pytest

from stall.model.shelf import Shelf
from stall.model.store import Store
from stall.model.user import User


async def test_user(tap, api):
    with tap.plan(5, 'Создание пользователя'):
        t = await api()

        await t.post_ok('api_developer_dataset',
                        json={
                            'method': 'user',
                            'kwargs': {'role': 'executer'}
                        })
        t.status_is(200, diag=True)

        t.json_has('user_id')
        t.json_is('role', 'executer')

        user_id = t.res['json']['user_id']

        user = await User.load(user_id)
        tap.ok(user, 'Пользователь создан')


async def test_uuid(tap, api):
    with tap.plan(3, 'Генерация uuid'):
        t = await api()

        await t.post_ok('api_developer_dataset',
                        json={
                            'method': 'uuid',
                        })
        t.status_is(200, diag=True)
        t.json_like('uuid', r'^[0-9a-fA-F]{32}$', 'uuid сгенерён')


@pytest.mark.parametrize('repeat', [1, 2, 27])
async def test_repeat(tap, api, repeat):
    with tap.plan(3, 'repeat'):
        t = await api()
        await t.post_ok('api_developer_dataset',
                        json={
                            'method': 'uuid',
                            'repeat': repeat
                        })
        t.status_is(200, diag=True)
        t.json_like(f'{(repeat or 1) - 1}',
                    r'^[0-9a-fA-F]{32}$',
                    'uuid сгенерён')


async def test_multiset_object(tap, api):
    with tap.plan(5, 'store_setup метод с объектом'):
        t = await api()
        await t.post_ok(
            'api_developer_dataset',
            json={
                'method': 'multiset',
                'kwargs': {
                    'store': {'title': 'test store'},
                }
            }
        )
        t.status_is(200, diag=True)

        t.json_has('store')

        store_id = t.res['json']['store']['store_id']
        store = await Store.load(store_id)
        tap.ok(store, 'Store создан')
        tap.eq(store.title, 'test store', 'Store корректен')


async def test_multiset_list(tap, api):
    with tap.plan(10, 'store_setup метод со списком'):
        t = await api()
        await t.post_ok(
            'api_developer_dataset',
            json={
                'method': 'multiset',
                'kwargs': {
                    'store': {'title': 'test store'},
                }
            }
        )
        t.status_is(200, diag=True)

        t.json_has('store')

        store_id = t.res['json']['store']['store_id']
        await t.post_ok(
            'api_developer_dataset',
            json={
                'method': 'multiset',
                'kwargs': {
                    'shelf': [
                        {
                            'store_id': store_id,
                            'title': 'Shelf 1',
                        },
                        {
                            'store_id': store_id,
                            'title': 'Shelf 2',
                        },
                    ]
                }
            }
        )
        t.json_has('shelf')
        shelf_objs = t.res['json']['shelf']
        shelves = await Shelf.list(
            by='full',
            conditions=(
                'shelf_id',
                [shelf['shelf_id'] for shelf in shelf_objs]
            ),
        )
        tap.eq(len(shelves.list), 2, 'Создано 2 полки')
        titles = [shelf.title for shelf in shelves]
        tap.in_ok('Shelf 1', titles, 'Название полки 1 совпадает')
        tap.in_ok('Shelf 2', titles, 'Название полки 2 совпадает')
        tap.eq(shelves.list[0].store_id, store_id, 'store_id корректен')
        tap.eq(shelves.list[1].store_id, store_id, 'store_id корректен')
