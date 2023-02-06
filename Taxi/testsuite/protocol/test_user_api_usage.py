import json

import bson
import pytest


@pytest.fixture(autouse=True)
def user_api_service_autouse(mockserver, config):
    config.set_values(
        dict(
            USER_API_USE_USER_PHONES_CREATION=True,
            USER_API_USE_USER_PHONES_BULK_CREATION=True,
            USER_API_CLIENT_USER_PHONES_TIMEOUT_MS=2000,
            PROTOCOL_USERS_SET_AUTHORIZED_WITH_USER_API=True,
        ),
    )


@pytest.fixture(scope='function', autouse=True)
def feedback_service(mockserver):
    @mockserver.json_handler('/feedback/1.0/wanted/retrieve')
    def mock_service(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert sorted(data.keys()) == ['id', 'newer_than', 'phone_id']
        return {'orders': []}


def test_order(
        taxi_protocol,
        mockserver,
        load_json,
        db,
        mock_user_api,
        pricing_data_preparer,
):
    def create_draft(req_file=None, **http_kwargs):
        if req_file is None:
            req_file = 'basic_request.json'
        request = load_json(req_file)
        draft_resp = taxi_protocol.post(
            '3.0/orderdraft', request, **http_kwargs,
        )
        assert draft_resp.status_code == 200
        return draft_resp.json()['orderid']

    def commit_order(order_id, **http_kwargs):
        request = load_json('basic_request.json')
        commit_request = {
            'id': request['id'],
            'orderid': order_id,
            'check_unfinished_commit': False,
        }

        return taxi_protocol.post(
            '3.0/ordercommit', commit_request, **http_kwargs,
        )

    def create_order(req_file=None, **http_kwargs):
        order_id = create_draft(req_file, **http_kwargs)
        commit_resp = commit_order(order_id, **http_kwargs)
        return order_id, commit_resp

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.2,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}

    @mockserver.json_handler('/user-api/users/set_authorized')
    def mock_user_api_set_authorized(request):
        db.users.update(
            {'_id': request.json['id']},
            {
                '$set': {
                    'authorized': request.json['authorized'],
                    'phone_id': bson.ObjectId(request.json['phone_id']),
                },
                '$unset': {'confirmation': True},
            },
        )

    response = create_order('basic_request.json', x_real_ip='my-ip-address')
    assert mock_user_api_set_authorized.times_called == 1
    assert response[-1].status_code == 200
    assert mock_user_api.user_phones_times_called == 1
