from datetime import timedelta

import pytest

from libstall.util import token


@pytest.mark.parametrize('role', ['chief_audit', 'executer'])
async def test_check_sqr(tap, api, dataset, role):
    with tap.plan(9, 'Сквозная проверка SQR'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        user = await dataset.user(role='admin', store=store)
        tap.ok(user, 'Пользователь создан')

        t = await api(user=user, spec='doc/api/admin/stores.yaml')

        await t.post_ok('api_admin_stores_generate_sqr', json={'ttl': 23})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        service_qr = t.res['json']['service_qr']

        check_user = await dataset.user(role=role, store=store)
        tap.ok(check_user, 'Проверяющий пользователь создан')

        t = await api(user=check_user)

        await t.post_ok(
            'api_tsd_check_sqr',
            json={'service_qr': service_qr}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


@pytest.mark.parametrize('expiration, expected_code', [
    (15, 200),
    (25, 403)
])
async def test_expiration(
        tap, now, api, dataset, cfg, expiration, expected_code):
    with tap.plan(4, 'Проверка сервисного QR истекает время'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        user = await dataset.user(role='executer', store=store)
        tap.ok(user, 'Пользователь создан')

        t = await api(user=user)

        service_qr = token.pack(
            cfg('web.auth.secret'),
            service_qr={
                'created': now() - timedelta(minutes=expiration),
                'ttl': 20,
                'store_id': store.store_id,
            }
        )

        await t.post_ok(
            'api_tsd_check_sqr',
            json={'service_qr': service_qr}
        )

        t.status_is(expected_code, diag=True)


async def test_wrong_store(tap, now, api, dataset, cfg, uuid):
    with tap.plan(5, 'Проверка сервисного QR не тот склад'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        user = await dataset.user(role='executer', store=store)
        tap.ok(user, 'Пользователь создан')

        t = await api(user=user)

        service_qr = token.pack(
            cfg('web.auth.secret'),
            service_qr={
                'created': now(),
                'ttl': 20,
                'store_id': uuid(),
            }
        )

        await t.post_ok(
            'api_tsd_check_sqr',
            json={'service_qr': service_qr}
        )

        t.status_is(403, diag=True)
        t.json_is('message', 'Wrong store')


async def test_wrong_sqr(tap, api, dataset):
    with tap.plan(5, 'SQR кривой'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        user = await dataset.user(role='executer', store=store)
        tap.ok(user, 'Пользователь создан')

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_check_sqr',
            json={'service_qr': 'abracadabra'}
        )

        t.status_is(403, diag=True)
        t.json_is('message', 'Invalid service QR')
