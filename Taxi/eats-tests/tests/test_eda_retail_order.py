import time


def test_get_pickers_list(core):
    core.set_host('https://eda.yandex')

    response = core.get_pickers_list()
    assert response.status_code == 200
    assert response.json() == {
        'meta': {'count': 2},
        'payload': {
            'pickers': [
                {
                    'available_places': [1],
                    'available_until': '2100-01-01T00:00:00+0300',
                    'id': 1,
                    'name': 'test',
                    'phone_id': '68696aae79e7486cb389503778ddf1a0',
                    'requisite_type': 'TinkoffBank',
                    'requisite_value': '3456789',
                },
                {
                    'available_places': [2],
                    'available_until': '2100-01-01T00:00:00+0300',
                    'id': 3,
                    'name': 'test2',
                    'phone_id': '68696aae79e7486cb389503778ddf1a0',
                    'requisite_type': 'TinkoffBank',
                    'requisite_value': '3456789009',
                },
            ],
        },
    }


def test_create_order_and_cancel(picker):
    picker.set_host('http://eats-picker-orders.eda.yandex.net')

    order_nr, response = picker.create_order(
        place_id=305694, flow_type='picking_packing',
    )
    assert response.status_code == 200
    assert response.json()['result'] == 'OK'

    picker_id = '2'
    assign = picker.put_courier(order_nr=order_nr, picker_id=picker_id)
    assert assign.status_code == 204

    cancel_order = picker.cancel_order(order_nr)
    assert cancel_order.status_code == 204


def test_create_order_and_dispatch(picker, supply):
    picker.set_host('http://eats-picker-orders.eda.yandex.net')
    supply.set_host('http://eats-picker-supply.eda.yandex.net')

    place_id: int = 1
    picker_id: int = 1
    response = supply.select_picker(place_id=place_id)
    assert response.status_code == 200
    assert response.json()['picker_id'] == str(picker_id)

    response = supply.change_priority(picker_id=str(picker_id), add=100)
    assert response.status_code == 200

    order_nr = picker.random_order_nrs()
    _, response = picker.create_order(
        order_nr=order_nr, place_id=1, flow_type='picking_packing',
    )
    assert response.status_code == 200
    assert response.json()['result'] == 'OK'

    picker.put_courier(order_nr, picker_id=str(picker_id))

    response = get_orders(picker, str(picker_id))
    order = response.json()['orders'][0]
    assert order['flow_type'] == 'picking_packing'


def get_orders(picker, picker_id):
    response = None
    for _ in range(60):
        response = picker.external_get_orders(picker_id=str(picker_id))
        assert response.status_code == 200
        if len(response.json()['orders']) >= 1:
            return response
        time.sleep(1)
    assert len(response.json()['orders']) >= 1, response.json()
    return response
