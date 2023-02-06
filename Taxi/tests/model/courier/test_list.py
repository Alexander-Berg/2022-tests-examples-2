from stall.model.courier import Courier


async def test_simple(dataset, tap):
    with tap.plan(13, 'Операция получения списка курьеров'):
        courier = await dataset.courier()
        tap.ok(courier, 'курьер создан')

        cursor = await Courier.list(
            by='full',
            conditions=('courier_id', courier.courier_id),
        )
        with cursor:
            tap.ok(cursor.list, 'список получен')
            tap.eq(len(cursor.list), 1, 'в нем один элемент')

            loaded = cursor.list[0]

            tap.isa_ok(loaded, Courier, 'курьер')
            tap.eq(loaded.courier_id, courier.courier_id, 'идентификатор')
            tap.eq(loaded.first_name, courier.first_name, 'имя')
            tap.eq(loaded.middle_name, courier.middle_name, 'отчество')
            tap.eq(loaded.last_name, courier.last_name, 'фамилия')
            tap.eq(loaded.status, courier.status, 'компания')
            tap.eq(loaded.cluster_id, courier.cluster_id, 'кластер')
            tap.eq(loaded.delivery_type, courier.delivery_type, 'тип доставки')
            tap.eq(loaded.tags, courier.tags, 'теги')
            tap.eq(loaded.user_id, courier.user_id, 'создатель')
