import pytest

from libstall.config import cfg
from libstall.util import token
from stall import lp
from stall.model.user import User


async def test_assign_errors(tap, api, uuid):
    tap.plan(4)

    t = await api()

    await t.post_ok('api_courier_user_assign_device')
    t.status_is(400, 'нет json в запросе', diag=True)

    await t.post_ok('api_courier_user_assign_device',
                    json={'device': uuid(), 'barcode': '123'})
    t.status_is(403, diag=True)

    tap()


@pytest.mark.parametrize('attempts', [1, 2])
async def test_assign(tap, api, uuid, dataset, attempts):
    with tap.plan(10 + 8 * attempts):
        t = await api()

        user = await dataset.user(role='courier', nick='Вася')
        tap.ok(user, 'пользователь сгенерирован')
        tap.ok(user.store_id, 'склад задан')
        tap.eq(user.role, 'courier', 'Роль пользователя')

        lp.clean_cache()

        device = uuid()

        for attempt in range(1, attempts + 1):
            await t.post_ok('api_courier_user_assign_device',
                            json={
                                'device': device,
                                'barcode': user.qrcode
                            },
                            desc=f'Попытка залогиниться {attempt}')
            t.status_is(200, diag=True)

            t.json_is('code', 'OK')
            t.json_is('user', user.user_id)
            t.json_is('store', user.store_id)
            t.json_is('fullname', user.nick)
            t.json_has('token', 'токен есть')
            t.json_is('mode', 'wms', 'Режим работы WMS')

        auth_token = t.res['json']['token']

        payload_token = token.unpack(cfg('web.auth.secret'), auth_token)

        tap.isa_ok(payload_token, dict, 'Распаковали токен')

        tap.eq(payload_token.get('user_id'), user.user_id, 'user_id')
        tap.eq(payload_token.get('device'), device, 'device')

        loaded = await user.load(user.user_id)
        tap.ok(loaded, 'Пользователь выбран из БД')
        tap.in_ok(device, loaded.device, 'Устройство в списке у пользователя')

        tap.ok(lp.exists(['device', 'store', user.store_id]),
               'сообщение по склау отправлены')
        tap.ok(
            lp.exists(
                ['device', 'store', user.store_id],
                {
                    'type': 'link',
                    'user': user.user_id,
                    'device': device,
                }
            ),
            'сообщение по склау отправлены (полная проверка)'
        )


async def test_reassign(tap, api, uuid, dataset):
    with tap.plan(17):
        t = await api()

        device = uuid()

        user1 = await dataset.user(role='courier',
                                   nick='Петя',
                                   device=[device])
        tap.ok(user1, 'пользователь сгенерирован')
        tap.ok(user1.store_id, 'склад задан')
        tap.eq(user1.role, 'courier', 'Роль пользователя')
        tap.eq(user1.device, [device], f'девайс {device}')

        user = await dataset.user(role='courier', nick='Вася')
        tap.ok(user, 'пользователь сгенерирован')
        tap.ok(user.store_id, 'склад задан')
        tap.eq(user.role, 'courier', 'Роль пользователя')
        tap.ne(user.device, [device], 'device')

        lp.clean_cache()

        await t.post_ok('api_courier_user_assign_device',
                        json={
                            'device': device,
                            'barcode': user.qrcode
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        l1 = await User.load(user1.user_id)
        l2 = await User.load(user.user_id)

        tap.ok(l1, 'первый пользователь перегружен')
        tap.eq(l1.device, [], 'у него больше нет устройства')

        tap.ok(l2, 'второй пользователь перегружен')
        tap.in_ok(device, l2.device, 'у него прописано устройство')

        tap.ok(
            lp.exists(
                ['device', 'store', l1.store_id],
                {
                    'type': 'unlink',
                    'user': l1.user_id,
                    'device': device
                }
            ),
            'сообщение о разлогине пользователя 1'
        )

        tap.ok(
            lp.exists(
                ['device', 'store', l2.store_id],
                {
                    'type': 'link',
                    'user': l2.user_id,
                    'device': device
                }
            ),
            'сообщение о логине пользователя 2'
        )


async def test_reassign_other_device(tap, api, uuid, dataset):
    with tap.plan(9, 'Тестируем разлогин самого себя на др. устройствах'):
        t = await api()

        old_devices = [uuid(), uuid()]
        device = uuid()

        user = await dataset.user(
            role='courier',
            device=old_devices
        )
        tap.ok(user, 'пользователь создан')

        lp.clean_cache()

        await t.post_ok('api_courier_user_assign_device',
                        json={
                            'device': device,
                            'barcode': user.qrcode
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await user.reload(), 'Перегружен пользователь')

        tap.eq(user.device, [device], 'Девайс у пользователя')

        for i, d in enumerate(old_devices):
            tap.ok(
                lp.exists(
                    ['device', 'store', user.store_id],
                    {
                        'type': 'unlink',
                        'user': user.user_id,
                        'device': d,
                    }
                ),
                f'сообщение о разлогине пользователя {i}'
            )

        tap.ok(
            lp.exists(
                ['device', 'store', user.store_id],
                {
                    'type': 'link',
                    'user': user.user_id,
                    'device': device
                }
            ),
            'сообщение о логине пользователя'
        )
