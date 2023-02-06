from stall.model.default_store_config import DefaultStoreConfig


async def test_nothing(tap, uuid):
    with tap.plan(1, 'Без объекта'):
        config = DefaultStoreConfig({
            'level': 'company',
            'object_id': uuid(),
            'options': {
                'exp_test_1_exp': True,
                'exp_test_2_exp': True,
            }
        })
        obj = await config.get_related_object()
        tap.eq(obj, None, 'Нет объекта')


async def test_company(tap, dataset):
    with tap.plan(2, 'Компания, как объект'):
        company = await dataset.company()
        config = DefaultStoreConfig({
            'level': 'company',
            'object_id': company.company_id,
            'options': {
                'exp_test_1_exp': True,
                'exp_test_2_exp': True,
            }
        })
        obj = await config.get_related_object()
        tap.ok(obj, 'Есть объект')
        tap.eq(obj.company_id, company.company_id, 'Компания правильная')


async def test_cluster(tap, dataset):
    with tap.plan(2, 'Кластер, как объект'):
        cluster = await dataset.cluster()
        config = DefaultStoreConfig({
            'level': 'cluster',
            'object_id': cluster.cluster_id,
            'options': {
                'exp_test_1_exp': True,
                'exp_test_2_exp': True,
            }
        })
        obj = await config.get_related_object()
        tap.ok(obj, 'Есть объект')
        tap.eq(obj.cluster_id, cluster.cluster_id, 'Кластер тот')
