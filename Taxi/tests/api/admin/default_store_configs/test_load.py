async def test_load_by_id(tap, api, dataset, cfg):
    with tap.plan(13, 'Получение конфигов по идентификатору'):
        current_config = cfg('business.store.options')
        current_config['exp_test_1_exp'] = True
        cfg.set('business.store.options', current_config)

        config_1 = await dataset.default_store_config(
            options={'exp_test_1_exp': False})
        config_2 = await dataset.default_store_config(
            options={'exp_test_1_exp': True})
        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_default_store_configs_load',
            json={'default_config_id': config_1.default_config_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is(
            'default_store_config.default_config_id',
            config_1.default_config_id,
            'идентификатор'
        )
        t.json_is(
            'default_store_config.level',
            config_1.level,
            'уровень'
        )
        t.json_is(
            'default_store_config.object_id',
            config_1.object_id,
            'объекта ID'
        )
        t.json_is(
            'default_store_config.options',
            config_1.options,
            'options'
        )
        t = await api(user=user)
        await t.post_ok(
            'api_admin_default_store_configs_load',
            json={
                'default_config_id': [
                    config_1.default_config_id,
                    config_2.default_config_id,
                ]
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_has('default_store_config.0', 'есть первый')
        t.json_has('default_store_config.1', 'есть второй')
        t.json_hasnt('default_store_config.2', 'нет третьего')


async def test_missing_id(tap, api, dataset, uuid, cfg):
    with tap.plan(6, 'Не хватает айдишников'):
        current_config = cfg('business.store.options')
        current_config['exp_test_1_exp'] = True
        cfg.set('business.store.options', current_config)

        config = await dataset.default_store_config(
            options={'exp_test_1_exp': False})
        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_default_store_configs_load',
            json={'default_config_id': uuid()},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код')
        t = await api(user=user)
        await t.post_ok(
            'api_admin_default_store_configs_load',
            json={
                'default_config_id': [
                    config.default_config_id,
                    uuid(),
                ]
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код')


async def test_load_by_company(tap, api, dataset, cfg):
    with tap.plan(4, 'Получение конфигов по компании'):
        current_config = cfg('business.store.options')
        current_config['exp_test_1_exp'] = True
        cfg.set('business.store.options', current_config)
        company = await dataset.company()

        config = await dataset.default_store_config(
            company=company,
            options={'exp_test_1_exp': False}
        )
        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_default_store_configs_load',
            json={
                'level': 'company',
                'object_id': company.company_id,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is(
            'default_store_config.default_config_id',
            config.default_config_id,
            'идентификатор тот'
        )


async def test_missing_company(tap, api, dataset, uuid):
    with tap.plan(3, 'Не хватает компании'):
        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_default_store_configs_load',
            json={
                'level': 'company',
                'object_id': uuid()
            },
        )

        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND', 'код')


async def test_load_by_cluster(tap, api, dataset, cfg):
    with tap.plan(4, 'Получение конфигов по кластеру'):
        current_config = cfg('business.store.options')
        current_config['exp_test_1_exp'] = True
        cfg.set('business.store.options', current_config)
        cluster = await dataset.cluster()

        config = await dataset.default_store_config(
            cluster=cluster,
            options={'exp_test_1_exp': False}
        )
        user = await dataset.user(role='admin')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_default_store_configs_load',
            json={
                'level': 'cluster',
                'object_id': cluster.cluster_id,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is(
            'default_store_config.default_config_id',
            config.default_config_id,
            'идентификатор тот'
        )
