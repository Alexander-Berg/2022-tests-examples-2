import copy
import hashlib
import hmac
import json

import pytest

CLIENT_SECRET = 'some-client-secret'
REQUEST_DATA = {
    'event_type': 'orders.notification',
    'event_id': 'c4d2261e-2779-4eb6-beb0-cb41235c751e',
    'event_time': 1427343990,
    'meta': {
        'resource_id': '153dd7f1-339d-4619-940c-418943c14636',
        'status': 'pos',
        'user_id': '89dd9741-66b5-4bb4-b216-a813f3b21b4f',
    },
    'resource_href': (
        'https://api.uber.com/v2/eats/order/'
        '153dd7f1-339d-4619-940c-418943c14636'
    ),
}


async def test_event_api_validation(taxi_grocery_uber_gw, mockserver):
    """ Check X-Uber-Signature validation"""

    data = json.dumps(REQUEST_DATA)
    signature = hmac.new(
        CLIENT_SECRET.encode(), data.encode(), hashlib.sha256,
    ).hexdigest()

    @mockserver.json_handler('/processing/v1/grocery/uber_events/create-event')
    def _create_event():
        return {'event_id': 'some-id'}

    response = await taxi_grocery_uber_gw.post(
        'lavka/v1/uber-gw/v1/event',
        data=data,
        headers={
            'X-Uber-Signature': signature,
            'content-type': 'application/json',
        },
    )
    assert response.status_code == 200
    assert response.text == str()  # check for empty body


@pytest.mark.parametrize('has_event_id', [True, False])
async def test_event_api_200(taxi_grocery_uber_gw, mockserver, has_event_id):
    """ Check that webhook data is being proxied to processing
        if no event_id in request, it's being generated """

    local_request_data = copy.deepcopy(REQUEST_DATA)
    if not has_event_id:
        local_request_data.pop('event_id')
    data = json.dumps(local_request_data)
    signature = hmac.new(
        CLIENT_SECRET.encode(), data.encode(), hashlib.sha256,
    ).hexdigest()

    @mockserver.json_handler('/processing/v1/grocery/uber_events/create-event')
    def _create_event(request):
        print(request.json)
        if has_event_id:
            assert request.query['item_id'] == local_request_data['event_id']
            assert request.headers[
                'X-Idempotency-Token'
            ] == 'uber-gw-{}'.format(local_request_data['event_id'])
        else:
            assert request.query['item_id']
            generated_event_id = request.query['item_id']
            assert request.headers[
                'X-Idempotency-Token'
            ] == 'uber-gw-{}'.format(generated_event_id)
        assert request.json['trait'] == 'created'
        request.json.pop('trait')
        assert request.json == local_request_data
        return {'event_id': 'some-id'}

    response = await taxi_grocery_uber_gw.post(
        'lavka/v1/uber-gw/v1/event',
        data=data,
        headers={
            'X-Uber-Signature': signature,
            'content-type': 'application/json',
        },
    )
    assert response.status_code == 200
    assert response.text == str()  # check for empty body


async def test_event_api_401(taxi_grocery_uber_gw):
    """ Check X-Uber-Signature validation failure
    lavka/v1/uber-gw/v1/event should return 401 """

    response = await taxi_grocery_uber_gw.post(
        'lavka/v1/uber-gw/v1/event',
        data=json.dumps(REQUEST_DATA),
        headers={
            'X-Uber-Signature': 'random value',
            'content-type': 'application/json',
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        'code': 'SIGNATURE_VERIFICATION_FAILURE',
        'message': 'X-Uber-Signature validation failure',
    }


@pytest.mark.parametrize('procaas_error', [400, 409, 500])
async def test_event_api_500(taxi_grocery_uber_gw, mockserver, procaas_error):
    """ Check that no error processing is implemented so far """

    data = json.dumps(REQUEST_DATA)
    signature = hmac.new(
        CLIENT_SECRET.encode(), data.encode(), hashlib.sha256,
    ).hexdigest()

    @mockserver.json_handler('/processing/v1/grocery/uber_events/create-event')
    def _create_event():
        return mockserver.make_response(status=procaas_error)

    response = await taxi_grocery_uber_gw.post(
        'lavka/v1/uber-gw/v1/event',
        data=data,
        headers={
            'X-Uber-Signature': signature,
            'content-type': 'application/json',
        },
    )

    assert response.status_code == 500
