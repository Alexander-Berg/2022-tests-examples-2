import json


async def test_post_check_card(patch, web_app_client):
    @patch('taxi.stq.client.put')
    # pylint: disable=unused-variable
    async def put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    data = {
        'order_id': '123455',
        'region_id': 5,
        'success': True,
        'payment_id': 'odjfogdfg',
        'processing_index': 0,
        'antifraud_index': 1,
    }
    response = await web_app_client.post(
        '/event/update_transactions/check_card', data=json.dumps(data),
    )

    assert response.status == 200

    response_json = await response.json()
    event_id = response_json['id']

    response = await web_app_client.post(
        '/event', data=json.dumps({'event_id': event_id}),
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == {'id': event_id, 'status': 'pending'}


async def test_order_created_cash(patch, web_app_client):
    @patch('taxi.stq.client.put')
    # pylint: disable=unused-variable
    async def put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    data = {
        'user_uid': '445325700',
        'order_id': 'e9200a728aa8133f8814a9cbdaf5090a',
        'last_known_ip': '::ffff:94.100.229.237',
        'processing_index': 0,
        'source': None,
        'payment_type': 'cash',
        'user_phone_id': '598b753489216ea4eeb741c0',
        'nearest_zone': 'tbilisi',
        'payment_method_id': None,
        'destination_types': [],
        'client_application': 'yango_android',
        'client_version': '5.5.5',
        'source_type': 'other',
    }

    response = await web_app_client.post(
        '/event/processing/order_created', data=json.dumps(data),
    )

    assert response.status == 200


async def test_transporting_event(patch, web_app_client):
    @patch('taxi.stq.client.put')
    # pylint: disable=unused-variable
    async def put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    data = {
        'order_id': 'e9200a728aa8133f8814a9cbdaf5090a',
        'processing_index': 0,
        'tariff_class': 'econom',
        'transporting_time': '2019-04-18T16:04:56.845082+03:00',
        'fixed_price': True,
        'category_id': 'e9200a728aa8133f8814a9cbdaf5090a',
        'alias_id': 'e9200a728aa8133f8814a9cbdaf5090a',
        'db_id': 'e9200a728aa8133f8814a9cbdaf5090a',
        'surge': {'surge': 1.0, 'alpha': 2, 'beta': 2.2, 'surcharge': 1.0},
        'coupon': {'value': 2, 'percent': 10, 'limit': 500},
        'discount_multiplier': 1.5,
    }

    response = await web_app_client.post(
        '/event/processing/driver_transporting', data=json.dumps(data),
    )

    assert response.status == 200


async def test_order_finished(patch, web_app_client):
    @patch('taxi.stq.client.put')
    # pylint: disable=unused-variable
    async def put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    data = {
        'order_id': 'e9200a728aa8133f8814a9cbdaf5090a',
        'processing_index': -1,
    }

    response = await web_app_client.post(
        '/event/processing/order_finished', data=json.dumps(data),
    )

    assert response.status == 200
