async def test_save(api, tap, dataset):
    with tap.plan(6, 'Сохранение настроек пользователем'):

        user = await dataset.user(role='barcode_executer', lang='ru_RU')
        tap.eq(user.lang, 'ru_RU', 'ru_RU')

        t = await api(user=user)

        await t.post_ok('api_tsd_user_options_save', json={'lang': 'en_EN'})
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_has('user', 'user')
        t.json_is('user.lang', 'en_EN')


async def test_save_virtual(api, tap):
    with tap.plan(4, 'Сохраняем в виртуальную роль'):
        t = await api()

        await t.post_ok('api_tsd_user_options_save', json={'lang': 'en_EN'})
        t.status_is(400, diag=True)

        t.json_is('code', 'ER_VIRTUAL_ROLE', 'code')
        t.json_is('message', 'Can\'t save virtual role', 'message')
