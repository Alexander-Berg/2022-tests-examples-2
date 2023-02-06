import asyncio
import copy
import datetime
import json

import pytest

from . import utils


# pylint: disable=too-many-lines


@utils.polling_delay_config()
async def test_order_get_by_id_wrong_input_400(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order', json={'foo': 'bar'},
    )
    assert response.status == 400
    assert 'X-Polling-Delay' not in response.headers


@utils.polling_delay_config()
@pytest.mark.parametrize(
    ['eats_id', 'picker_id'], [['12345', '1'], ['123', '124']],
)
async def test_order_not_found_404(
        taxi_eats_picker_orders, create_order, eats_id, picker_id,
):
    create_order(eats_id='123', picker_id='1')
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 404
    assert response.headers['X-Polling-Delay'] == '60'


@utils.polling_delay_config()
async def test_order_get_by_id_200(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        load_json,
):
    order_id = create_order(
        eats_id='123',
        picker_id='1',
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        spent=None,
    )

    fst_order_item_id = create_order_item(
        order_id=order_id,
        quantity=1.5,
        measure_value=200,
        sold_by_weight=True,
        images=('https://example.org/product1/orig',),
        show_vendor_code=True,
        measure_quantum=150,
        relative_quantum=0.5,
    )
    create_picked_item(
        order_item_id=fst_order_item_id, picker_id='1', weight=150,
    )

    snd_order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='eats-124',
        category_id='13',
        category_name='Bread',
        top_level_categories=[
            ('13', 'Bred', None, None, None),
            ('13.1', 'Moldy Bred', None, None, None),
        ],
        barcode_weight_algorithm=None,
        quantity=5,
        measure_max_overweight=None,
        price=20,
        images=('https://example.org/product1/xxx.jpeg',),
        measure_quantum=0.75,
    )
    create_picked_item(order_item_id=snd_order_item_id, picker_id='1', count=3)

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': '123'},
        headers=utils.da_headers('1'),
    )
    assert response.status == 200
    assert response.headers['X-Polling-Delay'] == '60'

    expected_response = load_json('order_expected_response.json')
    expected_response['payload']['id'] = str(order_id)
    response_data = response.json()
    assert response_data['payload']['is_asap']
    del response_data['payload']['is_asap']
    assert response_data['payload']['status_updated_at']
    del response_data['payload']['status_updated_at']
    assert response_data['payload']['created_at']
    del response_data['payload']['created_at']
    assert response_data['payload']['updated_at']
    del response_data['payload']['updated_at']
    assert response_data['payload']['customer_phone']
    del response_data['payload']['customer_phone']
    assert response_data['payload']['payment_limit']
    del response_data['payload']['payment_limit']
    assert response_data['payload']['payment_limit_coefficient']
    del response_data['payload']['payment_limit_coefficient']
    assert response_data['payload']['held_payment_limit']
    del response_data['payload']['held_payment_limit']
    assert response_data['payload']['customer_picker_phone_forwarding']
    del response_data['payload']['customer_picker_phone_forwarding']
    assert expected_response == response_data


@utils.polling_delay_config()
@pytest.mark.parametrize('communication_policy', utils.COMMUNICATION_POLICIES)
@pytest.mark.parametrize(
    'not_found_item_policy', utils.NOT_FOUND_ITEM_POLICIES,
)
async def test_order_get_by_id_with_picking_policy_200(
        taxi_eats_picker_orders,
        create_order,
        create_order_picking_policy,
        communication_policy,
        not_found_item_policy,
):
    eats_id = '123'
    picker_id = '1'
    create_order_picking_policy(
        eats_id=eats_id,
        communication_policy=communication_policy,
        not_found_item_policy=not_found_item_policy,
    )
    create_order(eats_id=eats_id, picker_id=picker_id, state='picking')

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200

    response_data = response.json()
    assert (
        response_data['payload']['communication_policy']
        == communication_policy
    )
    assert (
        response_data['payload']['not_found_item_policy']
        == not_found_item_policy
    )


async def test_order_get_by_id_without_picked_items_200(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        load_json,
):
    order_id = create_order(
        eats_id='123',
        picker_id='1',
        state='picking',
        payment_value=10,
        require_approval=True,
        spent=None,
    )
    create_order_item(
        order_id=order_id,
        quantity=1.5,
        measure_value=200,
        sold_by_weight=True,
        show_vendor_code=False,
        measure_quantum=150,
    )

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': '123'},
        headers=utils.da_headers('1'),
    )
    assert response.status == 200
    expected_response = load_json(
        'order_without_picked_items_expected_response.json',
    )

    expected_response['payload']['require_approval'] = True
    expected_response['payload']['id'] = str(order_id)
    response_data = response.json()
    assert response_data['payload']['is_asap']
    del response_data['payload']['is_asap']
    assert response_data['payload']['status_updated_at']
    del response_data['payload']['status_updated_at']
    assert response_data['payload']['created_at']
    del response_data['payload']['created_at']
    assert response_data['payload']['updated_at']
    del response_data['payload']['updated_at']
    assert response_data['payload']['customer_phone']
    del response_data['payload']['customer_phone']
    assert response_data['payload']['payment_limit']
    del response_data['payload']['payment_limit']
    assert response_data['payload']['payment_limit_coefficient']
    del response_data['payload']['payment_limit_coefficient']
    assert response_data['payload']['held_payment_limit']
    del response_data['payload']['held_payment_limit']
    assert response_data['payload']['customer_picker_phone_forwarding']
    del response_data['payload']['customer_picker_phone_forwarding']
    assert expected_response == response_data


@pytest.mark.parametrize(
    'handle, request_picker_id',
    [['/4.0/eats-picker/api/v1/order', '1'], ['/api/v1/order', None]],
)
@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type, soft_deleted',
    [
        [None, None, False],
        ['unknown_picker', None, False],
        ['unknown_picker', 'picker', False],
        ['1', 'picker', True],
        ['1', None, True],
        ['system', 'system', True],
        ['system', None, True],
        ['customer_id', 'customer', True],
    ],
)
async def test_order_get_by_id_soft_delete_200(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        load_json,
        handle,
        request_picker_id,
        is_deleted_by,
        deleted_by_type,
        soft_deleted,
):
    order_id = create_order(
        eats_id='123',
        picker_id='1',
        state='picking',
        payment_value=10,
        require_approval=True,
        spent=None,
    )
    create_order_item(
        order_id=order_id,
        quantity=1.5,
        measure_value=200,
        sold_by_weight=True,
        show_vendor_code=False,
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
        measure_quantum=150,
    )

    response = await taxi_eats_picker_orders.get(
        handle,
        params={'eats_id': '123'},
        headers=utils.make_headers(request_picker_id),
    )
    assert response.status == 200
    expected_response = load_json(
        'order_without_picked_items_expected_response.json',
    )

    expected_response['payload']['require_approval'] = True
    expected_response['payload']['id'] = str(order_id)
    expected_response['payload']['picker_items'][0][
        'soft_deleted'
    ] = soft_deleted
    if not request_picker_id:
        del expected_response['payload']['picker_assignation_count']
    response_data = response.json()
    assert response_data['payload']['is_asap']
    del response_data['payload']['is_asap']
    assert response_data['payload']['status_updated_at']
    del response_data['payload']['status_updated_at']
    assert response_data['payload']['created_at']
    del response_data['payload']['created_at']
    assert response_data['payload']['updated_at']
    del response_data['payload']['updated_at']
    assert response_data['payload']['customer_phone']
    del response_data['payload']['customer_phone']
    assert response_data['payload']['customer_picker_phone_forwarding']
    del response_data['payload']['customer_picker_phone_forwarding']
    assert response_data['payload']['payment_limit']
    del response_data['payload']['payment_limit']
    assert response_data['payload']['payment_limit_coefficient']
    del response_data['payload']['payment_limit_coefficient']
    assert response_data['payload']['held_payment_limit']
    del response_data['payload']['held_payment_limit']
    assert expected_response == response_data


async def test_calc_total_weight_and_pickedup_total(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
):
    order_id = create_order(
        eats_id='123', last_version=1, picker_id='1', spent=10,
    )
    item_id_for_delete = create_order_item(
        order_id=order_id,
        eats_item_id='delete',
        quantity=5,
        sold_by_weight=False,
    )
    create_picked_item(
        order_item_id=item_id_for_delete, picker_id='1', count=3,
    )
    fst_order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='1234',
        measure_value=200,
        sold_by_weight=True,
    )
    create_picked_item(
        order_item_id=fst_order_item_id, picker_id='1', weight=100,
    )
    snd_order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='1235',
        version=1,
        measure_value=400,
        sold_by_weight=True,
    )
    create_picked_item(
        order_item_id=snd_order_item_id,
        cart_version=0,
        picker_id='1',
        weight=300,
    )
    create_picked_item(
        order_item_id=snd_order_item_id,
        cart_version=1,
        picker_id='2',
        weight=400,
    )

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': '123'},
        headers=utils.da_headers('1'),
    )
    assert response.status == 200

    payload = response.json()['payload']
    assert payload['pickedup_total'] == '7.50'
    assert payload['total_weight'] == 300
    assert payload['spent'] == '10.00'
    assert len(payload['picker_items']) == 1


async def test_internal_calc_total_weight_and_pickedup_total(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
):
    order_id = create_order(eats_id='123', last_version=1, picker_id='1')
    item_id_for_delete = create_order_item(
        order_id=order_id,
        eats_item_id='delete',
        quantity=5,
        sold_by_weight=False,
    )
    create_picked_item(
        order_item_id=item_id_for_delete, picker_id='1', count=3,
    )
    fst_order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='1234',
        measure_value=200,
        sold_by_weight=True,
    )
    create_picked_item(
        order_item_id=fst_order_item_id, picker_id='1', weight=100,
    )
    snd_order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='1235',
        version=1,
        measure_value=400,
        sold_by_weight=True,
    )
    create_picked_item(
        order_item_id=snd_order_item_id,
        cart_version=0,
        picker_id='1',
        weight=300,
    )
    create_picked_item(
        order_item_id=snd_order_item_id,
        cart_version=1,
        picker_id='2',
        weight=400,
    )

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': '123'},
        headers=utils.da_headers('1'),
    )
    assert response.status == 200

    response_data = response.json()
    assert response_data['payload']['picker_assignation_count'] == 1
    del response_data['payload']['picker_assignation_count']

    response2 = await taxi_eats_picker_orders.get(
        '/api/v1/order', params={'eats_id': '123'},
    )

    assert response2.status == 200

    response2_data = response2.json()

    assert response2_data == response_data


async def test_internal_order_get_by_id_200(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        load_json,
):
    order_id = create_order(
        eats_id='123',
        picker_id='1',
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        spent=None,
    )

    fst_order_item_id = create_order_item(
        order_id=order_id,
        quantity=1.5,
        measure_value=200,
        sold_by_weight=True,
        images=('https://example.org/product1/orig',),
        show_vendor_code=True,
        measure_quantum=150,
        relative_quantum=0.5,
    )
    create_picked_item(
        order_item_id=fst_order_item_id, picker_id='1', weight=150,
    )

    snd_order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='eats-124',
        category_id='13',
        category_name='Bread',
        top_level_categories=[
            ('13', 'Bred', None, None, None),
            ('13.1', 'Moldy Bred', None, None, None),
        ],
        barcode_weight_algorithm=None,
        quantity=5,
        measure_max_overweight=None,
        price=20,
        images=('https://example.org/product1/xxx.jpeg',),
        measure_quantum=0.75,
    )
    create_picked_item(order_item_id=snd_order_item_id, picker_id='1', count=3)

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': '123'},
        headers=utils.da_headers('1'),
    )
    assert response.status == 200

    expected_response = load_json('order_expected_response.json')
    expected_response['payload']['id'] = str(order_id)
    response_data = response.json()
    assert response_data['payload']['is_asap']
    del response_data['payload']['is_asap']
    assert response_data['payload']['status_updated_at']
    del response_data['payload']['status_updated_at']
    assert response_data['payload']['created_at']
    del response_data['payload']['created_at']
    assert response_data['payload']['updated_at']
    del response_data['payload']['updated_at']
    assert response_data['payload']['customer_phone']
    del response_data['payload']['customer_phone']
    assert response_data['payload']['customer_picker_phone_forwarding']
    del response_data['payload']['customer_picker_phone_forwarding']
    assert response_data['payload']['payment_limit']
    del response_data['payload']['payment_limit']
    assert response_data['payload']['payment_limit_coefficient']
    del response_data['payload']['payment_limit_coefficient']
    assert response_data['payload']['held_payment_limit']
    del response_data['payload']['held_payment_limit']
    assert expected_response == response_data

    response2 = await taxi_eats_picker_orders.get(
        '/api/v1/order', params={'eats_id': '123'},
    )

    assert response2.status == 200

    response_data = response.json()
    response2_data = response2.json()

    del response_data['payload']['picker_assignation_count']

    assert response2_data == response_data


@pytest.mark.parametrize(
    'url', ['/4.0/eats-picker/api/v1/order', '/api/v1/order'],
)
async def test_no_phone_id_no_phone(
        taxi_eats_picker_orders, create_order, url,
):
    create_order(
        eats_id='123',
        picker_id='1',
        picker_phone_id=None,
        courier_id='2',
        courier_phone_id=None,
        customer_phone_id=None,
    )

    response = await taxi_eats_picker_orders.get(
        url, params={'eats_id': '123'}, headers=utils.da_headers('1'),
    )
    assert response.status == 200

    payload = response.json()['payload']
    assert 'forwarded_picker_phone' not in payload
    assert 'forwarded_courier_phone' not in payload
    assert 'customer_phone' not in payload


@pytest.mark.parametrize(
    'url', ['/4.0/eats-picker/api/v1/order', '/api/v1/order'],
)
@pytest.mark.now('2020-10-20T17:50:00+0000')
async def test_actual_phone(taxi_eats_picker_orders, create_order, url):
    create_order(
        eats_id='123',
        picker_id='1',
        picker_phone_id='picker_phone_id',
        picker_phone=('+7-call-me-picker', '2020-10-21T17:50:00+0000'),
        courier_id='2',
        courier_phone_id='courier_phone_id',
        courier_phone=('+7-call-me-courier', '2020-10-21T17:50:00+0000'),
        customer_phone_id='customer_phone_id',
        customer_forwarded_phone=(
            '+7-call-me-customer',
            '2020-10-21T17:50:00+0000',
        ),
        customer_picker_phone_forwarding=(
            '+7-call-me-customer (from picker)',
            '2020-10-21T17:50:00+0000',
        ),
    )

    response = await taxi_eats_picker_orders.get(
        url, params={'eats_id': '123'}, headers=utils.da_headers('1'),
    )
    assert response.status == 200

    payload = response.json()['payload']
    assert payload['forwarded_picker_phone'] == '+7-call-me-picker'
    assert payload['forwarded_courier_phone'] == '+7-call-me-courier'
    assert payload['customer_phone'] == '+7-call-me-customer'
    assert payload['customer_picker_phone_forwarding'] == {
        'expires_at': '2020-10-21T17:50:00+00:00',
        'phone': '+7-call-me-customer (from picker)',
    }


@pytest.fixture(name='eats_core')
def _eats_core(mockserver):
    @mockserver.json_handler('/eats-core/v1/supply/performer-location')
    def _list_by_ids_handler(request):
        known_positions = {
            '1': {
                'longitude': 43.412297,
                'latitude': 39.965948,
                'is_precise': True,
            },
            '2': {
                'longitude': 43.401854,
                'latitude': 39.971893,
                'is_precise': True,
            },
        }

        params = {
            p.split('=')[0]: p.split('=')[1]
            for p in request.query_string.decode().split('&')
        }
        courier_id = params.get('performer_id')
        assert courier_id

        position = known_positions.get(courier_id)
        if position:
            return {'performer_position': position}
        return mockserver.make_response(
            json.dumps(
                {
                    'isSuccess': False,
                    'statusCode': 404,
                    'type': f'Position not found for courier {courier_id}',
                },
            ),
            404,
        )


@pytest.fixture(name='vgw_api')
def _vgw_api(mockserver, mocked_time):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _forwardings_handler(request):
        known_conversions = {
            'phone_1': {'phone': '+7-call-me-baby', 'ext': '1111'},
            'phone_2': {'phone': '+1-ghost-busters', 'ext': '2222'},
            'phone_3': {'phone': '+0-dont-disturb', 'ext': '3333'},
        }
        assert request.method == 'POST'
        if len(request.json.get('call_location', [])) != 2:
            return mockserver.make_response(
                json.dumps(
                    {
                        'code': 'PartnerUnableToHandle',
                        'error': {
                            'code': 'PartnerUnableToHandle',
                            'message': (
                                'call_location is invalid in the request'
                            ),
                        },
                    },
                ),
                400,
            )
        phone_id = request.json.get('callee_phone_id')
        assert phone_id

        if known_conversions.get(phone_id):
            response = copy.deepcopy(known_conversions[phone_id])
            response['expires_at'] = (
                mocked_time.now()
                + datetime.timedelta(seconds=request.json['new_ttl'])
            ).strftime('%Y-%m-%dT%H:%M:%S+0000')
            return response
        return mockserver.make_response(
            json.dumps(
                {
                    'code': 'PartnerResponsedNotFound',
                    'error': {
                        'code': 'PartnerResponsedNotFound',
                        'message': f'No forwarding found for id {phone_id}',
                    },
                },
            ),
            400,
        )

    return _forwardings_handler


@pytest.mark.parametrize(
    'url', ['/4.0/eats-picker/api/v1/order', '/api/v1/order'],
)
@pytest.mark.now('2020-10-20T17:50:00+0000')
@utils.send_order_events_config()
async def test_create_new_phone(
        taxi_eats_picker_orders,
        create_order,
        url,
        vgw_api,
        mock_processing,
        get_order,
        eats_core,
):
    order_id = create_order(
        eats_id='123',
        picker_id='1',
        picker_phone_id='phone_1',
        picker_phone=None,
        courier_id='2',
        courier_phone_id='phone_2',
        courier_phone=None,
        customer_phone_id='phone_3',
        customer_forwarded_phone=None,
        customer_picker_phone_forwarding=None,
    )

    response = await taxi_eats_picker_orders.get(
        url, params={'eats_id': '123'}, headers=utils.da_headers('1'),
    )
    assert response.status == 200

    payload = response.json()['payload']
    assert payload['forwarded_picker_phone'] == '+7-call-me-baby,,1111'
    assert payload['forwarded_courier_phone'] == '+1-ghost-busters,,2222'
    assert payload['customer_phone'] == '+0-dont-disturb,,3333'
    assert payload['customer_picker_phone_forwarding'] == {
        'expires_at': '2020-10-20T20:50:00+00:00',
        'phone': '+7-call-me-baby,,1111',
    }

    order = get_order(order_id)
    assert order['picker_phone']
    assert order['courier_phone']
    assert order['customer_forwarded_phone']
    assert order['customer_picker_phone_forwarding']
    assert vgw_api.times_called == 4
    assert mock_processing.times_called == 1


@pytest.mark.now('2020-10-20T17:50:00+0000')
async def test_create_new_customer_phone_no_picker_id(
        taxi_eats_picker_orders, create_order, vgw_api, get_order,
):
    order_id = create_order(
        eats_id='123',
        picker_id=None,
        picker_phone_id=None,
        picker_phone=None,
        customer_phone_id='phone_3',
        customer_forwarded_phone=None,
        customer_picker_phone_forwarding=None,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order', params={'eats_id': '123'},
    )
    assert response.status == 200

    payload = response.json()['payload']
    assert payload['customer_phone'] == '+7123456789'

    order = get_order(order_id)
    assert order['customer_forwarded_phone'] is None
    assert order['customer_picker_phone_forwarding'] is None


@pytest.mark.parametrize(
    'url', ['/4.0/eats-picker/api/v1/order', '/api/v1/order'],
)
@pytest.mark.now('2020-10-20T17:50:00+0000')
async def test_create_new_phone_when_expired(
        taxi_eats_picker_orders, create_order, url, vgw_api, eats_core,
):
    create_order(
        eats_id='123',
        picker_id='1',
        picker_phone_id='phone_1',
        picker_phone=('+7-999-888-77-66', '2020-10-20T17:45:00+0000'),
        courier_id='2',
        courier_phone_id='phone_2',
        courier_phone=('+7-555-444-33-22', '2020-10-20T17:45:00+0000'),
        customer_phone_id='phone_3',
        customer_forwarded_phone=(
            '+7-800-555-35-35',
            '2020-10-20T17:45:00+0000',
        ),
        customer_picker_phone_forwarding=(
            '+7-800-555-35-35',
            '2020-10-20T17:45:00+0000',
        ),
    )

    response = await taxi_eats_picker_orders.get(
        url, params={'eats_id': '123'}, headers=utils.da_headers('1'),
    )
    assert response.status == 200

    payload = response.json()['payload']
    assert payload['forwarded_picker_phone'] == '+7-call-me-baby,,1111'
    assert payload['forwarded_courier_phone'] == '+1-ghost-busters,,2222'
    assert payload['customer_phone'] == '+0-dont-disturb,,3333'
    assert payload['customer_picker_phone_forwarding'] == {
        'expires_at': '2020-10-20T20:50:00+00:00',
        'phone': '+7-call-me-baby,,1111',
    }


@pytest.mark.parametrize(
    'url', ['/4.0/eats-picker/api/v1/order', '/api/v1/order'],
)
@pytest.mark.parametrize('customer_phone_id', ['+7123456789', None])
@pytest.mark.now('2020-10-20T17:50:00+0000')
async def test_no_phone_in_case_vgw_api_fails(
        taxi_eats_picker_orders,
        create_order,
        url,
        customer_phone_id,
        vgw_api,
        eats_core,
):
    create_order(
        eats_id='123',
        picker_id='1',
        picker_phone_id='unknown_phone_id_1',
        picker_phone=None,
        courier_id='1',
        courier_phone_id='unknown_phone_id_2',
        courier_phone=None,
        customer_phone_id=customer_phone_id,
        customer_forwarded_phone=None,
        customer_picker_phone_forwarding=None,
    )

    response = await taxi_eats_picker_orders.get(
        url, params={'eats_id': '123'}, headers=utils.da_headers('1'),
    )
    assert response.status == 200

    payload = response.json()['payload']
    assert 'forwarded_picker_phone' not in payload
    assert 'forwarded_courier_phone' not in payload
    assert 'customer_picker_phone_forwarding' not in payload
    if customer_phone_id:
        assert payload['customer_phone'] == '+7123456789'
    else:
        assert 'customer_phone' not in payload


@pytest.mark.parametrize(
    'url', ['/4.0/eats-picker/api/v1/order', '/api/v1/order'],
)
@pytest.mark.now('2020-10-20T17:50:00+0000')
async def test_no_phone_if_fail_to_find_picker_location(
        taxi_eats_picker_orders, create_order, url, vgw_api, eats_core,
):
    create_order(
        eats_id='123',
        picker_id='10',
        picker_phone_id='phone_1',
        picker_phone=None,
        courier_id='20',
        courier_phone_id='phone_2',
        courier_phone=None,
        customer_phone_id='phone_3',
        customer_picker_phone_forwarding=None,
    )

    response = await taxi_eats_picker_orders.get(
        url, params={'eats_id': '123'}, headers=utils.da_headers('10'),
    )
    assert response.status == 200

    payload = response.json()['payload']
    assert 'forwarded_picker_phone' not in payload
    assert 'forwarded_courier_phone' not in payload
    assert 'customer_picker_phone_forwarding' not in payload


@pytest.mark.parametrize(
    'url', ['/4.0/eats-picker/api/v1/order', '/api/v1/order'],
)
@pytest.mark.now('2020-10-20T17:50:00+0000')
async def test_concurrent_create_new_number(
        taxi_eats_picker_orders, create_order, url, eats_core, mockserver,
):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _forwardings_handler(request):
        return {
            'phone': request.json['nonce'],
            'ext': '',
            'expires_at': '2020-10-20T20:50:00+0000',
        }

    create_order(
        eats_id='123',
        picker_id='1',
        picker_phone_id='phone_1',
        picker_phone=None,
    )

    tasks = [
        asyncio.create_task(
            taxi_eats_picker_orders.get(
                url, params={'eats_id': '123'}, headers=utils.da_headers('1'),
            ),
        )
        for _ in range(5)
    ]
    responses = [await t for t in tasks]

    assert all(r.status == 200 for r in responses)

    def get_phone(response):
        return response.json()['payload']['forwarded_picker_phone']

    assert len(set(get_phone(r) for r in responses)) == 1


@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/order', '/api/v1/order'],
)
@pytest.mark.parametrize(
    'author, author_type',
    [
        ['someone', None],
        ['customer', 'customer'],
        [None, 'system'],
        ['1122', 'system'],
        ['1122', 'picker'],
        ['another_picker', 'system'],
        ['another_picker', 'picker'],
    ],
)
async def test_get_order_by_version(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        load_json,
        handle,
        author,
        author_type,
):
    eats_id = '123'
    picker_id = '1'
    order_id = create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='picking',
        payment_value=110,
        payment_limit=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        last_version=2,
        spent=None,
    )

    fst_order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='eats-item-1',
        version=0,
        quantity=1,
        measure_value=200,
        measure_quantum=150,
    )
    create_picked_item(
        order_item_id=fst_order_item_id,
        picker_id=picker_id,
        count=1,
        cart_version=0,
    )
    snd_order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='eats-item-2',
        version=1,
        quantity=2,
        measure_value=250,
        show_vendor_code=True,
        measure_quantum=187.5,
        author=author,
        author_type=author_type,
    )
    create_picked_item(
        order_item_id=snd_order_item_id,
        picker_id=picker_id,
        count=1,
        cart_version=1,
    )
    create_picked_item(
        order_item_id=snd_order_item_id,
        picker_id=picker_id,
        count=2,
        cart_version=2,
    )
    trd_order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='eats-item-3',
        version=2,
        quantity=3,
        measure_value=300,
        show_vendor_code=False,
        measure_quantum=225,
    )
    create_picked_item(
        order_item_id=trd_order_item_id,
        picker_id=picker_id,
        count=3,
        cart_version=3,
    )

    response = await taxi_eats_picker_orders.get(
        handle,
        params={'eats_id': eats_id, 'version': 1},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200

    expected_response = load_json('order_by_version_expected_response.json')
    expected_response['payload']['id'] = str(order_id)
    response_data = response.json()
    assert response_data['payload']['is_asap']
    del response_data['payload']['is_asap']
    assert response_data['payload']['status_updated_at']
    del response_data['payload']['status_updated_at']
    assert response_data['payload']['created_at']
    del response_data['payload']['created_at']
    assert response_data['payload']['updated_at']
    del response_data['payload']['updated_at']
    assert response_data['payload']['customer_phone']
    del response_data['payload']['customer_phone']
    assert response_data['payload']['customer_picker_phone_forwarding']
    del response_data['payload']['customer_picker_phone_forwarding']
    assert abs(float(response_data['payload']['payment_limit']) - 110) < 1e-6
    del response_data['payload']['payment_limit']
    assert (
        abs(float(response_data['payload']['held_payment_limit']) - 30) < 1e-6
    )
    assert 'payment_limit_coefficient' in response_data['payload']
    del response_data['payload']['payment_limit_coefficient']
    del response_data['payload']['held_payment_limit']
    if not handle.startswith('/4.0'):
        del expected_response['payload']['picker_assignation_count']
    assert expected_response == response_data


@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/order', '/api/v1/order'],
)
@pytest.mark.parametrize(
    'author, author_type, expected_version',
    [
        ['someone', None, 1],
        ['customer', 'customer', 1],
        [None, 'system', 1],
        ['1', 'system', 1],
        ['1', 'picker', 1],
        ['another_picker', 'system', 0],
        ['another_picker', 'picker', 0],
    ],
)
async def test_get_order_version_author(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        handle,
        author,
        author_type,
        expected_version,
):
    eats_id = '123'
    picker_id = '1'
    order_id = create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        last_version=2,
    )

    create_order_item(order_id=order_id, eats_item_id='0', version=0)
    create_order_item(
        order_id=order_id,
        eats_item_id='1',
        version=1,
        author=author,
        author_type=author_type,
    )

    response = await taxi_eats_picker_orders.get(
        handle,
        params={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200

    response_data = response.json()
    assert response_data['payload']['version'] == expected_version
    picker_items = response_data['payload']['picker_items']
    assert len(picker_items) == 1
    assert picker_items[0]['id'] == str(expected_version)


@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/order', '/api/v1/order'],
)
@pytest.mark.parametrize('customer_name', ['Vasya', None])
async def test_get_order_no_customer_name(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        handle,
        customer_name,
        mockserver,
):
    eats_id = '123'
    picker_id = '1'
    customer_phone = '+79054831698'
    customer_phone_id = 'phone_id'
    create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        customer_phone_id=customer_phone_id,
        customer_name=customer_name,
    )

    @mockserver.json_handler(f'/personal/v1/phones/bulk_retrieve')
    def _mock_personal_phones(request):
        assert request.method == 'POST'
        assert request.json['items']
        result = []
        result.append({'id': customer_phone_id, 'value': customer_phone})
        return mockserver.make_response(status=200, json={'items': result})

    response = await taxi_eats_picker_orders.get(
        handle,
        params={'eats_id': eats_id, 'version': 1},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200

    response_data = response.json()
    if customer_name:
        assert response_data['payload']['customer']['name'] == customer_name
    else:
        assert 'name' not in response_data['payload']['customer']
    assert response_data['payload']['customer']['phone'] == customer_phone


async def test_picker_assigned_count(
        taxi_eats_picker_orders, create_order, create_order_status,
):
    picker_id_1 = '1'
    picker_id_2 = '2'
    eats_id_1 = '123'
    eats_id_2 = '1234'
    order_id1 = create_order(
        eats_id=eats_id_1,
        picker_id=picker_id_1,
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )
    order_id2 = create_order(
        eats_id=eats_id_2,
        picker_id=picker_id_2,
        state='new',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )
    create_order_status(
        order_id=order_id2,
        last_version=0,
        state='assigned',
        author_id=picker_id_2,
    )
    create_order_status(
        order_id=order_id2,
        last_version=0,
        state='assigned',
        author_id=picker_id_1,
    )
    create_order_status(
        order_id=order_id2,
        last_version=0,
        state='assigned',
        author_id=picker_id_2,
    )

    create_order_status(
        order_id=order_id1,
        last_version=0,
        state='assigned',
        author_id=picker_id_1,
    )
    create_order_status(
        order_id=order_id1,
        last_version=0,
        state='picking',
        author_id=picker_id_1,
    )
    create_order_status(
        order_id=order_id1,
        last_version=0,
        state='assigned',
        author_id=picker_id_1,
    )
    create_order_status(
        order_id=order_id1,
        last_version=0,
        state='assigned',
        author_id=picker_id_2,
    )
    create_order_status(
        order_id=order_id1,
        last_version=0,
        state='assigned',
        author_id=picker_id_1,
    )
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': eats_id_1},
        headers=utils.da_headers(picker_id_1),
    )
    assert response.status == 200
    assert response.json()['payload']['picker_assignation_count'] == 3

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': eats_id_2},
        headers=utils.da_headers(picker_id_2),
    )
    assert response.status == 200
    assert response.json()['payload']['picker_assignation_count'] == 2


@pytest.mark.parametrize(
    'measure_version, pickedup_total',
    [[None, '78.75'], ['1', '78.75'], ['2', '52.50']],
)
@utils.polling_delay_config()
async def test_get_order_with_quantum_fields(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        create_picked_item,
        load_json,
        measure_version,
        pickedup_total,
):
    order_id = create_order(
        eats_id='123',
        picker_id='1',
        state='picking',
        payment_value=110,
        payment_limit=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
        spent=None,
    )

    # новые поля не соответствуют старым, чтобы можно было увидеть разный
    # результат вычислений
    fst_order_item_id = create_order_item(
        order_id=order_id,
        quantity=1.5,
        measure_value=200,
        sold_by_weight=True,
        images=('https://example.org/product1/orig',),
        show_vendor_code=True,
        price=25,
        measure_quantum=100,
        quantum_quantity=2,
        absolute_quantity=200,
        quantum_price=15,
    )
    create_picked_item(
        order_item_id=fst_order_item_id, picker_id='1', weight=150,
    )

    snd_order_item_id = create_order_item(
        order_id=order_id,
        eats_item_id='eats-124',
        category_id='13',
        category_name='Bread',
        top_level_categories=[
            ('13', 'Bred', None, None, None),
            ('13.1', 'Moldy Bred', None, None, None),
        ],
        barcode_weight_algorithm=None,
        quantity=5,
        measure_max_overweight=None,
        price=20,
        images=('https://example.org/product1/xxx.jpeg',),
        measure_quantum=100,
        quantum_quantity=1,
        absolute_quantity=100,
        quantum_price=10,
    )
    create_picked_item(order_item_id=snd_order_item_id, picker_id='1', count=3)

    headers = utils.da_headers('1')
    if measure_version is not None:
        headers['X-Measure-Version'] = measure_version
    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': '123'},
        headers=headers,
    )
    assert response.status == 200
    assert response.headers['X-Polling-Delay'] == '60'

    expected_response = load_json('order_measure_v2_expected_response.json')
    expected_response['payload']['id'] = str(order_id)
    response_data = response.json()
    assert response_data['payload']['is_asap']
    del response_data['payload']['is_asap']
    assert response_data['payload']['status_updated_at']
    del response_data['payload']['status_updated_at']
    assert response_data['payload']['created_at']
    del response_data['payload']['created_at']
    assert response_data['payload']['updated_at']
    del response_data['payload']['updated_at']
    assert (
        response_data['payload']['held_payment_limit']
        == response_data['payload']['pickedup_total']
        == pickedup_total
    )
    del response_data['payload']['held_payment_limit']
    assert 'payment_limit_coefficient' in response_data['payload']
    del response_data['payload']['payment_limit_coefficient']
    del response_data['payload']['pickedup_total']
    assert response_data['payload']['customer_picker_phone_forwarding']
    del response_data['payload']['customer_picker_phone_forwarding']
    assert expected_response == response_data


@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/order', '/api/v1/order'],
)
async def test_get_order_customer_orders_count(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        handle,
):
    eats_id = '123'
    picker_id = '1'

    create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='picking',
        customer_orders_count=42,
    )

    response = await taxi_eats_picker_orders.get(
        handle,
        params={'eats_id': eats_id},
        headers=utils.make_headers(picker_id),
    )
    assert response.status == 200

    assert response.json()['payload']['customer_orders_count'] == 42
