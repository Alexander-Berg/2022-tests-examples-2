from stall.model.courier import Courier


async def test_save(tap):
    with tap.plan(14, 'Операции сохранения / загрузки'):
        courier = Courier()
        tap.ok(courier, 'инстанцирован')

        tap.eq(courier.courier_id, None, 'идентификатора до сохранения нет')
        tap.ok(await courier.save(), 'сохранен')
        tap.ok(courier.courier_id, 'идентификатор назначился')
        courier_id = courier.courier_id

        tap.eq(courier.first_name, None, 'имени нет')
        courier.first_name = 'Алексей'
        tap.ok(await courier.save(), 'сохранен еще раз')
        tap.eq(courier.courier_id, courier_id, 'идентификатор не поменялся')
        tap.eq(courier.first_name, 'Алексей', 'имя сохранено верно')

        loaded = await Courier.load(courier_id)
        tap.ok(loaded, 'загружено')
        tap.isa_ok(loaded, Courier, 'тип')
        tap.eq(loaded.first_name, courier.first_name, 'ник')
        tap.eq(loaded.courier_id, courier.courier_id, 'id')

        tap.ok(await courier.rm(), 'удалён')
        tap.ok(not await Courier.load(courier_id), 'удалён в БД')
