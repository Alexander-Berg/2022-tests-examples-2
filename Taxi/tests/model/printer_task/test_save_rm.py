from stall.model.printer_task import PrinterTask

async def test_save_rm(tap, uuid, dataset):
    with tap.plan(7, 'Создание удаление'):
        payload = await dataset.printer_task_payload(data=uuid())
        tap.ok(payload, f'payload создан [shard={payload.shardno}]')


        task = PrinterTask({
            'store_id': uuid(),
            'type': 'pdf',
            'payload_id': payload.payload_id})
        tap.ok(task, 'инстанцировано')

        tap.ok(not task.task_id, 'идентификатора пока нет')
        tap.ok(await task.save(), 'сохранено')
        tap.ok(task.task_id, 'идентификатор назначен')


        tap.ok(await task.rm(force=True), 'Удалён таск')
        tap.ok(not await payload.load(payload.payload_id),
               'payload в БД тоже удалён')

async def test_rm_lsn(tap, dataset, uuid):
    with tap.plan(3, 'lsn растёт при пометке как удалённое'):
        task = await dataset.printer_task(data=uuid())
        tap.eq(task.status, 'processing', 'таска создана')
        lsn = task.lsn

        tap.ok(await task.rm(), 'таска удалена')
        tap.ne(task.lsn, lsn, 'lsn увеличился')
