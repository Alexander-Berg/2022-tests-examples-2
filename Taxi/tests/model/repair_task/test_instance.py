from stall.model.repair_task import RepairTask


async def test_instance(uuid, tap, dataset):
    with tap.plan(7, 'Создание и сохранение заявки на ремонт'):
        store = await dataset.store()
        task = RepairTask({
            'external_id': uuid(),
            'status': 'NEW',
            'store_id': store.store_id,
            'vars': {'lavkach_type': 'REPAIR'},
            'company_id': store.company_id,
        })

        saved = await task.save()

        loaded = await RepairTask.load(saved.task_id)
        tap.ok(loaded, 'загрузили')
        tap.eq(loaded.external_id, task.external_id, 'external_id')
        tap.eq(loaded.type, 'assets', 'type')
        tap.eq(loaded.source, 'lavkach', 'source')
        tap.eq(loaded.status, 'NEW', 'status')
        tap.eq(loaded.store_id, task.store_id, 'store_id')
        tap.eq(loaded.vars.get('lavkach_type'), 'REPAIR', 'lavkach_type')
