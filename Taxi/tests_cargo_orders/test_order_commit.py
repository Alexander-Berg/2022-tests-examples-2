import pytest


ORDER_ID = '9db1622e-582d-4091-b6fc-4cb2ffdc12c0'

PROFILE_REQUEST = {
    'user': {'personal_phone_id': 'personal_phone_id_1'},
    'name': 'Насруло',
    'sourceid': 'cargo',
}


def commit_request():
    return {
        'order_id': ORDER_ID,
        'waybill_ref': 'waybill-ref',
        'segments': [{'claim_id': 'test_claim_1', 'segment_id': 'segment1'}],
        'path': [
            {
                'segment_id': 'segment1',
                'claim_point_id': 1,
                'waybill_point_id': 'waybill_point0',
                'visit_order': 1,
            },
            {
                'segment_id': 'segment1',
                'claim_point_id': 2,
                'waybill_point_id': 'waybill_point1',
                'visit_order': 2,
            },
            {
                'segment_id': 'segment1',
                'claim_point_id': 3,
                'waybill_point_id': 'waybill_point1',
                'visit_order': 3,
            },
        ],
    }


def batch_commit_request():
    return {
        'order_id': ORDER_ID,
        'waybill_ref': 'waybill-ref',
        'segments': [
            {'claim_id': 'test_claim_1', 'segment_id': 'segment1'},
            {'claim_id': 'test_claim_2', 'segment_id': 'segment2'},
        ],
        'path': [
            {
                'segment_id': 'segment1',
                'claim_point_id': 1,
                'waybill_point_id': 'waybill_point0',
                'visit_order': 1,
            },
            {
                'segment_id': 'segment2',
                'claim_point_id': 1,
                'waybill_point_id': 'waybill_point1',
                'visit_order': 2,
            },
            {
                'segment_id': 'segment1',
                'claim_point_id': 2,
                'waybill_point_id': 'waybill_point2',
                'visit_order': 3,
            },
            {
                'segment_id': 'segment1',
                'claim_point_id': 3,
                'waybill_point_id': 'waybill_point3',
                'visit_order': 4,
            },
            {
                'segment_id': 'segment2',
                'claim_point_id': 2,
                'waybill_point_id': 'waybill_point4',
                'visit_order': 5,
            },
            {
                'segment_id': 'segment2',
                'claim_point_id': 3,
                'waybill_point_id': 'waybill_point5',
                'visit_order': 6,
            },
        ],
    }


@pytest.fixture(autouse=True)
def default_mocks(mockserver):
    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _profile(request):
        assert request.json == PROFILE_REQUEST
        return {
            'dont_ask_name': False,
            'experiments': [],
            'name': 'Насруло',
            'personal_phone_id': 'personal_phone_id_1',
            'user_id': 'taxi_user_id_1',
        }


@pytest.mark.pgsql('cargo_orders', files=['order_uncommited.sql'])
async def test_basic(taxi_cargo_orders, mockserver, fetch_order, load_json):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def claims_full(request):
        return load_json('cargo-claims/default.json')

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def intapi_orders_commit(request):
        return {'orderid': 'taxi-order', 'status': 'searching'}

    response = await taxi_cargo_orders.post(
        '/v1/order/commit', json=commit_request(),
    )
    assert response.status_code == 200

    assert claims_full.times_called == 1
    assert intapi_orders_commit.times_called == 1

    assert intapi_orders_commit.next_call()['request'].json == {
        'userid': 'taxi_user_id_1',
        'orderid': 'taxi-order',
        'sourceid': 'cargo',
    }

    response_body = response.json()
    assert response_body == {
        'order_id': ORDER_ID,
        'provider_order_id': 'taxi-order',
        'revision': 2,
        'waybill_ref': 'waybill-ref',
    }

    order_doc = fetch_order(response_body['order_id'])
    assert order_doc.waybill_ref == 'waybill-ref'
    assert order_doc.provider_order_id == 'taxi-order'
    assert order_doc.commit_state == 'done'
    assert order_doc.revision == 2


@pytest.mark.pgsql('cargo_orders', files=['order_uncommited.sql'])
async def test_cargo_c2c(
        taxi_cargo_orders, mockserver, fetch_order, load_json,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def claims_full(request):
        response = load_json('cargo-claims/default.json')
        response.pop('corp_client_id')
        response['yandex_uid'] = 'some_yandex_uid'
        response['c2c_data'] = {
            'payment_method_id': 'corp-123',
            'payment_type': 'corp',
            'cargo_c2c_order_id': 'cargo_c2c_order_id_1',
        }
        return response

    @mockserver.json_handler('/cargo-c2c/v1/intiator-client-order')
    def mosck_c2c(request):
        assert request.json == {'cargo_c2c_order_id': 'cargo_c2c_order_id_1'}
        return {'user_id': 'some_user_id', 'user_agent': 'some_user_agent'}

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def intapi_orders_commit(request):
        return {'orderid': 'taxi-order', 'status': 'searching'}

    response = await taxi_cargo_orders.post(
        '/v1/order/commit', json=commit_request(),
    )
    assert response.status_code == 200

    assert claims_full.times_called == 1
    assert intapi_orders_commit.times_called == 1
    assert mosck_c2c.times_called == 1

    int_api_request = intapi_orders_commit.next_call()['request']
    assert int_api_request.json == {
        'userid': 'taxi_user_id_1',
        'orderid': 'taxi-order',
        'sourceid': 'cargo_c2c',
    }
    assert int_api_request.headers['User-Agent'] == 'some_user_agent'


@pytest.mark.pgsql('cargo_orders', files=['order_uncommited.sql'])
async def test_cargo_c2c_phoenix(
        taxi_cargo_orders, mockserver, fetch_order, load_json,
):
    card_id = 'card-xxx'
    yandex_uid = 'some_yandex_uid'
    payment_method_id = (
        'cargocorp:corpidxxx:card:' + yandex_uid + ':' + card_id
    )

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def claims_full(request):
        response = load_json('cargo-claims/default.json')
        response['yandex_uid'] = yandex_uid
        response['origin_info'] = {'origin': 'yandexgo'}
        response['features'] = [{'id': 'phoenix_claim'}]
        response['c2c_data'] = {
            'payment_method_id': payment_method_id,
            'payment_type': 'card',
            'cargo_c2c_order_id': 'cargo_c2c_order_id_1',
        }
        response['pricing_payment_methods'] = {
            'card': {
                'cardstorage_id': card_id,
                'owner_yandex_uid': yandex_uid,
            },
        }
        return response

    @mockserver.json_handler('/cargo-c2c/v1/intiator-client-order')
    def mosck_c2c(request):
        assert request.json == {'cargo_c2c_order_id': 'cargo_c2c_order_id_1'}
        return {'user_id': 'some_user_id', 'user_agent': 'some_user_agent'}

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def intapi_orders_commit(request):
        return {'orderid': 'taxi-order', 'status': 'searching'}

    response = await taxi_cargo_orders.post(
        '/v1/order/commit', json=commit_request(),
    )
    assert response.status_code == 200

    assert claims_full.times_called == 1
    assert intapi_orders_commit.times_called == 1
    assert mosck_c2c.times_called == 1

    int_api_request = intapi_orders_commit.next_call()['request']
    assert int_api_request.json == {
        'userid': 'taxi_user_id_1',
        'orderid': 'taxi-order',
        'sourceid': 'cargo_c2c',
    }
    assert int_api_request.headers['User-Agent'] == 'some_user_agent'


@pytest.mark.parametrize(
    ('intapi_code', 'expected_code', 'metric_name'),
    (
        (404, 410, 'response-404'),
        (406, 400, 'response-406'),
        (410, 400, 'response-410'),
        (429, 429, 'response-429'),
        (500, 500, 'unexpected-exception'),
    ),
)
@pytest.mark.pgsql('cargo_orders', files=['order_uncommited.sql'])
async def test_error_metrics(
        taxi_cargo_orders,
        taxi_cargo_orders_monitor,
        mockserver,
        load_json,
        intapi_code: int,
        expected_code: int,
        metric_name: str,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('cargo-claims/default.json')

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def _intapi_orders_commit(request):
        return mockserver.make_response(
            status=intapi_code, json={'code': 'test_error'},
        )

    await taxi_cargo_orders.tests_control(reset_metrics=True)
    response = await taxi_cargo_orders.post(
        '/v1/order/commit', json=commit_request(),
    )
    assert response.status_code == expected_code
    statistics = await taxi_cargo_orders_monitor.get_metric(
        'cargo-orders-client',
    )
    assert statistics['int-authproxy']['orders-commit'][metric_name] == 1


@pytest.mark.pgsql('cargo_orders', files=['order_uncommited.sql'])
async def test_response_200_metric(
        taxi_cargo_orders, taxi_cargo_orders_monitor, mockserver, load_json,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('cargo-claims/default.json')

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def _intapi_orders_commit(request):
        return mockserver.make_response(
            status=200, json={'orderid': 'some_id', 'status': 'created'},
        )

    await taxi_cargo_orders.tests_control(reset_metrics=True)
    await taxi_cargo_orders.post('/v1/order/commit', json=commit_request())
    statistics = await taxi_cargo_orders_monitor.get_metric(
        'cargo-orders-client',
    )
    assert statistics['int-authproxy']['orders-commit']['response-200'] == 1


@pytest.mark.parametrize(
    ('code', 'reason'), (('UNKNOWN_COMMIT_ERROR', 'COMMIT_ERROR'),),
)
@pytest.mark.pgsql('cargo_orders', files=['order_uncommited.sql'])
async def test_reason(
        taxi_cargo_orders,
        mockserver,
        load_json,
        fetch_taxi_order_error,
        code: str,
        reason: str,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('cargo-claims/default.json')

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def _intapi_orders_commit(request):
        return mockserver.make_response(status=406, json={'code': code})

    response = await taxi_cargo_orders.post(
        '/v1/order/commit', json=commit_request(),
    )
    assert response.status_code == 400

    error = fetch_taxi_order_error()
    assert error['reason'] == reason
    assert error['message'] == code


@pytest.mark.pgsql('cargo_orders', files=['order_uncommited.sql'])
async def test_429_commit(taxi_cargo_orders, mockserver, load_json):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('cargo-claims/default.json')

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def _intapi_orders_commit(request):
        return mockserver.make_response(
            status=429, json={'code': 'test_error'},
        )

    response = await taxi_cargo_orders.post(
        '/v1/order/commit', json=commit_request(),
    )
    assert response.status_code == 429


@pytest.mark.pgsql('cargo_orders', files=['order_uncommited.sql'])
async def test_403_error(
        taxi_cargo_orders, mockserver, load_json, fetch_taxi_order_error,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('cargo-claims/default.json')

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def _intapi_orders_commit(request):
        return mockserver.make_response(status=403, json={})

    response = await taxi_cargo_orders.post(
        '/v1/order/commit', json=commit_request(),
    )
    assert response.status_code == 403

    error = fetch_taxi_order_error()
    assert error['reason'] == 'COMMIT_ANTIFRAUD'
    assert error['message'] == 'UNKNOWN_INT_API_ERROR'


@pytest.mark.config(
    CARGO_ORDERS_ORDER_COMMIT_SETTINGS={
        'commit_500_restriction': {'enabled': True, 'count': 2},
    },
)
@pytest.mark.pgsql('cargo_orders', files=['order_uncommited.sql'])
async def test_500_error_restriction(
        taxi_cargo_orders, mockserver, load_json, fetch_taxi_order_error,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('cargo-claims/default.json')

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def _intapi_orders_commit(request):
        return mockserver.make_response(status=500, json={})

    for _x in range(0, 2):
        response = await taxi_cargo_orders.post(
            '/v1/order/commit', json=commit_request(),
        )
        assert response.status_code == 500

    response = await taxi_cargo_orders.post(
        '/v1/order/commit', json=commit_request(),
    )
    assert response.status_code == 406


@pytest.mark.pgsql('cargo_orders', files=['order_uncommited.sql'])
async def test_corp_error(taxi_cargo_orders, mockserver, load_json):
    # Return 410 and retry draft creation from dispatch

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return load_json('cargo-claims/default.json')

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def _intapi_orders_commit(request):
        return mockserver.make_response(
            status=406, json={'error': {'code': 'CORP_SERVICE_ERROR'}},
        )

    response = await taxi_cargo_orders.post(
        '/v1/order/commit', json=commit_request(),
    )
    assert response.status_code == 410

    # Check that order was deleted
    response = await taxi_cargo_orders.post(
        '/v1/orders/bulk-info',
        json={'cargo_orders_ids': ['9db1622e-582d-4091-b6fc-4cb2ffdc12c0']},
    )
    assert response.json() == {'orders': []}


@pytest.mark.pgsql('cargo_orders', files=['order_uncommited.sql'])
async def test_fetch_all_claims(
        taxi_cargo_orders, mockserver, fetch_order, load_json,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def claims_full(request):
        full_response = load_json('cargo-claims/default.json')
        full_response['id'] = request.query['claim_id']
        return full_response

    @mockserver.json_handler('/int-authproxy/v1/orders/commit')
    def intapi_orders_commit(request):
        return {'orderid': 'taxi-order', 'status': 'searching'}

    response = await taxi_cargo_orders.post(
        '/v1/order/commit', json=batch_commit_request(),
    )
    assert response.status_code == 200

    assert claims_full.times_called == 2
    assert intapi_orders_commit.times_called == 1

    assert intapi_orders_commit.next_call()['request'].json == {
        'userid': 'taxi_user_id_1',
        'orderid': 'taxi-order',
        'sourceid': 'cargo',
    }

    response_body = response.json()
    assert response_body == {
        'order_id': ORDER_ID,
        'provider_order_id': 'taxi-order',
        'revision': 2,
        'waybill_ref': 'waybill-ref',
    }
