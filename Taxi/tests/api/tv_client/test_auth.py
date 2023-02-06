import datetime
import pytest
from libstall.util import now


async def test_code_not_assigned(api, tap, random_secret_key):
    with tap.plan(2):
        t = await api()

        await t.post_ok('api_tv_client_auth',
                        json={'secret_key': random_secret_key})

        t.status_is(403, diag=True)


@pytest.mark.parametrize('set_cookie', [True, False])
async def test_code_auth(dataset,
                         tap,
                         api,
                         set_cookie,
                         random_secret_key):
    with tap.plan(7):
        t = await api()

        secret_key = random_secret_key

        store = await dataset.store()
        device = await dataset.device(store=store, secret_key=secret_key)

        await t.post_ok('api_tv_client_auth',
                        json={'secret_key': secret_key,
                              'lang': 'en_US',
                              'cookie': set_cookie})

        t.status_is(200, diag=True)
        t.json_has('token', 'токен есть')
        t.json_has('device', 'device есть')
        tap.eq(t.res['json']['device']['store_id'],
               store.store_id,
               'store_id верный')

        await device.reload()

        tap.eq(device.lang, 'en_US', 'язык поменялся')

        if set_cookie:
            t.header_has('Set-Cookie', 'Установка кук есть')
        else:
            t.header_hasnt('Set-Cookie', 'Установки кук нет')


async def test_code_auth_inactive_device(dataset,
                                         tap,
                                         api,
                                         random_secret_key):
    with tap.plan(2):
        t = await api()

        code = random_secret_key

        store = await dataset.store()
        await dataset.device(store=store, secret_key=code, status='inactive')

        await t.post_ok('api_tv_client_auth',
                        json={'secret_key': code})

        t.status_is(403, diag=True)


async def test_code_auth_expired(dataset,
                                 tap,
                                 api,
                                 random_secret_key):
    with tap.plan(2):
        t = await api()

        code = random_secret_key

        store = await dataset.store()
        await dataset.device(store=store,
                             secret_key=code,
                             created=now() - datetime.timedelta(minutes=2,
                                                                seconds=1))

        await t.post_ok('api_tv_client_auth',
                        json={'secret_key': code})

        t.status_is(403, diag=True)
