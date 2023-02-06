import pytest

from order_core_exp_parametrize import CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
from protocol.yauber import yauber


_ORDER_DRAFT_PATH = '3.0/orderdraft'


@pytest.fixture(scope='function', autouse=True)
def order_service(mockserver, load_json):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}


def get_order_collection(db, order_id):
    proc = db.order_proc.find_one(
        {'_id': order_id},
        {
            '_id': 0,
            'created': 0,
            'status_updated': 0,
            'updated': 0,
            'order.created': 0,
            'order.status_updated': 0,
        },
    )
    order = proc['order']
    order['user_phone_id'] = {'$oid': str(order['user_phone_id'])}
    return order


def orderdraft(taxi_protocol, mockserver, load_json, request, bearer):
    @mockserver.json_handler('/chat/1.0/chat')
    def mock_chat(request):
        return {'id': 'some_new_chat_id'}

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        query = set(request.query_string.decode().split('&'))
        assert (
            query
            == {
                'method=oauth',
                'userip=',
                'format=json',
                'dbfields=subscription.suid.669',
                'aliases=1%2C10%2C16',
                'oauth_token=test_token',
                'getphones=bound',
                'get_login_id=yes',
                'phone_attributes=102%2C107%2C4',
            }
            or query
            == {
                'method=sessionid',
                'userip=',
                'host=yandex.ru',
                'format=json',
                'dbfields=subscription.suid.669',
                'sessionid=5',
                'getphones=bound',
                'get_login_id=yes',
                'phone_attributes=102%2C107',
            }
        )
        return {
            'uid': {'value': '4003514353'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:yauber_request'},
            'phones': [
                {'attributes': {'102': '+71111111111'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    response = taxi_protocol.post(
        _ORDER_DRAFT_PATH, request, bearer=bearer, headers=yauber.headers,
    )
    assert response.status_code == 200
    return response.json()


@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_yauber(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        load,
        load_json,
        db,
):
    request = load_json('request.json')
    response = orderdraft(
        taxi_protocol, mockserver, load, request, bearer='test_token',
    )
    response_id = response['orderid']
    order = get_order_collection(db, response_id)
    assert order['source'] == 'yauber'
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled
