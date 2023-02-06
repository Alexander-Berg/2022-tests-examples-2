async def test_create(tap, api, dataset, cfg):
    with tap.plan(8, 'Создание конфига'):
        current_config = cfg('business.store.options')
        current_config['exp_test_1_exp'] = True
        cfg.set('business.store.options', current_config)
        user = await dataset.user(role='admin')
        company = await dataset.company()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_default_store_configs_save',
            json={
                'level': 'company',
                'object_id': company.company_id,
                'options': {'exp_test_1_exp': False},
                'vars': {'god': 'why'}
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is(
            'default_store_config.object_id',
            company.company_id,
            'company_id'
        )
        t.json_is(
            'default_store_config.level',
            'company',
            'level'
        )
        config_id = t.res['json']['default_store_config']['default_config_id']
        in_db = await dataset.DefaultStoreConfig.load(config_id)
        tap.ok(in_db, 'В базе нашли конфиг')
        tap.eq(
            in_db.options,
            {'exp_test_1_exp': False},
            'options правильные'
        )
        tap.eq(
            in_db.vars,
            {'god': 'why'},
            'vars правильные'
        )


async def test_create_missing(tap, api, dataset, uuid, cfg):
    with tap.plan(3, 'Создание (нет компании)'):
        current_config = cfg('business.store.options')
        current_config['exp_test_1_exp'] = True
        cfg.set('business.store.options', current_config)
        user = await dataset.user(role='admin')
        t = await api(user=user)
        await t.post_ok(
            'api_admin_default_store_configs_save',
            json={
                'level': 'company',
                'object_id': uuid(),
                'options': {'exp_test_1_exp': False},
                'vars': {'god': 'why'}
            },
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код')


async def test_update(tap, api, dataset, cfg):
    with tap.plan(6, 'Обновление конфига'):
        current_config = cfg('business.store.options')
        current_config['exp_test_1_exp'] = True
        cfg.set('business.store.options', current_config)
        user = await dataset.user(role='admin')
        config = await dataset.default_store_config(options={})
        tap.eq(config.options, {}, 'Нет опций')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_default_store_configs_save',
            json={
                'default_config_id': config.default_config_id,
                'options': {'exp_test_1_exp': True}
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        tap.ok(await config.reload(), 'Перезабрали конфиг')
        tap.eq(
            config.options,
            {'exp_test_1_exp': True},
            'Обновился конфиг'
        )


async def test_change_object(tap, api, dataset, uuid, cfg):
    with tap.plan(4, 'Обновление объекта'):
        current_config = cfg('business.store.options')
        current_config['exp_test_1_exp'] = True
        cfg.set('business.store.options', current_config)
        user = await dataset.user(role='admin')
        config = await dataset.default_store_config(options={})
        tap.eq(config.options, {}, 'Нет опций')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_default_store_configs_save',
            json={
                'default_config_id': config.default_config_id,
                'object_id': uuid(),
                'options': {'exp_test_1_exp': True}
            },
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код')
