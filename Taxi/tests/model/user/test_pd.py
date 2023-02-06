from stall.client.personal import client as personal


async def test_pd(tap, dataset, uuid, ext_api):
    with tap.plan(10, 'Проверяем работу хешированных полей'):

        store = await dataset.store()
        provider = await dataset.provider()
        user = await dataset.user(
            store=store,
            provider=provider,
            email=f'{uuid()}@yandex.ru',
            phone='+7123456789',
        )

        # pylint: disable=unused-argument
        async def bulk_store(request):
            return {
                'items': [
                    {'id': uuid()},
                ],
            }


        async with await ext_api(personal, bulk_store):
            tap.is_ok(user.email_hash, None, 'email_hash не установлен')
            tap.is_ok(user.phone_hash, None, 'phone_hash не установлен')

            tap.ok(
                await user.reload_phone_pd_id(phone='+7123456780'),
                'ПД телефон получен'
            )
            tap.ok(
                await user.reload_email_pd_id(email=f'{uuid()}@yandex.ru'),
                'ПД почта получен'
            )


            with await user.save():
                tap.ok(user.email_hash, 'email_hash установлен')
                tap.ok(user.phone_hash, 'phone_hash установлен')

            tap.ok(
                await user.reload_phone_pd_id(phone=None),
                'ПД телефон сброшен'
            )
            tap.ok(
                await user.reload_email_pd_id(email=None),
                'ПД почта'
            )

            with await user.save(email=None, phone=None):
                tap.eq(user.email_hash, None, 'email_hash сброшен')
                tap.eq(user.phone_hash, None, 'phone_hash сброшен')
