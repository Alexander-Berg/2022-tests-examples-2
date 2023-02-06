import datetime


def _get_order_created_date(i):
    return datetime.datetime(
        year=2020, month=3, day=i + 1, tzinfo=datetime.timezone.utc,
    ).isoformat()


async def test_order_log_flow(taxi_grocery_order_log):
    for i in range(10):
        previous_order_id = 'order_' + str(i - 2)
        order_id = 'order_' + str(i)
        if i % 2 == 0:
            yandex_uid = 'yandex_uid_1'
        else:
            yandex_uid = 'yandex_uid_2'
        request = {
            'order_id': order_id,
            'order_log_info': {
                'order_state': 'created',
                'yandex_uid': yandex_uid,
            },
        }
        response = await taxi_grocery_order_log.post(
            '/processing/v1/insert', json=request,
        )
        assert response.status_code == 200

        cursor_data = {'count': 10}
        retrieve_request_json = {
            'range': cursor_data,
            'user_identity': {
                'yandex_uid': '',
                'bound_yandex_uids': [yandex_uid, 'test-uid-1'],
            },
            'include_service_metadata': True,
        }
        response = await taxi_grocery_order_log.post(
            '/internal/orders/v1/retrieve',
            headers={
                'Accept-Language': 'ru',
                'X-Request-Application': 'app_brand=yataxi',
            },
            json=retrieve_request_json,
        )
        if int(i / 2) > 0:
            assert response.status_code == 200
            assert 'service_metadata' in response.json()
            service_metadata = response.json()['service_metadata']
            assert service_metadata['last_order_id'] == previous_order_id
            assert 'orders' in response.json()
            orders = response.json()['orders']
            assert len(orders) == int(i / 2)
        else:
            assert response.status_code == 200
            assert 'service_metadata' not in response.json()
            orders = response.json()['orders']
            assert not orders

        request = {
            'order_id': order_id,
            'order_log_info': {
                'order_state': 'closed',
                'yandex_uid': yandex_uid,
                'order_created_date': _get_order_created_date(i),
            },
        }
        response = await taxi_grocery_order_log.post(
            '/processing/v1/insert', json=request,
        )
        assert response.status_code == 200

        response = await taxi_grocery_order_log.post(
            '/internal/orders/v1/retrieve',
            headers={
                'Accept-Language': 'ru',
                'X-Request-Application': 'app_brand=yataxi',
            },
            json=retrieve_request_json,
        )
        assert response.status_code == 200
        assert 'service_metadata' in response.json()
        service_metadata = response.json()['service_metadata']
        assert service_metadata['last_order_id'] == order_id
        assert service_metadata[
            'last_order_created_at'
        ] == _get_order_created_date(i)

    cursor_data = {'count': 2, 'older_than': 'order_8'}
    retrieve_request_json = {
        'range': cursor_data,
        'user_identity': {
            'yandex_uid': 'yandex_uid_1',
            'bound_yandex_uids': ['test-uid-1'],
        },
        'include_service_metadata': False,
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve',
        headers={
            'Accept-Language': 'ru',
            'X-Request-Application': 'app_brand=yataxi',
        },
        json=retrieve_request_json,
    )
    assert response.status_code == 200
    assert 'service_metadata' not in response.json()
    orders = response.json()['orders']
    assert orders
    assert orders[0]['order_id'] == 'order_6'
    assert orders[1]['order_id'] == 'order_4'
