from stall.model.printer_task_payload import PrinterTaskPayload


async def test_save(tap):
    tap.plan(6)
    payload = PrinterTaskPayload({'data': 'Hello, world'})
    tap.ok(payload, 'инстанцирован')
    tap.eq(payload.data, 'Hello, world', 'data')


    tap.ok(not payload.payload_id, 'идентификатор пока не назначен')
    tap.ok(await payload.save(), 'сохранено')
    tap.ok(payload.payload_id, 'идентификатор назначен')

    tap.ok(await payload.rm(), 'удалено')


    tap()


async def test_dataset(tap, dataset):
    tap.plan(4)
    payload = await dataset.printer_task_payload(data='Hello')
    tap.ok(payload, 'создан')
    tap.eq(payload.data, 'Hello', 'data')
    tap.ok(payload.payload_id, 'идентификатор')

    tap.ok(await payload.rm(), 'удалено')


    tap()
