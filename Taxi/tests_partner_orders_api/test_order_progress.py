import json

import pytest

ERROR_RESPONSE = {'message': 'Invalid'}
AGENT_ID = 'Gpartner'
AGENT_USER_ID = '241406a0972b4c4abbf5187e684f0061'
HEADERS = {'X-External-Service': AGENT_ID, 'Accept-Language': 'ru'}
ORDER_ID = 'a88b3d49a8c24681bbf8d93cd158d8df'
PARK_ID = '643753730233'


@pytest.fixture(name='mock_driver_position')
def _mock_driver_trackstory(mockserver):
    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_position(request):
        return {
            'position': {
                'direction': 30,
                'lon': 55.1,
                'lat': 53.2,
                'speed': 30,
                'timestamp': 1502366306,
            },
            'type': 'raw',
        }


@pytest.mark.pgsql('partner_orders_api', files=['agent_orders.sql'])
async def test_order_progress_full(
        taxi_partner_orders_api, mockserver, mock_driver_position, load_json,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        return load_json('int_api_response_full.json')

    @mockserver.json_handler(
        '/driver-order-misc/internal/driver-order-misc/v1/voiceforwarding',
    )
    def _voiceforwarding(_):
        return {'ext': '9003', 'order_id': ORDER_ID, 'phone': '+70003990011'}

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        assert request.json['order_id'] == ORDER_ID
        assert set(request.json['fields']) == set(
            [
                'order.agent.agent_id',
                'order.performer.uuid',
                'order.performer.db_id',
                'performer.alias_id',
                'updated',
            ],
        )
        return {
            'fields': {
                'updated': '2021-02-16T11:45:36.475+00:00',
                'order': {
                    'performer': {
                        'uuid': 'uuid_1',
                        'car_number': 'А111АА97',
                        'db_id': PARK_ID,
                    },
                    'agent': {'agent_id': AGENT_ID},
                },
                'performer': {'alias_id': 'some_alias_id'},
            },
            'order_id': ORDER_ID,
            'replica': 'master',
            'version': '1',
        }

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/progress',
        json={'order_id': ORDER_ID, 'agent_user_id': AGENT_USER_ID},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response_full.json')


@pytest.mark.pgsql('partner_orders_api', files=['agent_orders.sql'])
async def test_order_progress_required(
        taxi_partner_orders_api, mockserver, load_json,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        return load_json('int_api_response_required.json')

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_position(request):
        return mockserver.make_response(
            json={'code': 'not_found', 'message': ''}, status=404,
        )

    @mockserver.json_handler(
        '/driver-order-misc/internal/driver-order-misc/v1/voiceforwarding',
    )
    def _voiceforwarding(_):
        return {'ext': '9003', 'order_id': ORDER_ID, 'phone': '+70003990011'}

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        assert set(request.json['fields']) == set(
            [
                'order.agent.agent_id',
                'order.performer.uuid',
                'order.performer.db_id',
                'performer.alias_id',
                'updated',
            ],
        )
        return {
            'fields': {
                'order': {
                    'performer': {
                        'uuid': 'uuid_1',
                        'car_number': 'А111АА97',
                        'db_id': PARK_ID,
                    },
                    'agent': {'agent_id': AGENT_ID},
                },
                'performer': {'alias_id': 'some_alias_id'},
            },
            'order_id': ORDER_ID,
            'replica': 'master',
            'version': '1',
        }

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/progress',
        json={'order_id': ORDER_ID, 'agent_user_id': AGENT_USER_ID},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response_required.json')


@pytest.mark.parametrize(
    'int_api_status, partner_status, response_json',
    [
        (
            400,
            400,
            {'code': 'BAD_REQUEST', 'message': 'Invalid request parameters'},
        ),
        (
            401,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
        (
            429,
            429,
            {'code': 'TOO_MANY_REQUESTS', 'message': 'Too many requests'},
        ),
        (
            500,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
    ],
)
@pytest.mark.pgsql('partner_orders_api', files=['agent_orders.sql'])
async def test_order_progress_forwarding_error_response(
        taxi_partner_orders_api,
        mockserver,
        mock_driver_position,
        int_api_status,
        partner_status,
        response_json,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_draft(_):
        return mockserver.make_response(
            json.dumps(ERROR_RESPONSE), status=int_api_status,
        )

    @mockserver.json_handler(
        '/driver-order-misc/internal/driver-order-misc/v1/voiceforwarding',
    )
    def _voiceforwarding(_):
        return {'ext': '9003', 'order_id': ORDER_ID, 'phone': '+70003990011'}

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        assert set(request.json['fields']) == set(
            [
                'order.agent.agent_id',
                'order.performer.uuid',
                'order.performer.db_id',
                'performer.alias_id',
                'updated',
            ],
        )
        return {
            'fields': {
                'order': {
                    'performer': {
                        'uuid': 'uuid_1',
                        'car_number': 'А111АА97',
                        'db_id': PARK_ID,
                    },
                    'agent': {'agent_id': AGENT_ID},
                },
                'performer': {'alias_id': 'some_alias_id'},
            },
            'order_id': ORDER_ID,
            'replica': 'master',
            'version': '1',
        }

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/progress',
        headers=HEADERS,
        json={'order_id': 'some_order_id', 'agent_user_id': AGENT_USER_ID},
    )
    assert response.status_code == partner_status
    assert response.json() == response_json


@pytest.mark.pgsql('partner_orders_api', files=['agent_orders.sql'])
async def test_order_progress_empty_orders(
        taxi_partner_orders_api, mockserver, mock_driver_position,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_draft(_):
        return {'orders': []}

    @mockserver.json_handler(
        '/driver-order-misc/internal/driver-order-misc/v1/voiceforwarding',
    )
    def _voiceforwarding(_):
        return {'ext': '9003', 'order_id': ORDER_ID, 'phone': '+70003990011'}

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        assert set(request.json['fields']) == set(
            [
                'order.agent.agent_id',
                'order.performer.uuid',
                'order.performer.db_id',
                'performer.alias_id',
                'updated',
            ],
        )
        return {
            'fields': {
                'order': {
                    'performer': {
                        'uuid': 'uuid_1',
                        'car_number': 'А111АА97',
                        'db_id': PARK_ID,
                    },
                    'agent': {'agent_id': AGENT_ID},
                },
                'performer': {'alias_id': 'some_alias_id'},
            },
            'order_id': ORDER_ID,
            'replica': 'master',
            'version': '1',
        }

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/progress',
        headers=HEADERS,
        json={'order_id': 'some_order_id', 'agent_user_id': AGENT_USER_ID},
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'agent_id, agent_user_id, status',
    (
        ('wrong_agent_id', AGENT_USER_ID, 400),
        (AGENT_ID, 'wrong_agent_user_id', 500),
    ),
)
@pytest.mark.pgsql('partner_orders_api', files=['agent_orders.sql'])
async def test_order_progress_mismatch_agent_id(
        taxi_partner_orders_api,
        mockserver,
        mock_driver_position,
        load_json,
        agent_id,
        agent_user_id,
        status,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        return load_json('int_api_response_required.json')

    @mockserver.json_handler(
        '/driver-order-misc/internal/driver-order-misc/v1/voiceforwarding',
    )
    def _voiceforwarding(_):
        return {'ext': '9003', 'order_id': ORDER_ID, 'phone': '+70003990011'}

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        assert request.json['order_id'] == ORDER_ID
        assert set(request.json['fields']) == set(
            [
                'order.agent.agent_id',
                'order.performer.uuid',
                'order.performer.db_id',
                'performer.alias_id',
                'updated',
            ],
        )
        return {
            'fields': {
                'order': {
                    'performer': {
                        'uuid': 'uuid_1',
                        'car_number': 'А111АА97',
                        'db_id': PARK_ID,
                    },
                    'agent': {'agent_id': agent_id},
                },
                'performer': {'alias_id': 'some_alias_id'},
            },
            'order_id': ORDER_ID,
            'replica': 'master',
            'version': '1',
        }

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/progress',
        headers=HEADERS,
        json={'order_id': ORDER_ID, 'agent_user_id': agent_user_id},
    )
    assert response.status_code == status
