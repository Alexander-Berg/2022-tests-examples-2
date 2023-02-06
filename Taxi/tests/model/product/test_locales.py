async def test_add(tap, dataset):
    with tap.plan(4, 'добавление локализованных полей'):
        product = await dataset.product()

        tap.ok(not product.vars('locales', None), 'нет локалей')

        product.locales.add('title', 'milk', 'en_US')
        product.locales.add('long_title', 'milkkk', 'en_US')
        product.locales.add('long_title', 'молочкоооо', 'ru_RU')

        await product.save()

        tap.eq(len(product.locales), 2, 'добавили переводы')
        tap.eq(product.locales['title'], {'en_US': 'milk'}, 'title')
        tap.eq(
            product.locales['long_title'],
            {'en_US': 'milkkk', 'ru_RU': 'молочкоооо'},
            'long_title',
        )


async def test_merge(tap, dataset):
    with tap.plan(5, 'мерж полей'):
        product = await dataset.product()

        tap.ok(not product.vars('locales', None), 'нет локалей')

        product.locales.add('title', 'milk', 'en_US')
        product.locales.add('title', 'молочко', 'ru_RU')
        product.locales.add('work_title', 'рабочее молочко', 'ru_RU')
        product.locales.add('short_title', 'короткое молочко', 'ru_RU')

        await product.save()

        tap.eq(len(product.locales), 3, 'добавили переводы')

        product.locales.merge('title', 'work_title', 'short_title')

        tap.eq(
            product.locales['title'],
            {'en_US': 'milk', 'ru_RU': 'короткое молочко'},
            'title',
        )

        product.locales.merge('title2', 'title')
        tap.eq(
            product.locales['title2'],
            {'en_US': 'milk', 'ru_RU': 'короткое молочко'},
            'title -> title2',
        )

        product.locales.merge('title2', 'title2')
        tap.eq(
            product.locales['title2'],
            {'en_US': 'milk', 'ru_RU': 'короткое молочко'},
            'title2 -> title2 не теряем ключ',
        )


async def test_by_lang(tap, dataset):
    with tap.plan(5):
        product = await dataset.product(
            vars={
                'locales': {
                    'title': {'en_US': 'milk'},
                    'long_title': {'en_US': 'long milk', 'he_IL': 'j milk'},
                }
            }
        )

        tap.eq(len(product.locales), 2, 'добавили переводы')

        tap.eq(
            product.locales.by_lang('en_US'),
            {'title': 'milk', 'long_title': 'long milk'},
            'en_US',
        )
        tap.eq(
            product.locales.by_lang('en'),
            {'title': 'milk', 'long_title': 'long milk'},
            'en',
        )
        tap.eq(
            product.locales.by_lang('he'),
            {'long_title': 'j milk'},
            'he',
        )
        tap.eq(
            product.locales.by_lang('kr'),
            {},
            'не такого языка у нас',
        )



async def test_pure_python(tap, dataset):
    with tap.plan(4, 'при передаче языка сразу переведенный дикт'):
        product = await dataset.product(
            vars={
                'locales': {
                    'title': {'en_US': 'milk'},
                    'long_title': {
                        'en_US': 'milkkk',
                        'ru_RU': 'молочкоооо',
                    },
                }
            }
        )

        tap.ok(product.vars('locales'), 'есть локали')

        en = product.pure_python(lang='en')

        tap.eq(en['title'], 'milk', 'перевод поля')
        tap.eq(en['long_title'], 'milkkk', 'перевод поля')

        ru = product.pure_python(lang='ru_RU')

        tap.eq(ru['long_title'], 'молочкоооо', 'перевод поля')
