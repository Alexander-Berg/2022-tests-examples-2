# pylint: disable=too-many-lines
import datetime
import math
from typing import Any
from typing import Dict

import pytest
import pytz

from . import utils

HANDLE_V1 = '/4.0/eats-picker/api/v1/order/soft-check'
HANDLE_V2 = '/4.0/eats-picker/api/v2/order/soft-check'


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_get_soft_check_400(taxi_eats_picker_orders, handle):
    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers('picker'), json={},
    )
    assert response.status_code == 400


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_get_soft_check_new_200(
        taxi_eats_picker_orders,
        init_measure_units,
        mockserver,
        create_order,
        get_order_by_eats_id,
        handle,
):
    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def _mock_integrations(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': '',
                    'payload': {'type': 'code128', 'value': '123'},
                },
            },
        )

    eats_id = '1234'
    picker_id = '1'

    create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )

    request_body = {'order_nr': eats_id}

    if handle == HANDLE_V1:
        request_body['picker_items'] = [
            {
                'id': '1',
                'count': 1,
                'measure': {'value': 1000, 'unit': 'gramm'},
            },
        ]

    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers(picker_id), json=request_body,
    )
    expected_json = {
        'payload': {
            'confirmation_type': 'barcode',
            'description': '',
            'payload': {'type': 'code128', 'value': '123'},
        },
    }
    order_soft_check_id = get_order_by_eats_id(eats_id)['soft_check_id']

    assert response.status_code == 200
    assert response.json() == expected_json
    assert order_soft_check_id == '123'


@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_get_soft_check_v2_new_200(
        taxi_eats_picker_orders,
        init_measure_units,
        mockserver,
        create_order,
        create_order_item,
        create_picked_item,
        get_order_by_eats_id,
):
    eats_id = '1234'
    picker_id = '1'

    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def _mock_integrations(request):
        assert request.json == {
            'order_nr': eats_id,
            'picker_items': [
                {
                    'id': 'item-0',
                    'count': 2,
                    'measure': {'value': 1, 'unit': 'GRM'},
                },
                {
                    'id': 'item-1',
                    'count': 2,
                    'measure': {'value': 1, 'unit': 'GRM'},
                },
            ],
        }
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': '',
                    'payload': {'type': 'code128', 'value': '123'},
                },
            },
        )

    order_id = create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )

    order_item_id_0 = create_order_item(order_id, 'item-0')
    order_item_id_1 = create_order_item(order_id, 'item-1')
    order_item_id_2 = create_order_item(order_id, 'item-2')

    create_picked_item(order_item_id_0, cart_version=1, count=1)
    create_picked_item(order_item_id_1, cart_version=1, count=1)
    create_picked_item(order_item_id_2, cart_version=1, count=1)
    create_picked_item(order_item_id_0, cart_version=2, count=2)
    create_picked_item(order_item_id_1, cart_version=2, count=2)
    create_picked_item(order_item_id_0, cart_version=3, count=3)
    create_picked_item(order_item_id_2, cart_version=3, count=3)

    request_body = {'order_nr': eats_id, 'cart_version': 2}

    response = await taxi_eats_picker_orders.post(
        HANDLE_V2, headers=utils.da_headers(picker_id), json=request_body,
    )
    expected_json = {
        'payload': {
            'confirmation_type': 'barcode',
            'description': '',
            'payload': {'type': 'code128', 'value': '123'},
        },
    }
    order_soft_check_id = get_order_by_eats_id(eats_id)['soft_check_id']

    assert response.status_code == 200
    assert response.json() == expected_json
    assert order_soft_check_id == '123'


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@utils.send_order_events_config()
async def test_get_soft_check_add_item_200(
        taxi_eats_picker_orders,
        init_measure_units,
        mockserver,
        create_order,
        get_order_by_eats_id,
        create_order_item,
        create_order_soft_check,
        get_order_soft_check,
        mock_processing,
        handle,
):

    eats_id = '1234'
    picker_id = '1'
    first_soft_check_id = '111'
    second_soft_check_id = '222'

    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def _mock_integrations(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': '',
                    'payload': {
                        'type': 'code128',
                        'value': second_soft_check_id,
                    },
                },
            },
        )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    order_id = create_order(
        state='picking',
        eats_id=eats_id,
        picker_id=picker_id,
        soft_check_id=first_soft_check_id,
    )

    for i in range(3):
        create_order_item(order_id=order_id, eats_item_id=str(i))

    response = await taxi_eats_picker_orders.post(
        f'/4.0/eats-picker/api/v2/order/cart?eats_id={eats_id}',
        json={
            'cart_version': 1,
            'picker_items': [
                {'id': str(i), 'count': i + 1, 'weight': None}
                for i in range(1)
            ],
        },
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200

    create_order_soft_check(
        order_id, eats_id, 1, picker_id, first_soft_check_id,
    )

    assert mock_processing.times_called == 1

    response = await taxi_eats_picker_orders.post(
        f'/4.0/eats-picker/api/v2/order/cart?eats_id={eats_id}',
        json={
            'cart_version': 2,
            'picker_items': [
                {'id': str(i), 'count': i + 1, 'weight': None}
                for i in range(2)
            ],
        },
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200

    assert mock_processing.times_called == 2

    request_body = {'order_nr': eats_id}
    if handle == HANDLE_V1:
        request_body['picker_items'] = [
            {
                'id': '0',
                'count': 1,
                'measure': {'value': 1000, 'unit': 'gramm'},
            },
            {
                'id': '1',
                'count': 2,
                'measure': {'value': 1000, 'unit': 'gramm'},
            },
        ]

    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers(picker_id), json=request_body,
    )
    expected_json = {
        'payload': {
            'confirmation_type': 'barcode',
            'description': '',
            'payload': {'type': 'code128', 'value': second_soft_check_id},
        },
    }
    order_soft_check_id = get_order_by_eats_id(eats_id)['soft_check_id']

    assert response.status_code == 200
    assert response.json() == expected_json
    assert order_soft_check_id == second_soft_check_id

    soft_check = get_order_soft_check(order_id)
    assert soft_check['cart_version'] == 3
    assert soft_check['value'] == second_soft_check_id


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@utils.send_order_events_config()
async def test_get_soft_check_remove_item_200(
        taxi_eats_picker_orders,
        init_measure_units,
        mockserver,
        create_order,
        get_order_by_eats_id,
        create_order_item,
        create_order_soft_check,
        get_order_soft_check,
        mock_processing,
        handle,
):

    eats_id = '1234'
    picker_id = '1'
    first_soft_check_id = '111'
    second_soft_check_id = '222'

    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def _mock_integrations(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': '',
                    'payload': {
                        'type': 'code128',
                        'value': second_soft_check_id,
                    },
                },
            },
        )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    order_id = create_order(
        state='picking',
        eats_id=eats_id,
        picker_id=picker_id,
        soft_check_id=first_soft_check_id,
    )

    for i in range(3):
        create_order_item(order_id=order_id, eats_item_id=str(i))

    response = await taxi_eats_picker_orders.post(
        f'/4.0/eats-picker/api/v2/order/cart?eats_id={eats_id}',
        json={
            'cart_version': 1,
            'picker_items': [
                {'id': str(i), 'count': i + 1, 'weight': None}
                for i in range(2)
            ],
        },
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    create_order_soft_check(
        order_id, eats_id, 1, picker_id, first_soft_check_id,
    )

    response = await taxi_eats_picker_orders.post(
        f'/4.0/eats-picker/api/v2/order/cart?eats_id={eats_id}',
        json={
            'cart_version': 2,
            'picker_items': [
                {'id': str(i), 'count': i + 1, 'weight': None}
                for i in range(1)
            ],
        },
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200

    assert mock_processing.times_called == 2

    request_body = {'order_nr': eats_id}
    if handle == HANDLE_V1:
        request_body['picker_items'] = [
            {
                'id': '0',
                'count': 1,
                'measure': {'value': 1000, 'unit': 'gramm'},
            },
        ]

    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers(picker_id), json=request_body,
    )
    expected_json = {
        'payload': {
            'confirmation_type': 'barcode',
            'description': '',
            'payload': {'type': 'code128', 'value': second_soft_check_id},
        },
    }
    order_soft_check_id = get_order_by_eats_id(eats_id)['soft_check_id']

    assert response.status_code == 200
    assert response.json() == expected_json
    assert order_soft_check_id == second_soft_check_id

    soft_check = get_order_soft_check(order_id)
    assert soft_check['cart_version'] == 3
    assert soft_check['value'] == second_soft_check_id


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@utils.send_order_events_config()
async def test_get_soft_check_alter_count_item_200(
        taxi_eats_picker_orders,
        init_measure_units,
        mockserver,
        create_order,
        get_order_by_eats_id,
        create_order_item,
        create_order_soft_check,
        get_order_soft_check,
        mock_processing,
        handle,
):

    eats_id = '1234'
    picker_id = '1'
    first_soft_check_id = '111'
    second_soft_check_id = '222'

    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def _mock_integrations(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': '',
                    'payload': {
                        'type': 'code128',
                        'value': second_soft_check_id,
                    },
                },
            },
        )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    order_id = create_order(
        state='picking',
        eats_id=eats_id,
        picker_id=picker_id,
        soft_check_id=first_soft_check_id,
    )

    for i in range(3):
        create_order_item(order_id=order_id, eats_item_id=str(i))

    response = await taxi_eats_picker_orders.post(
        f'/4.0/eats-picker/api/v2/order/cart?eats_id={eats_id}',
        json={
            'cart_version': 1,
            'picker_items': [
                {'id': str(i), 'count': 1, 'weight': None} for i in range(1)
            ],
        },
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    create_order_soft_check(
        order_id, eats_id, 1, picker_id, first_soft_check_id,
    )

    response = await taxi_eats_picker_orders.post(
        f'/4.0/eats-picker/api/v2/order/cart?eats_id={eats_id}',
        json={
            'cart_version': 2,
            'picker_items': [
                {'id': str(i), 'count': 2, 'weight': None} for i in range(1)
            ],
        },
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200

    assert mock_processing.times_called == 2

    request_body = {'order_nr': eats_id}
    if handle == HANDLE_V1:
        request_body['picker_items'] = [
            {
                'id': '0',
                'count': 2,
                'measure': {'value': 1000, 'unit': 'gramm'},
            },
        ]

    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers(picker_id), json=request_body,
    )
    expected_json = {
        'payload': {
            'confirmation_type': 'barcode',
            'description': '',
            'payload': {'type': 'code128', 'value': second_soft_check_id},
        },
    }
    order_soft_check_id = get_order_by_eats_id(eats_id)['soft_check_id']

    assert response.status_code == 200
    assert response.json() == expected_json
    assert order_soft_check_id == second_soft_check_id

    soft_check = get_order_soft_check(order_id)
    assert soft_check['cart_version'] == 3
    assert soft_check['value'] == second_soft_check_id


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@utils.send_order_events_config()
async def test_get_soft_check_no_request_200(
        taxi_eats_picker_orders,
        init_measure_units,
        mockserver,
        create_order,
        get_order_by_eats_id,
        create_order_item,
        create_order_soft_check,
        get_order_soft_check,
        mock_processing,
        handle,
):

    eats_id = '1234'
    picker_id = '1'
    first_soft_check_id = '111'
    second_soft_check_id = '222'

    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def _mock_integrations(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': '',
                    'payload': {
                        'type': 'code128',
                        'value': second_soft_check_id,
                    },
                },
            },
        )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    order_id = create_order(
        state='picking',
        eats_id=eats_id,
        picker_id=picker_id,
        soft_check_id=first_soft_check_id,
    )

    for i in range(3):
        create_order_item(order_id=order_id, eats_item_id=str(i))

    response = await taxi_eats_picker_orders.post(
        f'/4.0/eats-picker/api/v2/order/cart?eats_id={eats_id}',
        json={
            'cart_version': 1,
            'picker_items': [
                {'id': str(i), 'count': 1, 'weight': None} for i in range(1)
            ],
        },
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    create_order_soft_check(
        order_id, eats_id, 2, picker_id, first_soft_check_id,
    )

    response = await taxi_eats_picker_orders.post(
        f'/4.0/eats-picker/api/v2/order/cart?eats_id={eats_id}',
        json={
            'cart_version': 2,
            'picker_items': [
                {'id': str(i), 'count': 1, 'weight': None} for i in range(1)
            ],
        },
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 202

    assert mock_processing.times_called == 1

    request_body = {'order_nr': eats_id}
    if handle == HANDLE_V1:
        request_body['picker_items'] = [
            {
                'id': '0',
                'count': 1,
                'measure': {'value': 1000, 'unit': 'gramm'},
            },
        ]

    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers(picker_id), json=request_body,
    )
    expected_json = {
        'payload': {
            'confirmation_type': 'barcode',
            'description': '',
            'payload': {'type': 'code128', 'value': first_soft_check_id},
        },
    }
    order_soft_check_id = get_order_by_eats_id(eats_id)['soft_check_id']

    assert response.status_code == 200
    assert response.json() == expected_json
    assert order_soft_check_id == first_soft_check_id

    soft_check = get_order_soft_check(order_id)
    assert soft_check['cart_version'] == 2
    assert soft_check['value'] == first_soft_check_id


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_get_soft_check_404(
        taxi_eats_picker_orders, mockserver, create_order, handle,
):
    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def _mock_integrations(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': '',
                    'payload': {'type': 'code128', 'value': '123'},
                },
            },
        )

    order_id = '1234'
    picker_id = '1'

    create_order(
        eats_id=order_id,
        picker_id=picker_id,
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )

    request_body = {'order_nr': '123'}
    if handle == HANDLE_V1:
        request_body['picker_items'] = [
            {
                'id': '1',
                'count': 1,
                'measure': {'value': 1000, 'unit': 'gramm'},
            },
        ]

    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers(picker_id), json=request_body,
    )
    assert response.status_code == 404


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_get_soft_check_500(
        taxi_eats_picker_orders, mockserver, create_order, handle,
):
    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def _mock_integrations(request):
        return mockserver.make_response(
            status=403, json={'code': '403', 'message': ''},
        )

    order_id = '1234'
    picker_id = '1'

    create_order(
        eats_id=order_id,
        picker_id=picker_id,
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )

    request_body = {'order_nr': order_id}
    if handle == HANDLE_V1:
        request_body['picker_items'] = [
            {
                'id': '1',
                'count': 1,
                'measure': {'value': 1000, 'unit': 'gramm'},
            },
        ]

    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers(picker_id), json=request_body,
    )
    assert response.status_code == 500


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@pytest.mark.parametrize(
    'brand_id, exp_on',
    [('brand1', True), ('brand2', True), ('brand1', False)],
)
async def test_get_soft_check_text_config(
        taxi_eats_picker_orders,
        mockserver,
        create_order,
        brand_id,
        exp_on,
        experiments3,
        load_json,
        handle,
):
    expected_json = {
        'payload': {
            'confirmation_type': 'barcode',
            'description': '',
            'payload': {'type': 'code128', 'value': '123'},
        },
    }
    exp_json = load_json('exp3_soft_check_text_on.json')

    if not exp_on:
        exp_json['configs'][0]['match']['enabled'] = False
    elif brand_id == 'brand1':
        expected_json['text'] = 'test result text'
    else:
        expected_json['text'] = ''

    experiments3.add_experiments_json(exp_json)

    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def _mock_integrations(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': '',
                    'payload': {'type': 'code128', 'value': '123'},
                },
            },
        )

    eats_id = '1234'
    picker_id = '1'

    create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id=brand_id,
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )

    request_body = {'order_nr': eats_id}
    if handle == HANDLE_V1:
        request_body['picker_items'] = [
            {
                'id': '1',
                'count': 1,
                'measure': {'value': 1000, 'unit': 'gramm'},
            },
        ]

    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers(picker_id), json=request_body,
    )

    assert response.status_code == 200
    assert response.json() == expected_json


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_get_soft_check_lock_timeout_500(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_soft_check_lock,
        mocked_time,
        testpoint,
        handle,
):
    eats_id = '1234'
    picker_id = '1'

    create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )

    expires_at = mocked_time.now().replace(
        tzinfo=pytz.UTC,
    ) + datetime.timedelta(seconds=10)
    create_order_soft_check_lock(eats_id, expires_at)

    @testpoint('eats_picker_orders::soft-check-lock-timeout')
    async def timeout_exceeded(arg):
        mocked_time.sleep(11)
        await taxi_eats_picker_orders.invalidate_caches()

    request_body = {'order_nr': eats_id}
    if handle == HANDLE_V1:
        request_body['picker_items'] = []

    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers(picker_id), json=request_body,
    )

    assert response.status_code == 500
    assert response.json()['code'] == 'SOFT_CHECK_LOCK_TIMEOUT_EXCEEDED'
    assert timeout_exceeded.times_called == 1


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@pytest.mark.parametrize(
    'locked, expires_in, status',
    [
        (False, None, 200),
        (True, -1, 200),
        (True, 0, 200),
        (True, 1, 500),
        (True, 2, 500),
    ],
)
async def test_get_soft_check_lock_expiration(
        taxi_eats_picker_orders,
        init_measure_units,
        mockserver,
        create_order,
        create_order_soft_check_lock,
        get_order_by_eats_id,
        testpoint,
        mocked_time,
        locked,
        expires_in,
        status,
        handle,
):
    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def _mock_integrations(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': '',
                    'payload': {'type': 'code128', 'value': '123'},
                },
            },
        )

    eats_id = '1234'
    picker_id = '1'

    if locked:
        expires_at = mocked_time.now().replace(
            tzinfo=pytz.UTC,
        ) + datetime.timedelta(seconds=expires_in)
        create_order_soft_check_lock(eats_id, expires_at)

    @testpoint('eats_picker_orders::soft-check-lock-timeout')
    async def timeout_exceeded(arg):
        mocked_time.sleep(11)
        await taxi_eats_picker_orders.invalidate_caches()

    create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )

    request_body = {'order_nr': eats_id}
    if handle == HANDLE_V1:
        request_body['picker_items'] = [
            {
                'id': '1',
                'count': 1,
                'measure': {'value': 1000, 'unit': 'gramm'},
            },
        ]

    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers(picker_id), json=request_body,
    )

    assert response.status_code == status
    if status == 200:
        expected_json = {
            'payload': {
                'confirmation_type': 'barcode',
                'description': '',
                'payload': {'type': 'code128', 'value': '123'},
            },
        }
        order_soft_check_id = get_order_by_eats_id(eats_id)['soft_check_id']
        assert response.json() == expected_json
        assert order_soft_check_id == '123'
        assert timeout_exceeded.times_called == 0
    elif status == 500:
        assert response.json()['code'] == 'SOFT_CHECK_LOCK_TIMEOUT_EXCEEDED'
        assert timeout_exceeded.times_called == 1


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
@pytest.mark.parametrize('sleep', range(1, 6))
async def test_get_soft_check_lock_retry_500(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_soft_check_lock,
        testpoint,
        mocked_time,
        sleep: int,
        handle,
):
    eats_id = '1234'
    picker_id = '1'

    create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )

    expires_at = mocked_time.now().replace(
        tzinfo=pytz.UTC,
    ) + datetime.timedelta(seconds=10)
    create_order_soft_check_lock(eats_id, expires_at)

    @testpoint('eats_picker_orders::soft-check-lock-timeout')
    async def timeout_exceeded(arg):
        mocked_time.sleep(sleep)
        await taxi_eats_picker_orders.invalidate_caches()

    request_body: Dict[str, Any] = {'order_nr': eats_id}
    if handle == HANDLE_V1:
        request_body['picker_items'] = []

    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers(picker_id), json=request_body,
    )

    assert response.status_code == 500
    assert response.json()['code'] == 'SOFT_CHECK_LOCK_TIMEOUT_EXCEEDED'
    assert timeout_exceeded.times_called == math.ceil(10 / sleep)


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
@pytest.mark.experiments3(filename='config3_order_soft_check.json')
async def test_get_soft_check_lock_retry_200(
        taxi_eats_picker_orders,
        init_measure_units,
        mockserver,
        create_order,
        create_order_soft_check_lock,
        delete_order_soft_check_lock,
        get_order_by_eats_id,
        testpoint,
        mocked_time,
        handle,
):
    @mockserver.json_handler(
        '/eats-core-integrations/integrations/picker/cart_confirmation',
    )
    def _mock_integrations(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'confirmation_type': 'barcode',
                    'description': '',
                    'payload': {'type': 'code128', 'value': '123'},
                },
            },
        )

    eats_id = '1234'
    picker_id = '1'

    create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        state='picking',
        payment_value=110,
        flow_type='picking_packing',
        brand_id='i77',
        estimated_picking_time=600,
        finish_picking_at='1976-01-19T15:00:27.010000+03:00',
    )

    expires_at = mocked_time.now().replace(
        tzinfo=pytz.UTC,
    ) + datetime.timedelta(seconds=10)
    create_order_soft_check_lock(eats_id, expires_at)

    @testpoint('eats_picker_orders::soft-check-lock-timeout')
    async def timeout_exceeded(arg):
        if timeout_exceeded.times_called == 2:
            delete_order_soft_check_lock(eats_id)
        mocked_time.sleep(1)
        await taxi_eats_picker_orders.invalidate_caches()

    request_body = {'order_nr': eats_id}
    if handle == HANDLE_V1:
        request_body['picker_items'] = [
            {
                'id': '1',
                'count': 1,
                'measure': {'value': 1000, 'unit': 'gramm'},
            },
        ]

    response = await taxi_eats_picker_orders.post(
        handle, headers=utils.da_headers(picker_id), json=request_body,
    )

    expected_json = {
        'payload': {
            'confirmation_type': 'barcode',
            'description': '',
            'payload': {'type': 'code128', 'value': '123'},
        },
    }
    order_soft_check_id = get_order_by_eats_id(eats_id)['soft_check_id']

    assert response.status_code == 200
    assert response.json() == expected_json
    assert order_soft_check_id == '123'
    assert timeout_exceeded.times_called == 3


@pytest.mark.parametrize('handle', [HANDLE_V1, HANDLE_V2])
async def test_get_soft_check_401(taxi_eats_picker_orders, handle):
    bad_header = {
        'X-Request-Application-Version': '9.99 (9999)',
        'X-YaEda-CourierId': '123',
    }
    request_body = {'order_nr': '1234'}
    if handle == HANDLE_V1:
        request_body['picker_items'] = [
            {
                'id': '1',
                'count': 1,
                'measure': {'value': 1000, 'unit': 'gramm'},
            },
        ]
    response = await taxi_eats_picker_orders.post(
        handle, headers=bad_header, json=request_body,
    )
    assert response.status_code == 401
