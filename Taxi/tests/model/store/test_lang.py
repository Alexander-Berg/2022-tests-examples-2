async def test_lang(tap, dataset):
    with tap.plan(4, 'Код языка дожен быть четырехбуквенным'):
        with tap.raises(ValueError):
            await dataset.store(lang='ru')
        with tap.raises(ValueError):
            await dataset.store(lang='RU_ru')
        store = await dataset.store(lang='ru_RU')
        tap.ok(store, 'Объект создан')
        tap.eq(store.lang, 'ru_RU', 'Правильный код языка')
