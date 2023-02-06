from testsuite.utils import matching


async def test_stq(
        taxi_cargo_c2c,
        stq_runner,
        create_cargo_c2c_orders,
        mock_claims_full,
        stq,
):
    order_id = await create_cargo_c2c_orders()
    await stq_runner.cargo_c2c_routehistory_add.call(
        task_id='1', args=['phone_pd_id_3', order_id],
    )
    assert stq.routehistory_cargo_add.next_call()['kwargs']['order'] == {
        'created': matching.datetime_string,
        'user_id': 'some_user_id',
        'phone_id': 'phone_id',
        'order_id': order_id,
        'brand': 'yataxi',
        'yandex_uid': 'yandex_uid',
        'tariff_class': 'courier',
        'is_portal_uid': True,
        'route': [
            {
                'position': [1.0, 1.1],
                'full_text': 'Россия, Москва, Садовническая улица 82',
                'type': 'address',
                'entrance': '4',
                'uri': 'some uri',
                'phone_number': 'phone_pd_i',
                'personal_phone_id': 'phone_pd_id_1',
            },
            {
                'position': [2.0, 2.2],
                'full_text': 'Россия, Москва, Садовническая улица 82',
                'type': 'address',
                'entrance': '4',
                'uri': 'some uri',
                'phone_number': 'phone_pd_i',
                'personal_phone_id': 'phone_pd_id_1',
            },
            {
                'position': [3.0, 3.3],
                'full_text': 'Россия, Москва, Садовническая улица 82',
                'type': 'address',
                'entrance': '4',
                'uri': 'some uri',
                'phone_number': 'phone_pd_i',
                'personal_phone_id': 'phone_pd_id_1',
            },
            {
                'position': [4.0, 4.4],
                'full_text': 'Россия, Москва, Садовническая улица 82',
                'type': 'address',
                'entrance': '4',
                'uri': 'some uri',
                'phone_number': 'phone_pd_i',
                'personal_phone_id': 'phone_pd_id_1',
            },
            {
                'position': [5.0, 5.5],
                'full_text': 'Россия, Москва, Садовническая улица 82',
                'type': 'address',
                'entrance': '4',
                'uri': 'some uri',
                'phone_number': 'phone_pd_i',
                'personal_phone_id': 'phone_pd_id_2',
            },
        ],
    }
