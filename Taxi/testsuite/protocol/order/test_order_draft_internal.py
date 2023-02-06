import datetime

import pytz


_ORDER_DRAFT_INTERNAL_PATH = 'internal/orderdraft'


def get_proc_collection(db, order_id):
    proc = db.order_proc.find_one(
        {'_id': order_id},
        {'order._id': 0, 'order.created': 0, 'order.status_updated': 0},
    )
    return proc


def orderdraft_internal(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order,
        bearer=None,
        cookie=None,
        headers={},
        x_real_ip='my-ip-address',
):
    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        geo_docs = load_json(order + '/yamaps.json')
        for doc in geo_docs:
            if request.query_string.decode().find(doc['url']) != -1:
                return doc['response']

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_pickup_zones(request):
        return {}

    @mockserver.json_handler('/chat/1.0/chat')
    def mock_chat(request):
        return {'id': 'some_new_chat_id'}

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        assert (
            request.query_string.decode()
            == (
                'method=oauth&userip=&format=json&'
                'dbfields=subscription.suid.669&'
                'aliases=1%2C10%2C16&'
                'oauth_token=test_token&getphones=bound&'
                'get_login_id=yes&'
                'phone_attributes=102%2C107'
            )
            or request.query_string.decode()
            == (
                'method=sessionid&userip=my-ip-address&host=yandex.ru&'
                'format=json&dbfields=subscription.suid.669&sessionid=5&'
                'getphones=bound&get_login_id=yes&phone_attributes=102%2C107'
            )
        )
        return {
            'uid': {'value': '4003514353'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'phones': [
                {'attributes': {'102': '+71111111111'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    if bearer is not None:
        response = taxi_protocol.post(
            _ORDER_DRAFT_INTERNAL_PATH,
            request,
            bearer=bearer,
            headers=headers,
            x_real_ip=x_real_ip,
        )
    else:
        headers['Cookie'] = cookie
        response = taxi_protocol.post(
            _ORDER_DRAFT_INTERNAL_PATH,
            request,
            bearer=None,
            headers=headers,
            x_real_ip=x_real_ip,
        )
    assert response.status_code == 200
    return response.json()


def check_response(data, load_json, db, request, order, due=None):
    order_id = data['orderid']

    assert isinstance(order_id, str)
    actual_proc = get_proc_collection(db, order_id)
    expected_order = load_json(order + '/expected_order.json')
    if 'due' in request:
        due = due.astimezone(pytz.utc)
        expected_order['request']['due'] = datetime.datetime(
            due.year, due.month, due.day, due.hour, due.minute, due.second,
        )
        expected_urgency = expected_order['statistics'].pop('urgency')
        actual_urgency = actual_proc['order']['statistics'].pop('urgency')
        assert abs(actual_urgency - expected_urgency) <= 60

    if 'source_geoareas' in expected_order['request']:
        expected_order['request']['source_geoareas'] = set(
            expected_order['request']['source_geoareas'],
        )
        actual_proc['order']['request']['source_geoareas'] = set(
            actual_proc['order']['request']['source_geoareas'],
        )

    assert actual_proc['commit_state'] == expected_order.pop('commit_state')
    assert actual_proc['payment_tech'] == expected_order.pop('payment_tech')
    assert actual_proc['order'] == expected_order


def test_order_draft_internal(taxi_protocol, mockserver, load_json, db):
    order_path = 'order_1'
    request = load_json(order_path + '/request.json')
    response = orderdraft_internal(
        taxi_protocol,
        mockserver,
        load_json,
        request,
        order_path,
        bearer='test_token',
    )
    check_response(response, load_json, db, request, order_path)
