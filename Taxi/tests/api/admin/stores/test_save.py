# pylint: disable=too-many-lines

from datetime import datetime, timedelta
import json
import random

import pytest
from libstall.timetable import TimeTable
from stall.model.sampling_condition import SamplingCondition
from stall.model.shelf import (
    Shelf,
    SHELF_TYPES_TECH,
    SHELF_TYPES_KITCHEN_TECH,
)
from stall.model.store import STORE_SOURCES
from stall.model.default_store_config import DefaultStoreConfig


async def test_simple(api, dataset, uuid, tap):
    with tap.plan(3):
        cluster = await dataset.cluster()

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'external_id': uuid(),
                'cluster_id': cluster.cluster_id,
                'source': random.choice(STORE_SOURCES),
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_default_options(api, dataset, uuid, tap, cfg):
    with tap.plan(8, 'Настройки из дополнительных конфигов'):
        current_config = cfg('business.store.options')
        current_config['exp_test_exp'] = True
        cfg.set('business.store.options', current_config)
        company = await dataset.company()
        cluster = await dataset.cluster()
        user = await dataset.user(company_id=company.company_id)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'external_id': uuid(),
                'cluster_id': cluster.cluster_id,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        store_id = t.res['json']['store']['store_id']
        store = await dataset.Store.load(store_id)
        tap.eq(store.options.get('exp_test_exp'), True, 'Глобальный дефолт')
        await DefaultStoreConfig({
            'level': 'company',
            'object_id': company.company_id,
            'options': {'exp_test_exp': False},
        }).save()
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'external_id': uuid(),
                'cluster_id': cluster.cluster_id,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        store_id = t.res['json']['store']['store_id']
        store = await dataset.Store.load(store_id)
        tap.eq(store.options.get('exp_test_exp'), False, 'Дефолт из компании')


@pytest.mark.parametrize('role', ['admin'])
async def test_save_exists(api, dataset, uuid, tap, role):
    with tap.plan(26):
        company = await dataset.company()

        store = await dataset.store(company=company)
        tap.ok(store, 'склад создан')

        new_title = 'Тестовый склад ' + uuid()
        source = random.choice(STORE_SOURCES)

        user = await dataset.user(role=role, store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'company_id': company.company_id,
                'title': new_title,
                'currency': 'EUR',
                'source': source,
                'type': 'dc_external',
                'user_id': 'hello',
                'tz': 'Europe/London',
                'options': {'aaa': 111, 'bbb': True,
                            'tristero': True},
                'area': 880,
                'attr': {
                    'telephone': '88005553535',
                    'telegram': 'some_telegram_id',
                    'email': 'some.email@example.com',
                    'directions': 'пять шагов прямо, потом поверни налево',
                },
                'courier_area_id': '10503',
                'courier_area_title': 'ABCDER',
            },
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('store.store_id', store.store_id)
        t.json_is('store.title', new_title)
        t.json_is('store.source', source)
        t.json_is('store.assortment_id', None)
        t.json_is('store.kitchen_assortment_id', None)
        t.json_is('store.markdown_assortment_id', None)
        t.json_is('store.price_list_id', None)
        t.json_is('store.company_id', company.company_id)
        t.json_is('store.samples', [])
        t.json_is('store.tz', 'Europe/London', 'правильный часовой пояс')
        t.json_isnt('store.user_id', 'hello')
        t.json_is('store.options.aaa', 111)
        t.json_is('store.options.bbb', True)
        t.json_is('store.options.tristero', True)
        t.json_is('store.area', 880)
        t.json_is('store.attr.telephone', '88005553535')
        t.json_is('store.attr.telegram', 'some_telegram_id')
        t.json_is('store.attr.email', 'some.email@example.com')
        t.json_is(
            'store.attr.directions', 'пять шагов прямо, потом поверни налево',
        )
        t.json_is('store.messages_count', 0)
        t.json_is('store.courier_area_id', '10503')
        t.json_is('store.courier_area_title', 'ABCDER')


@pytest.mark.parametrize('role', ['admin'])
async def test_save_cluster_without_store(api, dataset, uuid, tap, role):
    with tap.plan(3, 'Проверяем дефолтные настройки из кластера'
                     ' и кейс несоответствия полей кластера'):
        t = await api(role=role)

        cluster = await dataset.cluster(
            lang='en_EN',
            tz='Europe/London',
            currency='EUR',
        )
        company = await dataset.company()
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'external_id': uuid(),
                'company_id': company.company_id,
                'cluster': cluster.title,
                'cluster_id': cluster.cluster_id,
                'title': 'Тестовый склад ' + uuid(),
            },
        )
        t.status_is(403, diag=True)

        t.json_is('code', 'ER_ACCESS',
                  'нельзя изменять company_id,'
                  ' потому что в stash создался store')


async def test_save_cluster_with_store(api, dataset, uuid, tap):
    with tap.plan(8, 'Проверяем дефолтные настройки из кластера'
                     ' и кейс несоответствия полей кластера'):
        t = await api(role='admin')

        cluster = await dataset.cluster(
            lang='en_EN',
            tz='Europe/London',
            currency='EUR',
        )

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'external_id': uuid(),
                'cluster': uuid(),
                'cluster_id': cluster.cluster_id,
                'title': 'Тестовый склад ' + uuid(),
            },
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('store.cluster', cluster.title)
        t.json_is('store.cluster_id', cluster.cluster_id)
        t.json_is('store.lang', 'en_EN')
        t.json_is('store.tz', 'Europe/London', 'правильный часовой пояс')
        t.json_is('store.currency', 'EUR')


@pytest.mark.parametrize('currency',
                         ['RUB', 'EUR', 'BYN', 'KZT', 'ZAR', 'AED', 'SAR'])
async def test_save_cluster_currency(api, dataset, uuid, tap, currency):
    with tap.plan(8, 'Проверяем дефолтные настройки из кластера '
                     'и валюту'):
        t = await api(role='admin')

        cluster = await dataset.cluster(
            lang='en_EN',
            tz='Europe/London',
            currency=currency,
        )

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'external_id': uuid(),
                'cluster': uuid(),
                'cluster_id': cluster.cluster_id,
                'title': 'Тестовый склад ' + uuid(),
            },
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('store.cluster', cluster.title)
        t.json_is('store.cluster_id', cluster.cluster_id)
        t.json_is('store.lang', 'en_EN')
        t.json_is('store.tz', 'Europe/London', 'правильный часовой пояс')
        t.json_is('store.currency', currency)


@pytest.mark.parametrize('role', ['admin'])
async def test_save_exists_assortment(api, dataset, uuid, tap, role):
    with tap.plan(14):
        assortment = await dataset.assortment()
        tap.ok(assortment, 'ассортимент создан')

        store = await dataset.store(assortment=assortment)
        tap.ok(store, 'склад создан')
        tap.eq(store.assortment_id, assortment.assortment_id, 'ассортимент')

        new_title = 'Тестовый склад ' + uuid()

        user = await dataset.user(role=role, store=store)
        t = await api(user=user)
        await t.post_ok('api_admin_stores_save',
                        json={
                            'store_id': store.store_id,
                            'title': new_title,
                            'currency': 'EUR'
                        })
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_is('store.store_id', store.store_id, 'store_id')
        t.json_is('store.title', new_title, 'title')
        t.json_is('store.assortment_id',
                  assortment.assortment_id,
                  'ассортимент')

        await t.post_ok('api_admin_stores_save',
                        json={
                            'store_id': store.store_id,
                            'title': new_title,
                            'currency': 'EUR',
                            'assortment_id': None
                        })
        t.json_is('code', 'OK', 'code')
        t.json_is('store.store_id', store.store_id, 'store_id')
        t.json_is('store.title', new_title, 'title')
        t.json_is('store.assortment_id', None, 'ассортимент сброшен')


# too long func name
# pylint: disable=invalid-name
@pytest.mark.parametrize('role', ['admin'])
async def test_save_existing_kitchen_assortment(api, dataset, uuid, tap, role):
    with tap.plan(14):
        assortment = await dataset.kitchen_assortment()
        tap.ok(assortment, 'ассортимент кухни создан')

        store = await dataset.store(kitchen_assortment=assortment)
        tap.ok(store, 'склад создан')
        tap.eq(
            store.kitchen_assortment_id, assortment.assortment_id,
            'ассортимент кухни'
        )

        new_title = 'Тестовый склад ' + uuid()

        user = await dataset.user(role=role, store=store)
        t = await api(user=user)
        await t.post_ok('api_admin_stores_save',
                        json={
                            'store_id': store.store_id,
                            'title': new_title,
                            'currency': 'EUR'
                        })
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_is('store.store_id', store.store_id, 'store_id')
        t.json_is('store.title', new_title, 'title')
        t.json_is('store.kitchen_assortment_id',
                  assortment.assortment_id,
                  'ассортимент кухни')

        await t.post_ok('api_admin_stores_save',
                        json={
                            'store_id': store.store_id,
                            'title': new_title,
                            'currency': 'EUR',
                            'kitchen_assortment_id': None
                        })
        t.json_is('code', 'OK', 'code')
        t.json_is('store.store_id', store.store_id, 'store_id')
        t.json_is('store.title', new_title, 'title')
        t.json_is(
            'store.kitchen_assortment_id', None, 'ассортимент кухни сброшен'
        )


@pytest.mark.parametrize('role', ['admin', 'expansioner'])
async def test_save_new_errors(api, uuid, tap, role):
    with tap.plan(11):
        t = await api(role=role)

        new_title = 'Тестовый склад ' + uuid()

        await t.post_ok('api_admin_stores_save',
                        json={})
        t.status_is(400, diag=True)

        t.json_is('code', 'ER_BAD_REQUEST')

        t.json_is('details.errors.0.path',
                  'body.store_id',
                  'store_id in body')
        t.json_is('details.errors.1.path',
                  'body.external_id',
                  'external_id in body')

        await t.post_ok('api_admin_stores_save',
                        json={
                            'title': new_title,
                        })
        t.status_is(400, diag=True)

        t.json_is('code', 'ER_BAD_REQUEST')

        t.json_is('details.errors.0.path',
                  'body.store_id',
                  'store_id in body')
        t.json_is('details.errors.1.path',
                  'body.external_id',
                  'external_id in body')
        t.json_hasnt('details.errors.2.path', 'title error isnt present')


@pytest.mark.parametrize('role', ['admin', 'expansioner'])
async def test_save_new(api, uuid, tap, dataset, role):
    with tap.plan(15):
        user = await dataset.user(role=role)
        t = await api(user=user)

        cluster = await dataset.cluster(title=f'Кластер {uuid()}')

        new_title = 'Тестовый склад ' + uuid()
        external_id = uuid()

        store_id = None

        await t.post_ok('api_admin_stores_save',
                        json={
                            'cluster_id': cluster.cluster_id,
                            'title': new_title,
                            'external_id': external_id,
                            'tz': 'Europe/London'
                        })
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_has('store.store_id', 'склад сохранён')

        if not store_id:
            store_id = t.res['json']['store']['store_id']

        t.json_is('store.external_id',
                  external_id,
                  'Внешний идентификатор склада')
        t.json_is('store.cluster', cluster.title)
        t.json_is('store.cluster_id', cluster.cluster_id)
        t.json_is('store.tz', 'Europe/London', 'правильный часовой пояс')
        t.json_is('store.title', new_title)
        t.json_is('store.store_id', store_id, 'Склад один и тот же')
        t.json_is('store.source', 'wms', 'source выставлен по умолчанию')
        t.json_isnt('store.status', 'active', 'Создаётся неактивный склад')
        t.json_is('store.user_id', user.user_id)

        await t.post_ok('api_admin_stores_save',
                        json={
                            'cluster': cluster.title,
                            'title': new_title,
                            'external_id': external_id,
                        })
        t.status_is(403, diag=True, desc='Повторно нельзя')


@pytest.mark.parametrize('role', ['admin', 'expansioner'])
async def test_save_geo(api, dataset, tap, role):
    with tap.plan(7):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(role=role, store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'address': 'Россия, Москва, улица Паршина, 4, 123103',
                'location': {
                    "geometry": {
                        "coordinates": ["37.461948", 55.789502],
                        "type": "Point",
                    },
                    "properties": {},
                    "type": "Feature",
                }
            },
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_is('store.store_id', store.store_id, 'store_id')
        t.json_is(
            'store.address',
            'Россия, Москва, улица Паршина, 4, 123103',
        )
        t.json_is(
            'store.location',
            {
                "geometry": {
                    "coordinates": [37.461948, 55.789502],
                    "type": "Point",
                },
                "properties": {},
                "type": "Feature",
            }
        )


async def test_save_bad_slug(api, dataset, tap):
    with tap.plan(4, 'проверка что в слаг нельзя пихнуть пробел'):
        t = await api(role='admin')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'slug': 'Чет с пробелом',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST', 'BAD_REQUEST')


@pytest.mark.parametrize('role', ['admin', 'expansioner'])
async def test_set_price_list(api, dataset, tap, role):
    with tap.plan(6):
        store = await dataset.store()
        tap.ok(store, 'Store created')
        tap.is_ok(store.price_list_id, None, 'Store with no price-list')

        price_list = await dataset.price_list()
        tap.ok(price_list, 'Price-list created')

        user = await dataset.user(role=role, store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'price_list_id': price_list.price_list_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('store.price_list_id', price_list.price_list_id)


async def test_fields_permissions(api, dataset, tap):
    with tap.plan(6):
        t = await api(role='category_manager')

        price_list1 = await dataset.price_list()
        price_list2 = await dataset.price_list()
        assortment1 = await dataset.assortment()
        assortment2 = await dataset.assortment()

        store = await dataset.store(
            title='Title1',
            price_list_id=price_list1.price_list_id,
            assortment_id=assortment1.assortment_id,
        )
        tap.ok(store, 'Store created')

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'title': 'Title2',
                'price_list_id': price_list2.price_list_id,
                'assortment_id': assortment2.assortment_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('store.price_list_id', price_list2.price_list_id)
        t.json_is('store.assortment_id', assortment2.assortment_id)
        t.json_is('store.title', 'Title1')


@pytest.mark.parametrize('role', ['admin'])
async def test_set_group_id(api, dataset, tap, role):
    with tap.plan(6):
        store = await dataset.store()
        tap.ok(store, 'Store created')

        tap.is_ok(store.group_id, None, 'Store with no product group')

        product_group = await dataset.product_group()
        tap.ok(product_group, 'Product group created')

        user = await dataset.user(role=role, store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'group_id': product_group.group_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('store.group_id', product_group.group_id)


@pytest.mark.parametrize('role', ['category_manager'])
async def test_fail_to_create(api, uuid, tap, role):
    with tap.plan(4):
        t = await api(role=role)

        new_cluster = 'Кластер ' + uuid()
        new_title = 'Тестовый склад ' + uuid()
        external_id = uuid()

        await t.post_ok('api_admin_stores_save',
                        json={
                            'cluster': new_cluster,
                            'title': new_title,
                            'external_id': external_id
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


@pytest.mark.parametrize('role', ['admin', 'expansioner'])
async def test_cannot_edit_external_id(api, dataset, tap, role):
    with tap.plan(5):
        store = await dataset.store(external_id='old_id')
        user = await dataset.user(role=role, store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_save',
            json={'store_id': store.store_id,
                  'external_id': 'new_id'},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'Склад обновлен')
        t.json_has('store', 'Вернулся склад')
        tap.eq_ok(t.res['json']['store']['external_id'],
                  'old_id',
                  'external_id не поменялся')


@pytest.mark.parametrize('role', ['admin', 'store_admin'])
async def test_set_samples(api, dataset, tap, role):
    with tap.plan(25):
        store = await dataset.store()
        tap.ok(store, 'Store created')

        user = await dataset.user(role=role, store=store)
        tap.ok(user, 'User created')

        t = await api()
        t.set_user(user)

        tap.eq_ok(store.samples, [], 'Store with no samples')

        samples = [
            {'product_id': '0', 'mode': 'required', 'count': 1, 'tags': [],
             'same_client_ttl': None},
            {'product_id': '1', 'mode': 'optional', 'count': 2, 'tags': [],
             'same_client_ttl': None},
            {'product_id': '2', 'mode': 'disabled', 'count': 3, 'tags': [],
             'same_client_ttl': None},
            {
                'product_id': '3',
                'mode': 'optional',
                'count': 4,
                'tags': ['packaging'],
                'same_client_ttl': None,
            },
        ]

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'samples': samples,
            },
        )
        t.status_is(200, diag=True)
        constant_true = SamplingCondition(
            {'condition_type': 'constant_true'}).pure_python()
        expected_samples = [
            {
                'condition': constant_true,
                'dttm_start': None,
                'dttm_till': None,
                # Скоро сэмплы будут хранится в отдельной таблице,
                # поэтому появились эти поля:
                'company_id': None,
                'lsn': None,
                'sample_id': None,
                'serial': None,
                'user_id': None,
                **sample,
            } for sample in samples
        ]
        for i, s in enumerate(expected_samples):
            t.json_is(f'store.samples.{i}.product_id', s['product_id'])
            t.json_is(f'store.samples.{i}.mode', s['mode'])
            t.json_is(f'store.samples.{i}.count', s['count'])
            t.json_is(f'store.samples.{i}.tags', s['tags'])
            t.json_is(f'store.samples.{i}.condition', s['condition'])


@pytest.mark.parametrize('role', ['admin', 'store_admin'])
async def test_set_samples_with_date(api, dataset, tap, role, now):
    with tap.plan(7):
        store = await dataset.store()
        tap.ok(store, 'Store created')

        user = await dataset.user(role=role, store=store)
        tap.ok(user, 'User created')

        t = await api()
        t.set_user(user)

        tap.eq_ok(store.samples, [], 'Store with no samples')

        samples = [{
            'product_id': '0',
            'mode': 'required',
            'count': 1,
            'tags': [],
            'dttm_start': now() + timedelta(days=1),
        }, {
            'product_id': '1',
            'mode': 'optional',
            'count': 2,
            'tags': [],
            'dttm_till': now() + timedelta(days=1),
        }, {
            'product_id': '2',
            'mode': 'disabled',
            'count': 1,
            'tags': [],
            'dttm_start': now(),
            'dttm_till': now() + timedelta(days=1),
        }]

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'samples': samples,
            },
        )
        t.status_is(200, diag=True)

        samples_res = json.loads(t.res['body'])['store']['samples']
        date_res = datetime.fromisoformat(samples_res[0]['dttm_start'])
        date_res = date_res.replace(microsecond=0, tzinfo=None)
        date_exp = samples[0]['dttm_start'].replace(microsecond=0, tzinfo=None)

        tap.eq(date_exp, date_res, 'Specified date')
        tap.eq(samples_res[0]['dttm_till'], None, 'Unspecified date')


@pytest.mark.parametrize('role', ['admin', 'store_admin'])
async def test_set_samples_with_ttl(api, dataset, tap, role):
    with tap.plan(8):
        store = await dataset.store()
        tap.ok(store, 'Store created')

        user = await dataset.user(role=role, store=store)
        tap.ok(user, 'User created')

        t = await api()
        t.set_user(user)

        tap.eq_ok(store.samples, [], 'Store with no samples')

        samples = [{
            'product_id': '0',
            'mode': 'required',
            'count': 1,
            'tags': [],
            'same_client_ttl': 10,
        }, {
            'product_id': '1',
            'mode': 'optional',
            'count': 2,
            'tags': [],
            'same_client_ttl': 14,
        }]

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'samples': samples,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        res = t.res['json']['store']['samples']

        tap.eq(res[0]['same_client_ttl'], 10, 'ttl for sample 1 is 10')
        tap.eq(res[1]['same_client_ttl'], 14, 'ttl for sample 2 is 14')


async def test_sampling_conditions(api, dataset, tap):
    with tap.plan(35):
        store = await dataset.store()
        tap.ok(store, 'Store created')

        user = await dataset.user(role='store_admin', store=store)
        tap.ok(user, 'User created')

        t = await api()
        t.set_user(user)

        tap.eq_ok(store.samples, [], 'Store with no samples')

        samples = [
            {
                'product_id': '10',
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'total_price_above',
                    'total_price': '1234.56',

                },
            },
            {
                'product_id': '11',
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'group_present',
                    'group_id': '12',
                    'children': None,  # это поле должно быть проигнорировано
                },
            },
            {
                'product_id': '110',
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'product_present',
                    'product_id': '12',
                    'count': 3,
                },
            },
            {
                'product_id': '111',
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'product_present',
                    'product_id': '12',
                    'count': None,  # означает то же, что и 1
                },
            },
            {
                'product_id': '13',
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'and',
                    'children': [
                        {
                            'condition_type': 'total_price_above',
                            'total_price': '1234.56'
                        },
                        {
                            'condition_type': 'or',
                            'children': [
                                {
                                    'condition_type': 'group_present',
                                    'group_id': '213',
                                },
                                {
                                    'condition_type': 'group_present',
                                    'group_id': '7131',
                                },
                            ],
                        },
                    ],
                },
            },
            {
                'product_id': '14',
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'tag_present',
                    'client_tag': 'some_tag0',

                },
            },
        ]

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'samples': samples,
            },
        )
        t.status_is(200, diag=True)
        for i, s in enumerate(samples):
            t.json_is(f'store.samples.{i}.product_id', s['product_id'])
            t.json_is(f'store.samples.{i}.mode', s['mode'])
            t.json_is(f'store.samples.{i}.count', s['count'])
            t.json_is(f'store.samples.{i}.tags', s['tags'])
            t.json_is(f'store.samples.{i}.condition',
                      SamplingCondition(s['condition']).pure_python())


async def test_bad_sampling_conditions(api, dataset, tap):
    with tap.plan(8):
        store = await dataset.store()
        tap.ok(store, 'Store created')

        user = await dataset.user(role='store_admin', store=store)
        tap.ok(user, 'User created')

        t = await api()
        t.set_user(user)

        tap.eq_ok(store.samples, [], 'Store with no samples')

        samples = [
            {
                'product_id': '13',
                'mode': 'optional',
                'count': 1,
                'tags': ['sampling'],
                'condition': {
                    'condition_type': 'and',
                },
            },
        ]

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'samples': samples,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Bad request')
        t.json_is('details', {'errors': [{
            'message': 'children not specified in condition and',
            'path': 'samples.0',
        }]})


async def test_cant_change_messages_count(api, dataset, tap, uuid):
    with tap.plan(6):
        t = await api(role='admin')

        token = uuid()
        store = await dataset.store(messages_count=23,
                                    messages_token=token)
        tap.ok(store, 'склад создан')

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'messages_count': 15,
                'messages_token': uuid(),
            },
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('store.messages_count', 23,
                  '"messages_count" did not change')
        t.json_is('store.messages_token', token,
                  '"messages_token" did not change')


async def test_no_cluster(api, uuid, tap):
    with tap.plan(2):
        t = await api(role='admin')
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'external_id': uuid(),
            },
        )

        t.status_is(403, diag=True)


async def test_wrong_cluster(api, dataset, uuid, tap):
    with tap.plan(4):
        company = await dataset.company()
        store = await dataset.store(company=company)
        user = await dataset.user(
            role='city_head',
            clusters_allow=['Москва'],
            store=store
        )

        tap.ok(store, 'склад создан')
        new_title = 'Тестовый склад ' + uuid()
        source = '1c'

        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'company_id': company.company_id,
                'title': new_title,
                'currency': 'EUR',
                'source': source,
                'user_id': 'hello',
                'tz': 'Europe/London',
                'options': {'aaa': 111, 'bbb': True,
                            'tristero': True},
                'area': 880,
                'attr': {
                    'telephone': '88005553535',
                    'telegram': 'some_telegram_id',
                    'email': 'some.email@example.com',
                    'directions': 'пять шагов прямо, потом поверни налево',
                },
                'cluter': 'Не Москва'
            },
        )
        t.status_is(403, diag=True)
        t.json_is('message', 'No access to cluster ' + store.cluster)


async def test_clusters_allow(api, dataset, uuid, tap):
    with tap.plan(24):
        company = await dataset.company()
        store = await dataset.store(company=company,
                                    cluster='Москва')
        user = await dataset.user(
            role='city_head',
            clusters_allow=['Москва'],
            store=store
        )

        tap.ok(store, 'склад создан')

        new_title = 'Тестовый склад ' + uuid()
        source = '1c'

        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'company_id': company.company_id,
                'title': new_title,
                'currency': 'EUR',
                'source': source,
                'user_id': 'hello',
                'tz': 'Europe/London',
                'options': {'aaa': 111, 'bbb': True,
                            'tristero': True},
                'area': 880,
                'attr': {
                    'telephone': '88005553535',
                    'telegram': 'some_telegram_id',
                    'email': 'some.email@example.com',
                    'directions': 'пять шагов прямо, потом поверни налево',
                }
            },
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('store.store_id', store.store_id)
        t.json_isnt('store.title', new_title)
        t.json_isnt('store.source', source)
        t.json_is('store.assortment_id', None)
        t.json_is('store.kitchen_assortment_id', None)
        t.json_is('store.markdown_assortment_id', None)
        t.json_is('store.price_list_id', None)
        t.json_is('store.company_id', company.company_id)
        t.json_is('store.samples', [])
        t.json_isnt('store.tz', 'Europe/London', 'правильный часовой пояс')
        t.json_isnt('store.user_id', 'hello')
        t.json_is('store.options.aaa', 111)
        t.json_is('store.options.bbb', True)
        t.json_is('store.options.tristero', True)
        t.json_isnt('store.area', 880)
        t.json_is('store.attr.telephone', '88005553535')
        t.json_is('store.attr.telegram', 'some_telegram_id')
        t.json_is('store.attr.email', 'some.email@example.com')
        t.json_is(
            'store.attr.directions', 'пять шагов прямо, потом поверни налево',
        )
        t.json_is('store.messages_count', 0)


@pytest.mark.parametrize('role', ['admin'])
async def test_courier_shift_setup(api, dataset, tap, role):
    with tap.plan(5, 'Проверка настроек смен курьера'):
        company = await dataset.company()
        store = await dataset.store(company=company,
                                    cluster='Москва')
        user = await dataset.user(role=role, store=store)
        t = await api(user=user)

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'courier_shift_setup': {'tags': ['test1']},
            },
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('store.store_id', store.store_id)
        t.json_is('store.courier_shift_setup.tags', ['test1'])


async def test_save_company(api, dataset, tap, uuid):
    with tap.plan(7, 'Проверка возможности смены компании'):
        # падает при тестировании в mouse
        # если company_id = None
        company = await dataset.company()
        store = await dataset.store(company=company)
        user = await dataset.user(role='admin')
        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'company_id': uuid(),
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        # возможно потому что сейв не происходит
        company = await dataset.company()
        store = await dataset.store(company=company)

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'company_id': company.company_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('store.store_id', store.store_id)


async def test_users_manage(api, dataset, tap):
    with tap.plan(15, 'изменяем поле users_manage'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        tap.is_ok(store.users_manage, None, 'None')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'users_manage': 'external',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await store.reload()
        tap.eq(store.users_manage, 'external', 'external')

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'users_manage': 'internal',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await store.reload()
        tap.eq(store.users_manage, 'internal', 'internal')

        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'users_manage': None,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await store.reload()
        tap.is_ok(store.users_manage, None, 'None')

@pytest.mark.skip(reason='ждём понедельника')
async def test_save_cost_center(api, dataset, tap):
    with tap.plan(15, 'Проверка возможности сохранения с/без cost_center'):
        store = await dataset.store(status='active')
        user = await dataset.user(role='admin')
        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'company_id': store.company_id,
                'status': 'active',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        old_status = store.status
        await store.reload()
        tap.eq_ok(old_status, store.status, 'Статус не поменялся')
        tap.eq_ok(
            store.cost_center,
            None,
            "OEBS доволен, запись не проставлена, но так должно быть"
        )
        store = await dataset.store(status='disabled')
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'company_id': store.company_id,
                'status': 'active',
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        old_status = store.status
        await store.reload()
        tap.eq_ok(old_status, store.status, 'статус не поменялся')
        tap.eq_ok(
            store.cost_center,
            None,
            "OEBS не доволен, запись не проставлена"
        )
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'company_id': store.company_id,
                'cost_center': 'Lav023',
                'status': 'active',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        old_status = store.status
        await store.reload()
        tap.ok(old_status != store.status, 'статус поменялся')
        tap.eq_ok(
            store.cost_center,
            'Lav023',
            "OEBS доволен, запись проставлена"
        )

async def test_save_check_errors(tap, api, dataset, job, push_events_cache):
    with tap.plan(21, 'проверяем check_errors при сохранении'):
        store = await dataset.store(status='repair')
        user = await dataset.user(role='admin')
        await dataset.shelf(store=store, type='kitchen_components')

        shelves = await Shelf.list_by_store(store_id=store.store_id)
        shelf_types = {s.type for s in shelves}
        for t in SHELF_TYPES_TECH + SHELF_TYPES_KITCHEN_TECH:
            tap.ok(t not in shelf_types, f'нет полки {t}')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'status': 'active',
                'kitchen_assortment_id': 'some_id',
            },
        )
        t.status_is(200)

        await push_events_cache(store, job_method='job_store_check_errors')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        shelves = await Shelf.list_by_store(store_id=store.store_id)
        shelf_types = {s.type for s in shelves}
        for t in SHELF_TYPES_TECH + SHELF_TYPES_KITCHEN_TECH:
            tap.ok(t in shelf_types, f'есть полка {t}')


async def test_save_options_setup(tap, api, dataset, cfg):
    with tap.plan(10, 'Проверяем, что сохраняется options_setup'):
        store = await dataset.store(
            options_setup={
                'exp_mc_hammer_timetable': [
                    {
                        'type': 'everyday',
                        'begin': '10:00',
                        'end': '11:00',
                    }
                ]
            }
        )
        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'options_setup': {'exp_mc_hammer_timetable': []}
            },
        )
        t.status_is(200)
        tap.ok(await store.reload(), 'Перезабрали склад')
        tap.eq(
            store.options_setup.exp_mc_hammer_timetable,
            TimeTable(),
            'Расписание почистили'
        )
        tap.eq(
            store.options_setup.sherlock_border,
            cfg('business.store.sherlock_border'),
            'sherlock_border'
        )
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'options_setup': {
                    'exp_mc_hammer_timetable': [
                        {
                            'type': 'everyday',
                            'begin': '01:00',
                            'end': '02:00',
                        }
                    ],
                    'sherlock_border': 5,
                }
            },
        )
        t.status_is(200)
        tap.ok(await store.reload(), 'Перезабрали склад')
        tap.eq(
            store.options_setup.exp_mc_hammer_timetable,
            TimeTable([{
                'type': 'everyday',
                'begin': '01:00',
                'end': '02:00',
            }]),
            'Расписание обновили'
        )
        tap.eq(
            store.options_setup.sherlock_border,
            5,
            'sherlock_border изменилось'
        )


async def test_save_samples_ids(api, dataset, tap):
    with tap.plan(5):
        company = await dataset.company()

        store = await dataset.store(company=company)
        tap.ok(store, 'склад создан')
        sample = await dataset.sample(company_id=company.company_id)

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'samples_ids': [sample.sample_id],
            },
        )
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('store.samples_ids', [sample.sample_id])


async def test_save_samples_ids_diff_company(api, dataset, tap):
    with tap.plan(5):
        company1 = await dataset.company()
        company2 = await dataset.company()

        store = await dataset.store(company=company1)
        tap.ok(store, 'склад создан')
        sample = await dataset.sample(company_id=company2.company_id)

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'samples_ids': [sample.sample_id],
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Companies of store and sample differ')


async def test_store_status(api, dataset, tap):
    with tap.plan(9, 'сотрудник мониторинга может изменять статус склада'):

        store = await dataset.store(status='active')
        tap.ok(store, 'склад создан')

        t = await api(role='monitoring')
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'status': 'disabled',
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('store.status', 'disabled', 'статус изменен')

        t = await api(role='monitoring')
        await t.post_ok(
            'api_admin_stores_save',
            json={
                'store_id': store.store_id,
                'title': 'складок',
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_isnt('store.title', 'складок', 'название не поменялось')
