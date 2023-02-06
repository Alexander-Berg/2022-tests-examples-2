async def test_add(tap, dataset):
    with tap.plan(3):
        group = await dataset.product_group()

        tap.ok(not group.vars('locales', None), 'нет локалей')

        group.locales.add('name', 'milk', 'en_US')
        group.locales.add('name', 'молочко', 'ru_RU')

        await group.save()

        tap.eq(len(group.locales), 1, 'добавили переводы')
        tap.eq(
            group.locales['name'],
            {'en_US': 'milk', 'ru_RU': 'молочко'},
            'name',
        )


async def test_pure_python(tap, dataset):
    with tap.plan(3):
        group = await dataset.product_group(
            vars={
                'locales': {
                    'name': {
                        'en_US': 'milkkk',
                        'ru_RU': 'молочкоооо',
                    },
                }
            }
        )

        tap.ok(group.vars('locales'), 'есть локали')

        en = group.pure_python(lang='en')

        tap.eq(en['name'], 'milkkk', 'перевод поля')

        ru = group.pure_python(lang='ru_RU')

        tap.eq(ru['name'], 'молочкоооо', 'перевод поля')
