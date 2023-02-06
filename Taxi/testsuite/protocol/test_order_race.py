import pytest


def make_order(taxi_protocol, request):
    response = taxi_protocol.post('3.0/order', request)
    assert response.status_code == 200
    response_body = response.json()
    return response_body


def make_order_expect_fail(taxi_protocol, request, expected_error_code):
    response = taxi_protocol.post('3.0/order', request)
    assert response.status_code == expected_error_code


def make_order_draft_commit(taxi_protocol, draft_request):
    draft_response = taxi_protocol.post('3.0/orderdraft', draft_request)
    assert draft_response.status_code == 200
    order_id = draft_response.json()['orderid']

    commit_request = {'id': draft_request['id'], 'orderid': order_id}

    commit_response = taxi_protocol.post('3.0/ordercommit', commit_request)
    assert commit_response.status_code == 200

    return commit_response.json()


@pytest.mark.parametrize(
    'testpoint_name',
    [
        'ordercommit::on_set_state_pending',
        'ordercommit::on_set_state_reserved',
        'ordercommit::on_set_state_done',
    ],
)
@pytest.mark.parametrize('create_order', [make_order, make_order_draft_commit])
def test_order_race(
        taxi_protocol, testpoint, load_json, db, testpoint_name, create_order,
):
    @testpoint(testpoint_name)
    def update_state_to_done(data):
        query = {'_id': data['order_id'], '_shard_id': 0}
        update = {'$set': {'commit_state': 'done'}}
        db.orders.find_and_modify(query, update, False)

    request = load_json('basic_request.json')
    create_order(taxi_protocol, request)
    assert update_state_to_done.times_called == 1
    assert db.order_proc.find_one({'_id': ''}) is None


def test_double_order_creation_fail_on_device_limit(taxi_protocol, load_json):
    request = load_json('basic_request.json')
    make_order(taxi_protocol, request)
    make_order_expect_fail(taxi_protocol, request, 429)


@pytest.mark.config(MAX_UNFINISHED_ORDERS=1, MAX_CONCURRENT_ORDERS=2)
def test_double_order_creation_fail_on_phone_limit(taxi_protocol, load_json):
    request = load_json('basic_request.json')
    make_order(taxi_protocol, request)
    make_order_expect_fail(taxi_protocol, request, 429)


@pytest.mark.config(MAX_CONCURRENT_ORDERS=2)
def test_double_order_creation_ok_if_allowed(taxi_protocol, load_json):
    request = load_json('basic_request.json')
    make_order(taxi_protocol, request)
    make_order(taxi_protocol, request)
    make_order_expect_fail(taxi_protocol, request, 429)
