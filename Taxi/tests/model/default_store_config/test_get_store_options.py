from stall.model.default_store_config import DefaultStoreConfig


async def test_no_configs(tap, dataset):
    with tap.plan(1, 'Без конфигов'):
        store = await dataset.store()
        options = await DefaultStoreConfig.get_store_options(store)
        tap.eq(options, {}, 'Нет дефолтных опций')


async def test_config(tap, dataset, cfg):
    with tap.plan(1, 'С конфигами'):
        current_config = cfg('business.store.options')
        current_config['exp_test_1_exp'] = True
        current_config['exp_test_2_exp'] = True
        current_config['exp_test_3_exp'] = True
        cfg.set('business.store.options', current_config)
        store = await dataset.store()
        await DefaultStoreConfig({
            'level': 'company',
            'object_id': store.company_id,
            'options': {
                'exp_test_1_exp': True,
                'exp_test_2_exp': True,
            }
        }).save()
        await DefaultStoreConfig({
            'level': 'cluster',
            'object_id': store.cluster_id,
            'options': {
                'exp_test_1_exp': False,
                'exp_test_3_exp': False,
            }
        }).save()

        options = await DefaultStoreConfig.get_store_options(store)
        tap.eq(
            options,
            {
                'exp_test_1_exp': False,
                'exp_test_2_exp': True,
                'exp_test_3_exp': False
            },
            'Дефолты проросли и смержились'
        )
