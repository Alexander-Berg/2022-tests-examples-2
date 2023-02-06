
from stall.client.personal import client as personal


async def test_phone(tap, api, dataset, ext_api, uuid, unique_phone):
    with tap.plan(5, 'Загрузка ПД телефона пользователя'):

        phone = unique_phone()
        phone_pd_id = uuid()

        user = await dataset.user(phone_pd_id=phone_pd_id)

        # pylint: disable=unused-argument
        async def bulk_store(request):
            return {
                'items': [
                    {'id': phone_pd_id, 'value': phone},
                ],
            }

        async with await ext_api(personal, bulk_store):
            t = await api(user=user)
            await t.post_ok(
                'api_admin_users_save_pd',
                json={
                    'data_type': 'phone',
                    'value': phone,
                },
            )

            t.status_is(200, diag=True)

            t.json_is('code', 'OK')
            t.json_is('id', phone_pd_id)
            t.json_is('value', phone)


async def test_failed(tap, api, dataset, ext_api, unique_email):
    with tap.plan(2, 'Ошибка загрузки ПД'):

        email = unique_email()

        user = await dataset.user()

        # pylint: disable=unused-argument
        async def bulk_store(request):
            return 500, ''

        async with await ext_api(personal, bulk_store):
            t = await api(user=user)
            await t.post_ok(
                'api_admin_users_save_pd',
                json={
                    'data_type': 'email',
                    'value': email,
                },
            )

            t.status_is(424, diag=True)
