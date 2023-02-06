from datetime import timedelta

import pytest

from libstall.util import token, time2time, now


@pytest.mark.parametrize('role', ['admin', 'chief_audit'])
async def test_generate_qr(tap, api, dataset, role, cfg):
    with tap.plan(9, 'Генерация сервисного QR'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        user = await dataset.user(role=role, store=store)
        tap.ok(user, 'Пользователь создан')

        t = await api(user=user)

        await t.post_ok('api_admin_stores_generate_sqr', json={'ttl': 23})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        service_qr = t.res['json']['service_qr']
        data = token.unpack(
            cfg('web.auth.secret'),
            service_qr
        )
        tap.ok(data, 'Распаковался токен')

        unpacked = data['service_qr']
        tap.eq(unpacked.get('ttl'), 23, 'Правильный ttl')
        tap.eq(unpacked.get('store_id'), store.store_id, 'Правильный store')

        expired = (
            time2time(unpacked.get('created')) +
            timedelta(minutes=unpacked.get('ttl'))
        )
        tap.ok(expired > now(), 'Не просрочился')


@pytest.mark.parametrize('role, json, expected_status', [
    ('admin', {}, 200),  # есть дефолтное значение
    ('executer', {'ttl': 25}, 403),  # нет пермита
    ('admin', {'ttl': 0}, 400),  # не по спеке значение
    ('admin', {'ttl': 3600}, 400),  # не по спеке значение
])
async def test_generate_codes(
        tap, api, dataset, role, json, expected_status):
    with tap.plan(4, 'SQR проверка кодов ответа'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        user = await dataset.user(role=role, store=store)
        tap.ok(user, 'Пользователь создан')

        t = await api(user=user)

        await t.post_ok('api_admin_stores_generate_sqr', json=json)

        t.status_is(expected_status, diag=True)
