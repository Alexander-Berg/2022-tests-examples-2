ALIAS_ID = 'alias_id'
ORDER_ID = 'order_id'
DRIVER_FREIGHTAGE = {
    'items': [
        {
            'type': 'header',
            'title': 'Договор фрахтования по заказу',
            'id': 'replaceme_header',
        },
        {
            'type': 'default',
            'reverse': True,
            'title': 'Фрахтовщик',
            'subtitle': 'ИП Юдаков Максим Викторович ИНН: 381805387129',
            'id': 'replaceme_item_2',
        },
        {
            'type': 'default_check',
            'checked': True,
            'title': 'Простая ЭП фрахтовщика',
            'id': 'replaceme_item_3',
        },
        {
            'type': 'default',
            'reverse': True,
            'title': 'Фрахтователь',
            'subtitle': '62832199eebd4aeb9940de7ebc7d9716 +793******97',
            'id': 'replaceme_item_4',
        },
        {
            'type': 'default_check',
            'checked': True,
            'title': 'Простая ЭП фрахтователя',
            'id': 'replaceme_item_5',
        },
        {
            'type': 'default',
            'reverse': True,
            'title': 'Тип и государственный номер ТС',
            'subtitle': 'M1 Е009КУ77',
            'id': 'replaceme_item_6',
        },
        {
            'type': 'default',
            'reverse': True,
            'title': 'Место подачи ТС',
            'subtitle': 'Россия, Москва, Садовническая набережная, 79',
            'id': 'replaceme_item_7',
        },
        {
            'type': 'default',
            'reverse': True,
            'title': 'Маршрут',
            'subtitle': 'Россия, Москва, 1-й Щипковский переулок, 2',
            'id': 'replaceme_item_8',
        },
        {
            'type': 'default',
            'reverse': True,
            'title': 'Круг лиц для перевозки',
            'subtitle': 'Определенный',
            'id': 'replaceme_item_9',
        },
        {
            'type': 'default',
            'reverse': True,
            'title': 'Срок выполнения перевозки',
            'subtitle': '26.08.2021',
            'id': 'replaceme_item_10',
        },
        {
            'type': 'default',
            'reverse': True,
            'title': 'Размер платы',
            'subtitle': '0 руб.',
            'id': 'replaceme_item_11',
        },
        {
            'type': 'default',
            'reverse': True,
            'title': 'Допуск пассажиров в ТС',
            'subtitle': 'Единоразовый код',
            'id': 'replaceme_item_12',
        },
    ],
}


async def test_stq_driver_orders_save_freightage(eulas, stq_runner, testpoint):
    alias_id = ALIAS_ID
    order_id = ORDER_ID
    freightage_data = DRIVER_FREIGHTAGE

    eulas.set_response(freightage_data)

    @testpoint('yt-logger-driver-freightage')
    def yt_logger_driver_freightage(data):
        del data['timestamp']
        assert data == {'alias_id': alias_id, 'document': freightage_data}

    await stq_runner.driver_orders_save_driver_freightage.call(
        task_id=alias_id,
        kwargs={'alias_id': alias_id, 'order_id': order_id},
        expect_fail=False,
    )

    assert yt_logger_driver_freightage.times_called == 1
