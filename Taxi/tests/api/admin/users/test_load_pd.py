
from stall.client.personal import client as personal


async def test_phone(tap, api, dataset, ext_api, uuid, unique_phone):
    with tap.plan(4, 'Загрузка ПД телефона пользователя'):

        phone = unique_phone()
        phone_pd_id = uuid()

        user = await dataset.user(phone_pd_id=phone_pd_id)

        # pylint: disable=unused-argument
        async def bulk_retrieve(request):
            return {
                'items': [
                    {'id': phone_pd_id, 'value': phone},
                ],
            }

        async with await ext_api(personal, bulk_retrieve):
            t = await api(user=user)
            await t.post_ok(
                'api_admin_users_load_pd',
                json={'user_id': user.user_id, 'data_type': 'phone'},
            )

            t.status_is(200, diag=True)

            t.json_is('code', 'OK')
            t.json_is('value', phone)


async def test_email(tap, api, dataset, ext_api, uuid, unique_email):
    with tap.plan(4, 'Загрузка ПД почты пользователя'):

        email = unique_email()
        email_pd_id = uuid()

        user = await dataset.user(email_pd_id=email_pd_id)

        # pylint: disable=unused-argument
        async def bulk_retrieve(request):
            return {
                'items': [
                    {'id': email_pd_id, 'value': email},
                ],
            }

        async with await ext_api(personal, bulk_retrieve):
            t = await api(user=user)
            await t.post_ok(
                'api_admin_users_load_pd',
                json={'user_id': user.user_id, 'data_type': 'email'},
            )

            t.status_is(200, diag=True)

            t.json_is('code', 'OK')
            t.json_is('value', email)


async def test_failed(tap, api, dataset, ext_api, uuid):
    with tap.plan(2, 'Ошибка загрузки ПД'):

        email_pd_id = uuid()

        user = await dataset.user(email_pd_id=email_pd_id)

        # pylint: disable=unused-argument
        async def bulk_retrieve(request):
            return 500, ''

        async with await ext_api(personal, bulk_retrieve):
            t = await api(user=user)
            await t.post_ok(
                'api_admin_users_load_pd',
                json={'user_id': user.user_id, 'data_type': 'email'},
            )

            t.status_is(424, diag=True)
