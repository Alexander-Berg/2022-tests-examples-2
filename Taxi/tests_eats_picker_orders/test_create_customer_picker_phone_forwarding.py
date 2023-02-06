import copy
import datetime
import json

import pytest

from . import utils


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


@pytest.mark.parametrize('customer_to_picker_allowed', [True, False])
@pytest.mark.now('2020-10-20T17:50:00+0000')
@utils.send_order_events_config()
@utils.update_phone_forwarding_config()
async def test_create_new_phone_when_expired(
        taxi_eats_picker_orders,
        stq,
        stq_runner,
        create_order,
        eats_core,
        vgw_api,
        mock_processing,
        customer_to_picker_allowed,
        experiments3,
):
    eats_id = '123'
    picker_id = '1'

    if customer_to_picker_allowed:
        experiments3.add_config(
            **utils.allowed_phone_forwardings('customer', 'picker'),
        )
    else:
        # Разрешаем только несуществующую переадресацию,
        # чтобы тем самым запретить все остальные
        experiments3.add_config(
            **utils.allowed_phone_forwardings('unknown', 'unknown'),
        )
    await taxi_eats_picker_orders.invalidate_caches()

    create_order(
        eats_id=eats_id,
        picker_id=picker_id,
        picker_phone_id='phone_1',
        customer_phone_id='whatever',
        customer_picker_phone_forwarding=(
            '+7-call-me-customer (from picker)',
            '2020-10-20T17:45:00+0000',
        ),
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/picker/orders',
        params={'picker_id': picker_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200
    payload = response.json()['orders'][0]
    assert 'customer_picker_phone_forwarding' not in payload

    if customer_to_picker_allowed:
        next_call = stq.update_phone_forwarding.next_call()
        task_id = next_call['id']
        kwargs = next_call['kwargs']
        await stq_runner.update_phone_forwarding.call(
            task_id=task_id, kwargs=kwargs,
        )
    else:
        assert stq.update_phone_forwarding.times_called == 0

    response = await taxi_eats_picker_orders.get(
        '/api/v1/picker/orders',
        params={'picker_id': picker_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 200
    payload = response.json()['orders'][0]
    if customer_to_picker_allowed:
        assert payload['customer_picker_phone_forwarding'] == {
            'expires_at': '2020-10-20T20:50:00+00:00',
            'phone': '+7-call-me-baby,,1111',
        }
    else:
        assert 'customer_picker_phone_forwarding' not in payload
    assert mock_processing.times_called == (
        1 if customer_to_picker_allowed else 0
    )


@pytest.mark.parametrize('method', ['put', 'post'])
@pytest.mark.parametrize('customer_to_picker_allowed', [True, False])
@pytest.mark.now('2020-10-20T17:50:00+0000')
@utils.send_order_events_config()
@utils.update_phone_forwarding_config()
async def test_update_phone_on_picker_assign(
        taxi_eats_picker_orders,
        stq,
        stq_runner,
        create_order,
        method,
        eats_core,
        vgw_api,
        mock_processing,
        mock_apply_state,
        customer_to_picker_allowed,
        experiments3,
):
    eats_id = '123'
    new_picker_id = '1'

    if customer_to_picker_allowed:
        experiments3.add_config(
            **utils.allowed_phone_forwardings('customer', 'picker'),
        )
    else:
        # Разрешаем только несуществующую переадресацию,
        # чтобы тем самым запретить все остальные
        experiments3.add_config(
            **utils.allowed_phone_forwardings('unknown', 'unknown'),
        )
    await taxi_eats_picker_orders.invalidate_caches()

    create_order(
        eats_id=eats_id,
        customer_phone_id='phone_2',
        picker_id=None,
        state='new',
    )
    response = await taxi_eats_picker_orders.request(
        method,
        f'/api/v1/order/courier?eats_id={eats_id}',
        json={
            'id': new_picker_id,
            'requisites': [{'type': 'TinkoffBank', 'value': '222'}],
            'picker_phone_id': 'phone_1',
            'picker_name': 'Picker Pickerovich',
        },
    )
    assert response.status_code == 204
    assert mock_processing.times_called == 1

    response = await taxi_eats_picker_orders.get(
        '/api/v1/picker/orders',
        params={'picker_id': new_picker_id},
        headers=utils.da_headers(new_picker_id),
    )
    assert response.status == 200
    payload = response.json()['orders'][0]
    assert 'customer_picker_phone_forwarding' not in payload

    next_call = stq.update_phone_forwarding.next_call()
    task_id = next_call['id']
    kwargs = next_call['kwargs']
    await stq_runner.update_phone_forwarding.call(
        task_id=task_id, kwargs=kwargs,
    )
    assert (
        mock_processing.times_called == 2 if customer_to_picker_allowed else 1
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/picker/orders',
        params={'picker_id': new_picker_id},
        headers=utils.da_headers(new_picker_id),
    )
    assert response.status == 200
    payload = response.json()['orders'][0]
    if customer_to_picker_allowed:
        assert payload['customer_picker_phone_forwarding'] == {
            'expires_at': '2020-10-20T20:50:00+00:00',
            'phone': '+7-call-me-baby,,1111',
        }
    else:
        assert 'customer_picker_phone_forwarding' not in payload
    assert (
        mock_processing.times_called == 2 if customer_to_picker_allowed else 1
    )
