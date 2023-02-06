from stall.model.default_store_config import DefaultStoreConfig


async def test_instance(tap, dataset, cfg):
    with tap.plan(6, 'Проверяем базовое инстанцирование'):
        company = await dataset.company()
        current_config = cfg('business.store.options')
        current_config['exp_test_exp'] = True
        cfg.set('business.store.options', current_config)
        instance = DefaultStoreConfig({
            'level': 'company',
            'object_id': company.company_id,
            'options': {'exp_test_exp': True}
        })
        tap.ok(instance, 'Инстанс получился')
        tap.ok(await instance.save(), 'Инстанс сохранился')
        tap.ok(instance.default_config_id, 'Появился ключик')

        from_db = await DefaultStoreConfig.load(instance.default_config_id)
        tap.ok(from_db, 'Достали из базы по ключу')
        by_obj = await DefaultStoreConfig.load(
            ['company', company.company_id], by='object')
        tap.ok(by_obj, 'По объекту достали')
        tap.eq(
            by_obj.default_config_id,
            from_db.default_config_id,
            'Тот же PK'
        )


async def test_dataset(tap, dataset):
    with tap.plan(2, 'Проверить датасет'):
        config = await dataset.default_store_config()
        tap.ok(config, 'Датасет вернул конфиг')
        tap.ok(config.default_config_id, 'Есть ключ')
