import argparse

from aiohttp import web

from scripts.cron.update_phones_from_staff import update_phone
from stall.client.personal import client as personal
from stall.client.staff import StaffClient


async def test_updates(tap, dataset, uuid, ext_api):
    with tap.plan(8, 'Обновление телефона'):
        user_no_phone = await dataset.user(
            provider='yandex-team',
            email='email@yandex.ru',
            provider_user_id=uuid(),
        )
        user_with_phone = await dataset.user(
            provider='yandex-team',
            email='email@yandex.ru',
            provider_user_id=uuid(),
            phone='+71234567890',
        )

        tap.ok(user_no_phone, 'Пользователь без телефона')
        tap.ok(user_with_phone, 'Пользователь c телефоном')

        phone_pd_id = uuid()

        # pylint: disable=unused-argument
        async def bulk_store(request):
            return web.json_response({
                'items': [
                    {'id': phone_pd_id}
                ]
            })

        requests = []
        async def handler(request):
            requests.append(request)

            if len(requests) == 1:
                return web.json_response(
                    {
                        'result': [
                            {"phones":
                                [
                                    {
                                        "number": "+7 123 456-78-90",
                                        "type": "mobile",
                                    }
                                ],
                                'id': 1,
                                'uid': user_no_phone.provider_user_id,
                                'login': 'login',
                            },
                            {"phones":
                                [
                                    {
                                        "number": "+7 123 456-70-90",
                                        "type": "mobile",
                                    }
                                ],
                                'id': 2,
                                'uid': user_with_phone.provider_user_id,
                                'login': 'login',
                            },
                        ],
                    }
                )
            if len(requests) == 2:
                return web.json_response(
                    {
                        'result': []
                    }
                )

        staff_client = StaffClient()

        async with await ext_api(personal, bulk_store):
            async with await ext_api(staff_client, handler) as client:
                staff_data = await client.get_users_by_query(
                    fields=[],
                    query='',
                )

        args = argparse.Namespace(
            apply=True,
        )

        await update_phone(
            {
                user_no_phone.provider_user_id: user_no_phone,
                user_with_phone.provider_user_id: user_with_phone,
            },
            staff_data,
            args
        )

        await user_no_phone.reload()
        tap.eq(user_no_phone.phone, '+71234567890', 'Телефон изменился')
        tap.ok(user_no_phone.phone_hash, 'Хеш телефона изменился')
        tap.eq(user_no_phone.phone_pd_id, phone_pd_id, 'Идентификатор ПД')

        await user_with_phone.reload()
        tap.eq(user_with_phone.phone, '+71234567090', 'Телефон изменился')
        tap.ok(user_with_phone.phone_hash, 'Хеш телефона изменился')
        tap.eq(user_with_phone.phone_pd_id, phone_pd_id, 'Идентификатор ПД')
