
async def test_dataset(tap, dataset):
    with tap.plan(4):
        store = await dataset.store()
        provider = await dataset.provider()
        user = await dataset.user(store=store, provider=provider)
        tap.ok(user, 'Объект создан')
        tap.eq(user.company_id, store.company_id, 'company_id')
        tap.eq(user.store_id, store.store_id, 'store_id')
        tap.eq(user.provider_id, provider.provider_id, 'provider_id')


async def test_lang(tap, dataset):
    with tap.plan(4, 'Код языка дожен быть четырехбуквенным'):
        user = await dataset.user()
        with tap.raises(ValueError):
            user.lang = 'ru'
            await user.save()
        with tap.raises(ValueError):
            user.lang = 'RU_ru'
            await user.save()
        user = await dataset.user(lang='ru_RU')
        tap.ok(user, 'Объект создан')
        tap.eq(user.lang, 'ru_RU', 'Правильный код языка')


async def test_pure_python(tap, dataset, uuid):
    with tap.plan(6, 'Сериализация'):
        store = await dataset.store()
        provider = await dataset.provider()
        user = await dataset.user(
            store=store,
            provider=provider,
            pin=uuid(),
            email_hash=uuid(),
            phone_hash=uuid(),
        )
        tap.ok(user.pin, 'pin')
        tap.ok('pin' not in user.pure_python(), 'pin удален')

        tap.ok(user.email_hash, 'email_hash установлен')
        tap.ok(
            'email_hash' not in user.pure_python(),
            'email_hash не сериализован'
        )

        tap.ok(user.phone_hash, 'phone_hash установлен')
        tap.ok(
            'phone_hash' not in user.pure_python(),
            'phone_hash не сериализован'
        )






