import json

import bson
import pytest

ERROR_RESPONSE = {'message': 'Invalid'}
AGENT_ID = 'Gpartner'
AGENT_USER_ID = '241406a0972b4c4abbf5187e684f0061'
HEADERS = {'X-External-Service': AGENT_ID, 'Accept-Language': 'ru'}
ORDER_ID = 'a88b3d49a8c24681bbf8d93cd158d8df'
PARK_ID = '81bbf8d93cd158d8dfa88b3d49a8c246'
CLID = '643753730233'


@pytest.fixture(name='mock_driver_photos')
def _mock_driver_photos(mockserver):
    @mockserver.json_handler('/udriver-photos/driver-photos/v1/photo')
    def _driver_photos(request):
        assert request.args['park_id'] == PARK_ID
        assert request.args['driver_profile_id'] == 'uuid_1'
        assert request.args['moderated_only'] == 'true'
        return {
            'actual_photo': {
                'avatar_url': (
                    'https://some.subdomain.yandex.net/some/path/to/avatar'
                ),
                'portrait_url': (
                    'https://some.subdomatin.yandex.net/some/path/to/portrait'
                ),
            },
        }


@pytest.fixture(name='mock_voiceforwarding')
def _mock_voiceforwarding(mockserver):
    @mockserver.json_handler(
        '/driver-order-misc/internal/driver-order-misc/v1/voiceforwarding',
    )
    def _voiceforwarding(_):
        return {'ext': '9003', 'order_id': ORDER_ID, 'phone': '+70003990011'}


@pytest.fixture(name='mock_rating')
def _mock_rating(mockserver):
    @mockserver.json_handler('/driver-ratings/v2/driver/rating')
    def _rating(request):
        assert request.query == {'unique_driver_id': 'unique_driver_id_1'}
        return {'unique_driver_id': 'unique_driver_id_1', 'rating': '4.79'}


@pytest.fixture(name='mock_tips')
def _mock_tips(mockserver):
    @mockserver.json_handler('/tips/internal/tips/v1/get-current-tips-sum')
    def _tips(_):
        return mockserver.make_response(status=500)


@pytest.fixture(name='mock_archive_api')
def _mock_archive_api(mockserver):
    @mockserver.json_handler('/archive-api/archive/order')
    def _archive_order(_):
        return mockserver.make_response(
            bson.BSON.encode(
                {
                    'doc': {
                        'payment_tech': {
                            'finish_handled': False,
                            'type': 'agent',
                            'sum_to_pay': {'ride': 10},
                        },
                    },
                },
            ),
            200,
        )


@pytest.fixture(name='mock_driver_position')
def _mock_driver_trackstory(mockserver):
    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_position(request):
        return {
            'position': {
                'direction': 328,
                'lon': 55.1,
                'lat': 53.2,
                'speed': 30,
                'timestamp': 1502366306,
            },
            'type': 'raw',
        }


@pytest.fixture(name='mock_order_core')
def _mock_order_core(mockserver):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        return {
            'fields': {
                'order': {
                    'performer': {
                        'uuid': 'uuid_1',
                        'car_number': 'А111АА97',
                        'db_id': PARK_ID,
                        'clid': CLID,
                    },
                    'agent': {'agent_id': AGENT_ID},
                    'nz': 'moscow',
                    'request': {
                        'due': '2021-01-01T12:00:00Z',
                        'toll_roads': {
                            'user_had_choice': False,
                            'user_chose_toll_road': True,
                            'auto_payment': True,
                        },
                    },
                },
                'performer': {
                    'alias_id': 'some_alias_id',
                    'candidate_index': 1,
                },
                'candidates': [
                    {'udid': 'wrong_udid'},
                    {'udid': 'unique_driver_id_1'},
                ],
            },
            'order_id': ORDER_ID,
            'replica': 'master',
            'version': '1',
        }


@pytest.mark.config(
    PARTNER_ORDERS_API_PRICE_DETAILS_MAPPING={
        'waiting_time_cost': ['paid_wating'],
        'child_seat': ['booster', 'big_booster'],
        'animals': ['animalstransport'],
        'surge': [],
    },
)
@pytest.mark.pgsql(
    'partner_orders_api', files=['agent_orders.sql', 'price_details.sql'],
)
async def test_order_full(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        mock_driver_photos,
        mock_voiceforwarding,
        mock_rating,
        mock_tips,
        mock_archive_api,
        mock_driver_position,
        mock_order_core,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        return load_json('int_api_response_full.json')

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _parks_retrieve(request):
        return {
            'parks': [
                {'park_id': CLID, 'data': {'account_tax_system': 'osn'}},
            ],
        }

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order',
        json={'order_id': ORDER_ID, 'agent_user_id': AGENT_USER_ID},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response_full.json')


@pytest.mark.config(
    PARTNER_ORDERS_API_PRICE_DETAILS_MAPPING={
        'waiting_time_cost': ['paid_wating'],
        'child_seat': ['booster', 'big_booster'],
        'animals': ['animalstransport'],
        'surge': ['surge'],
    },
)
@pytest.mark.pgsql(
    'partner_orders_api', files=['agent_orders.sql', 'price_details.sql'],
)
async def test_price_details_surge(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        mock_driver_photos,
        mock_voiceforwarding,
        mock_rating,
        mock_tips,
        mock_archive_api,
        mock_driver_position,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        return load_json('int_api_response_full.json')

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        return {
            'fields': {
                'order': {
                    'performer': {
                        'uuid': 'uuid_1',
                        'car_number': 'А111АА97',
                        'db_id': PARK_ID,
                        'clid': CLID,
                    },
                    'agent': {'agent_id': AGENT_ID},
                    'nz': 'moscow',
                    'request': {'due': '2021-01-01T12:00:00Z'},
                },
                'performer': {
                    'alias_id': 'some_alias_id',
                    'candidate_index': 1,
                },
                'candidates': [
                    {'udid': 'wrong_udid'},
                    {'udid': 'unique_driver_id_1'},
                ],
            },
            'order_id': ORDER_ID,
            'replica': 'master',
            'version': '1',
        }

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _parks_retrieve(request):
        return {
            'parks': [
                {'park_id': CLID, 'data': {'account_tax_system': 'osn'}},
            ],
        }

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order',
        json={'order_id': ORDER_ID, 'agent_user_id': AGENT_USER_ID},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response_with_surge.json')


@pytest.mark.parametrize(
    'driver_photos,order_fields,response_status_code',
    (
        (
            {
                'data': {
                    'actual_photo': {
                        'avatar_url': (
                            'https://some.subdomain.yandex.net'
                            '/some/path/to/avatar'
                        ),
                        'portrait_url': (
                            'https://some.subdomatin.yandex.net'
                            '/some/path/to/portrait'
                        ),
                    },
                },
                'status': 200,
            },
            {'status': 500},
            500,
        ),
        (
            {'status': 500},
            {
                'json': {
                    'fields': {
                        'order': {
                            'agent': {'agent_id': AGENT_ID},
                            'nz': 'moscow',
                        },
                        'request': {'due': '2021-01-01T12:00:00Z'},
                    },
                    'order_id': ORDER_ID,
                    'replica': 'master',
                    'version': '1',
                },
            },
            200,
        ),
    ),
)
@pytest.mark.pgsql('partner_orders_api', files=['agent_orders.sql'])
async def test_order_required(
        taxi_partner_orders_api,
        mockserver,
        mock_archive_api,
        load_json,
        driver_photos,
        order_fields,
        response_status_code,
        mock_tips,
        mock_driver_position,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        return load_json('int_api_response_required.json')

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(_):
        return mockserver.make_response(**order_fields)

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/photo')
    def _driver_photos(_):
        return mockserver.make_response(**driver_photos)

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _parks_retrieve(_):
        return mockserver.make_response(status=500)

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order',
        json={'order_id': ORDER_ID, 'agent_user_id': AGENT_USER_ID},
        headers=HEADERS,
    )
    assert response.status_code == response_status_code
    if response.status_code == 200:
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
async def test_order_forwarding_error_response(
        taxi_partner_orders_api,
        mockserver,
        mock_archive_api,
        int_api_status,
        partner_status,
        response_json,
        mock_tips,
        mock_driver_position,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        return mockserver.make_response(
            json.dumps(ERROR_RESPONSE), status=int_api_status,
        )

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        return {
            'fields': {
                'order': {
                    'request': {'due': '2021-01-01T12:00:00Z'},
                    'agent': {'agent_id': AGENT_ID},
                    'nz': 'moscow',
                },
            },
            'order_id': ORDER_ID,
            'replica': 'master',
            'version': '1',
        }

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _parks_retrieve(_):
        return mockserver.make_response(status=500)

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order',
        headers=HEADERS,
        json={'order_id': ORDER_ID, 'agent_user_id': AGENT_USER_ID},
    )
    assert response.status_code == partner_status
    assert response.json() == response_json


@pytest.mark.pgsql('partner_orders_api', files=['agent_orders.sql'])
async def test_order_empty_orders(
        taxi_partner_orders_api,
        mockserver,
        mock_tips,
        mock_driver_position,
        mock_archive_api,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        return {'orders': []}

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        return {
            'fields': {
                'order': {
                    'request': {'due': '2021-01-01T12:00:00Z'},
                    'agent': {'agent_id': AGENT_ID},
                    'nz': 'moscow',
                },
            },
            'order_id': ORDER_ID,
            'replica': 'master',
            'version': '1',
        }

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _parks_retrieve(_):
        return mockserver.make_response(status=500)

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order',
        headers=HEADERS,
        json={'order_id': ORDER_ID, 'agent_user_id': AGENT_USER_ID},
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
async def test_order_mismatch_agent_id(
        taxi_partner_orders_api,
        mockserver,
        mock_archive_api,
        load_json,
        agent_id,
        agent_user_id,
        status,
        mock_tips,
        mock_driver_position,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        return load_json('int_api_response_required.json')

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        return {
            'fields': {
                'order': {
                    'request': {'due': '2021-01-01T12:00:00Z'},
                    'agent': {'agent_id': agent_id},
                    'nz': 'moscow',
                },
            },
            'order_id': ORDER_ID,
            'replica': 'master',
            'version': '1',
        }

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _parks_retrieve(_):
        return mockserver.make_response(status=500)

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order',
        headers=HEADERS,
        json={'order_id': ORDER_ID, 'agent_user_id': agent_user_id},
    )
    assert response.status_code == status


@pytest.mark.parametrize(
    'taximeter_receipt, additional_fields',
    (
        (
            None,
            {
                'drop_off_location': [30.25012, 59.910333],
                'total_distance_meters': None,
            },
        ),
        (
            {
                'dst_actual_point': {'lon': 30.2502146, 'lat': 59.9103492},
                'total_distance': 11119.825254979462,
            },
            {
                'drop_off_location': [30.2502146, 59.9103492],
                'total_distance_meters': 11119,
            },
        ),
        (
            {
                'dst_actual_point': {'lon': 0, 'lat': 0},
                'total_distance': 11119.825254979462,
            },
            {
                'drop_off_location': [30.25012, 59.910333],
                'total_distance_meters': 11119,
            },
        ),
    ),
)
@pytest.mark.config(
    PARTNER_ORDERS_API_PRICE_DETAILS_MAPPING={
        'waiting_time_cost': ['paid_wating'],
        'child_seat': ['booster', 'big_booster'],
        'animals': ['animalstransport'],
        'surge': [],
    },
)
@pytest.mark.pgsql(
    'partner_orders_api', files=['agent_orders.sql', 'price_details.sql'],
)
async def test_order_response_in_complete_state(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        taximeter_receipt,
        additional_fields,
        mock_driver_photos,
        mock_voiceforwarding,
        mock_rating,
        mock_tips,
        mock_archive_api,
        mock_driver_position,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        orders_search_response = load_json('int_api_response_full.json')
        orders_search_response['orders'][0]['status'] = 'complete'
        return orders_search_response

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        order_core_response = load_json('order_core_extended_response.json')

        if taximeter_receipt:
            order_core_response['fields']['order'][
                'taximeter_receipt'
            ] = taximeter_receipt

        return order_core_response

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _parks_retrieve(request):
        return {
            'parks': [
                {'park_id': CLID, 'data': {'account_tax_system': 'osn'}},
            ],
        }

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order',
        headers=HEADERS,
        json={'order_id': ORDER_ID, 'agent_user_id': AGENT_USER_ID},
    )
    expected_response = load_json('response_full.json')
    expected_response.update(
        {
            'ended_at': '2021-01-01T12:02:00+00:00',
            'started_at': '2021-01-01T11:53:00+00:00',
            'arrived_at': '2021-01-01T11:51:00+00:00',
            'status': 'complete',
        },
    )

    filtered = dict((k, v) for k, v in additional_fields.items() if v)
    expected_response.update(filtered)
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'order_status',
    (
        'failed',
        'expired',
        'complete',
        'canceled',
        'search',
        'scheduling',
        'waiting',
        'driving',
        'transporting',
    ),
)
@pytest.mark.parametrize('previous_order_status', ('assigned' 'complete'))
@pytest.mark.pgsql('partner_orders_api', files=['agent_orders.sql'])
async def test_chain_orders(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        order_status,
        previous_order_status,
        mock_driver_photos,
        mock_voiceforwarding,
        mock_rating,
        mock_tips,
        mock_archive_api,
        mock_driver_position,
):
    previous_order_id = 'some_order_id'

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _parks_retrieve(request):
        return {}

    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        response = load_json('int_api_response_full.json')
        response['orders'][0]['status'] = order_status
        return response

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        if request.json['order_id'] == previous_order_id:
            return {
                'fields': {'order': {'status': previous_order_status}},
                'order_id': previous_order_id,
                'replica': 'master',
                'version': '1',
            }
        return {
            'fields': {
                'order': {
                    'performer': {
                        'uuid': 'uuid_1',
                        'car_number': 'А111АА97',
                        'db_id': PARK_ID,
                        'clid': CLID,
                    },
                    'agent': {'agent_id': AGENT_ID},
                    'nz': 'moscow',
                    'request': {'due': '2021-01-01T12:00:00Z'},
                },
                'performer': {
                    'alias_id': 'some_alias_id',
                    'candidate_index': 1,
                },
                'candidates': [
                    {'udid': 'wrong_udid'},
                    {
                        'udid': 'unique_driver_id_1',
                        'cp': {
                            'dest': [37.477, 56.733],
                            'id': previous_order_id,
                        },
                    },
                ],
            },
            'order_id': ORDER_ID,
            'replica': 'master',
            'version': '1',
        }

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order',
        json={'order_id': ORDER_ID, 'agent_user_id': AGENT_USER_ID},
        headers=HEADERS,
    )
    assert response.status_code == 200
    if order_status == 'driving' and previous_order_status == 'assigned':
        assert 'routeinfo' in response.json()
        routeinfo = response.json()['routeinfo']
        assert routeinfo == {
            'points': [
                {
                    'type': 'intermediate_destination',
                    'geopoint': [37.477, 56.733],
                },
            ],
        }
    else:
        assert 'routeinfo' not in response.json()


@pytest.mark.config(
    PARTNER_ORDERS_API_PRICE_DETAILS_MAPPING={
        'waiting_time_cost': ['paid_wating'],
        'child_seat': ['booster', 'big_booster'],
        'animals': ['animalstransport'],
        'surge': ['surge'],
    },
)
@pytest.mark.pgsql(
    'partner_orders_api', files=['agent_orders.sql', 'price_details.sql'],
)
async def test_tips(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        mock_driver_photos,
        mock_voiceforwarding,
        mock_rating,
        mock_archive_api,
        mock_driver_position,
):
    tips_sum = 20

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _parks_retrieve(request):
        return {}

    @mockserver.json_handler('/tips/internal/tips/v1/get-current-tips-sum')
    def _tips(_):
        return {'current_tips_sum': tips_sum}

    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        return load_json('int_api_response_full.json')

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        return {
            'fields': {
                'order': {
                    'performer': {
                        'uuid': 'uuid_1',
                        'car_number': 'А111АА97',
                        'db_id': PARK_ID,
                        'clid': CLID,
                    },
                    'agent': {'agent_id': AGENT_ID},
                    'nz': 'moscow',
                    'request': {'due': '2021-01-01T12:00:00Z'},
                },
                'performer': {
                    'alias_id': 'some_alias_id',
                    'candidate_index': 1,
                },
                'candidates': [
                    {'udid': 'wrong_udid'},
                    {'udid': 'unique_driver_id_1'},
                ],
            },
            'order_id': ORDER_ID,
            'replica': 'master',
            'version': '1',
        }

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order',
        json={'order_id': ORDER_ID, 'agent_user_id': AGENT_USER_ID},
        headers=HEADERS,
    )
    assert response.status_code == 200
    price_details = response.json().get('price_details')
    assert 'tips' in price_details
    assert price_details['tips'] == float(tips_sum) / 10000


@pytest.mark.parametrize(
    [
        'status',
        'payment_tech',
        'archive_api_response_code',
        'expected_code',
        'price_raw',
        'final_cost_is_ready',
    ],
    [
        (
            'assigned',
            {
                'finish_handled': True,
                'sum_to_pay': {'ride': 10},
                'type': 'agent',
            },
            200,
            200,
            555.7,
            False,
        ),
        (
            'assigned',
            {
                'finish_handled': True,
                'sum_to_pay': {'ride': 10},
                'type': 'agent',
            },
            200,
            200,
            555.7,
            False,
        ),
        ('finished', {}, 500, 200, 555.7, False),
        (
            'finished',
            {
                'finish_handled': False,
                'sum_to_pay': {'ride': 10},
                'type': 'agent',
            },
            200,
            200,
            555.7,
            False,
        ),
        (
            'finished',
            {
                'finish_handled': True,
                'sum_to_pay': {'ride': 1490000},
                'type': 'agent',
            },
            200,
            200,
            149,
            True,
        ),
    ],
)
@pytest.mark.config(
    PARTNER_ORDERS_API_PRICE_DETAILS_MAPPING={
        'waiting_time_cost': ['paid_wating'],
        'child_seat': ['booster', 'big_booster'],
        'animals': ['animalstransport'],
        'surge': ['surge'],
    },
)
@pytest.mark.pgsql(
    'partner_orders_api', files=['agent_orders.sql', 'price_details.sql'],
)
async def test_price_raw(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        mock_driver_photos,
        mock_voiceforwarding,
        mock_rating,
        mock_tips,
        mock_driver_position,
        status,
        payment_tech,
        archive_api_response_code,
        expected_code,
        price_raw,
        final_cost_is_ready,
):
    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _parks_retrieve(request):
        return {}

    @mockserver.json_handler('/archive-api/archive/order')
    def _archive_order(_):
        return mockserver.make_response(
            bson.BSON.encode({'doc': {'payment_tech': payment_tech}}),
            archive_api_response_code,
        )

    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        return load_json('int_api_response_full.json')

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_fields(request):
        order_core_response = load_json('order_core_extended_response.json')
        order_core_response['fields']['order_info']['statistics'][
            'status_updates'
        ][-1]['s'] = status
        return order_core_response

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order',
        json={'order_id': ORDER_ID, 'agent_user_id': AGENT_USER_ID},
        headers=HEADERS,
    )
    assert response.status_code == expected_code
    assert response.json().get('price_raw') == price_raw
    assert response.json().get('final_cost_is_ready') == final_cost_is_ready


@pytest.mark.config(
    PARTNER_ORDERS_API_PRICE_DETAILS_MAPPING={
        'waiting_time_cost': ['paid_wating'],
        'child_seat': ['booster', 'big_booster'],
        'animals': ['animalstransport'],
        'surge': [],
    },
)
@pytest.mark.parametrize(
    'int_api_paid_supply, partner_orders_api_paid_supply,'
    'price_details_paid_supply',
    [
        (
            {
                'is_dropped': True,
                'paid_supply_price_raw': 40.0,
                'paid_supply_price': '40 руб.',
            },
            {'is_dropped': True},
            None,
        ),
        (
            {
                'is_dropped': False,
                'paid_supply_price_raw': 40.0,
                'paid_supply_price': '40 руб.',
            },
            {
                'is_dropped': False,
                'paid_supply_price_raw': 40.0,
                'paid_supply_price': '40 руб.',
            },
            40.0,
        ),
        (None, None, None),
    ],
)
@pytest.mark.pgsql(
    'partner_orders_api', files=['agent_orders.sql', 'price_details.sql'],
)
async def test_paid_supply(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        int_api_paid_supply,
        partner_orders_api_paid_supply,
        price_details_paid_supply,
        mock_driver_photos,
        mock_voiceforwarding,
        mock_rating,
        mock_tips,
        mock_archive_api,
        mock_driver_position,
        mock_order_core,
):
    @mockserver.json_handler('/integration-api/v1/orders/search')
    def _order_search(_):
        int_api_response = load_json('int_api_response_full.json')
        if int_api_paid_supply is not None:
            orders = int_api_response.get('orders')
            for order in orders:
                order['paid_supply'] = int_api_paid_supply
        return int_api_response

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _parks_retrieve(request):
        return {
            'parks': [
                {'park_id': CLID, 'data': {'account_tax_system': 'osn'}},
            ],
        }

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order',
        json={'order_id': ORDER_ID, 'agent_user_id': AGENT_USER_ID},
        headers=HEADERS,
    )
    expected_json = load_json('response_full.json')
    if partner_orders_api_paid_supply is not None:
        expected_json['paid_supply'] = partner_orders_api_paid_supply
        if price_details_paid_supply is not None:
            expected_json['price_details'][
                'paid_supply'
            ] = price_details_paid_supply
            expected_json['price_details'][
                'additional_fee'
            ] -= price_details_paid_supply
    assert response.status_code == 200
    assert expected_json == response.json()
