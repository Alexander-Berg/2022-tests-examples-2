import json

import pytest

ORDER_ID = '123e4567-e89b-12d3-a456-426614174000'


@pytest.mark.parametrize('uid', ['user_id_1', None])
async def test_order_update_ok(taxi_tristero_b2b, mockserver, uid):
    customer_meta = {'key': 'value'}
    price = '1234.56'

    @mockserver.json_handler('/tristero-parcels/internal/v1/parcels/order')
    def _mock_parcels(request):
        body = request.json
        items = []
        for i in body['items']:
            item = {
                'barcode': i['barcode'],
                'measurements': i['measurements'],
                'state': 'created',
                'state_meta': {},
                'id': '123a4567-e89b-12d3-a456-42661417401{}'.format(
                    len(items),
                ),
            }
            if 'description' in i:
                item['description'] = i['description']
            items.append(item)
            assert body['customer_meta'] == customer_meta
        response = {
            'order_id': ORDER_ID,
            'ref_order': 'ref_order_1',
            'vendor': 'beru',
            'delivery_date': body['delivery_date'],
            'depot_id': 'depot_id_1',
            'state': 'reserved',
            'items': items,
            'token': 'some-token',
            'customer_meta': customer_meta,
            'price': price,
        }
        if uid is not None:
            response['uid'] = uid
        return response

    request = {
        'order_id': ORDER_ID,
        'delivery_date': '2020-09-09T23:00:00+00:00',
        'customer_meta': customer_meta,
        'items': [
            {
                'barcode': 'barcode_1',
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'weight': 1,
                    'length': 1,
                },
                'description': 'description_1',
            },
            {
                'barcode': 'barcode_2',
                'measurements': {
                    'width': 2,
                    'height': 2,
                    'weight': 2,
                    'length': 2,
                },
            },
        ],
        'price': price,
    }
    response = await taxi_tristero_b2b.put('/tristero/v1/order', json=request)
    assert response.status_code == 200
    assert len(response.json()['items']) == 2

    request['order_id'] = ORDER_ID
    request['vendor'] = 'beru'
    request['ref_order'] = 'ref_order_1'
    request['state'] = 'reserved'
    request['depot_id'] = 'depot_id_1'
    request['token'] = 'some-token'
    request.pop('items')
    request.pop('delivery_date')
    got_resp = response.json()
    got_resp.pop('items')
    assert got_resp == request


@pytest.mark.parametrize('partner_id', ['partner-id', None])
async def test_partner_id_is_forwarded_if_present(
        taxi_tristero_b2b, mockserver, partner_id,
):
    barcode = 'some-barcode'

    @mockserver.json_handler('/tristero-parcels/internal/v1/parcels/order')
    def _mock_parcels(request):
        body = request.json
        request_items = body['items']
        assert len(request_items) == 1
        request_item = request_items[0]

        if partner_id is not None:
            assert request_item['partner_id'] == partner_id
        else:
            assert 'partner_id' not in request_item

        response_item = {
            'barcode': request_item['barcode'],
            'measurements': request_item['measurements'],
            'state': 'created',
            'state_meta': {},
            'id': '123a4567-e89b-12d3-a456-42661417401{}'.format(
                len(request_items),
            ),
        }
        if 'description' in request_item:
            response_item['description'] = request_item['description']
        if 'partner_id' in request_item:
            response_item['partner_id'] = request_item['partner_id']

        response = {
            'order_id': ORDER_ID,
            'ref_order': 'ref_order_1',
            'vendor': 'beru',
            'delivery_date': body['delivery_date'],
            'depot_id': 'depot_id_1',
            'state': 'reserved',
            'items': [response_item],
            'token': 'some-token',
        }
        return response

    item = {
        'barcode': barcode,
        'measurements': {'width': 1, 'height': 1, 'weight': 1, 'length': 1},
        'description': 'description_1',
    }
    if partner_id is not None:
        item['partner_id'] = partner_id

    request = {
        'order_id': ORDER_ID,
        'delivery_date': '2020-09-09T23:00:00+00:00',
        'items': [item],
    }
    response = await taxi_tristero_b2b.put('/tristero/v1/order', json=request)
    assert response.status_code == 200
    assert len(response.json()['items']) == 1

    assert response.json()['items'][0]['barcode'] == barcode
    if partner_id is not None:
        assert response.json()['items'][0]['partner_id'] == partner_id
    else:
        assert 'partner_id' not in response.json()['items'][0]


@pytest.mark.parametrize('code', [404, 409, 400])
async def test_order_update_fail(taxi_tristero_b2b, mockserver, code):
    error_message = 'some client error'

    @mockserver.json_handler('/tristero-parcels/internal/v1/parcels/order')
    def _mock_parcels(request):
        return mockserver.make_response(
            json.dumps({'message': error_message}), status=code,
        )

    request = {
        'order_id': ORDER_ID,
        'delivery_date': '2020-09-09T23:00:00+00:00',
        'items': [
            {
                'barcode': 'barcode_1',
                'measurements': {
                    'width': 1,
                    'height': 1,
                    'weight': 1,
                    'length': 1,
                },
                'description': 'description_1',
            },
            {
                'barcode': 'barcode_2',
                'measurements': {
                    'width': 2,
                    'height': 2,
                    'weight': 2,
                    'length': 2,
                },
            },
        ],
    }
    response = await taxi_tristero_b2b.put(
        '/tristero/v1/order?vendor=beru&ref-order=ref_order_1', json=request,
    )
    assert response.status_code == code
    assert response.json()['message'] == error_message
